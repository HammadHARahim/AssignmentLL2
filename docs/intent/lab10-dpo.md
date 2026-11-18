# Lab 10 — Alignment Experiment (DPO)

## Statement of Intent

- **Outcome:** Full Lab 10 run on Colab CLI + evidence-backed report
- **User:** BS IT student (Lab 10 submission)
- **Why now:** Execute the lab end-to-end, not design-only
- **Success:** Base → preference inspect → DPO (β=0.1 + second β) → same-prompt compare; conclusion supported by experimental results
- **Constraint:** Qwen2.5-0.5B, `trl-lib/ultrafeedback_binarized`, DPO, Colab GPU via CLI
- **Out of scope:** Other models/datasets, non-DPO methods, extra polish beyond lab deliverables

## Fixed lab resources

| Resource | Value |
|----------|--------|
| Base model | `Qwen/Qwen2.5-0.5B` |
| Preference dataset | `trl-lib/ultrafeedback_binarized` |
| Alignment method | Direct Preference Optimization (DPO) |
| Environment | Google Colab + GPU (via Colab CLI) |

## Minimum requirements (must complete)

1. Test the base model before alignment
2. Inspect chosen and rejected responses from the preference dataset
3. Align the model using DPO
4. Test the aligned model using the same prompts
5. Compare the base and aligned responses
6. Experiment with at least one additional beta value
7. Support the conclusion with evidence from the runs

## Agent-owned decisions (handed off)

Prompts (≥5, ≥3 task types), evaluation rubric, preference-sample count, second beta value, and training/runtime knobs needed to finish within lab constraints — chosen by the agent unless the student overrides.

## Confirmed

Explicit yes from student, 2026-11-18.
