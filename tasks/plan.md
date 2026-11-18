# Implementation Plan: Lab 10 DPO Alignment

## Overview

Build and execute one Colab notebook that runs preference inspection, base-model eval, two DPO runs (β=0.1 and β=0.5), same-prompt comparison, then assemble `REPORT.md` from pulled artifacts (logs + JSON only). Spec: `spec.md`. Intent: `docs/intent/lab10-dpo.md`.

## Architecture Decisions

- **Single notebook** (`lab10_dpo.ipynb`) with numbered cells matching lab phases — easiest for Colab CLI execute + student hand-in.
- **LoRA + subset (1000 pairs, 200 steps)** — finishes on Colab GPU without full FT / full dataset.
- **Artifacts-first I/O** — every phase writes under `/content/artifacts`; pull logs + JSON only (no full adapters unless debug).
- **Shared `generate()`** — identical decoding for base / both DPO adapters so comparison is fair.
- **Manual rubric in report** — scores filled when writing `REPORT.md` from generated texts (not auto-scored in-notebook).

## Dependency graph

```
Colab CLI smoke
    → Notebook scaffold + deps + prompts
        → Preference inspection
            → Base eval
                → DPO β=0.1 → eval 0.1
                → DPO β=0.5 → eval 0.5   (sequential after 0.1 to avoid GPU contention)
                    → Pull artifacts
                        → REPORT.md
```

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Colab CLI missing / auth fails | High | Verify CLI + runtime before writing notebook; fall back to upload+manual run only if CLI broken |
| OOM on T4 | High | LoRA, max_length 512, small batch + grad accum; cut max_steps if needed |
| DPO train too slow | Med | Cap 200 steps; same subset both betas |
| HF download rate limits | Med | Cache model once; reuse for both runs |
| “Aligned always better” bias | Med | Score blindly from artifacts; allow Base wins in report |

## Parallelization

None for training (one GPU). Report writing can start drafting structure while last train runs, but final scores wait for all JSON outputs.

## Open Questions

None blocking — OQ1–3 resolved in `spec.md` on approval.
