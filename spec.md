# Spec: Lab 10 — Alignment Experiment (DPO)

**Intent:** `docs/intent/lab10-dpo.md`  
**Source lab:** `Lab_10_Open_Ended_Lab_Alignment_DPO.pdf`

## Assumptions (correct before approval)

1. Execution is via **Google Colab CLI** against a GPU runtime; local CPU-only training is out of scope.
2. Training uses a **subset** of `trl-lib/ultrafeedback_binarized` (not the full dataset) so both DPO runs finish in a Colab session.
3. Second beta is **0.5** (vs required baseline **0.1**) to contrast stronger vs weaker deviation from the reference policy.
4. Evaluation is **manual 1–5 scoring** on four criteria (no LLM-as-judge).
5. Deliverable is a **Colab notebook + `REPORT.md`** with tables and pasted evidence (not a graded LMS upload automation).
6. Agent owns prompt text, rubric, subset size, and training hyperparameters unless you override them in review.

→ Approve or correct these; they freeze into the experiment.

---

## Objective

Run an open-ended DPO alignment experiment on `Qwen/Qwen2.5-0.5B` using `trl-lib/ultrafeedback_binarized`, then decide from **your own evidence** whether alignment improved the model.

**User:** BS IT student submitting Lab 10 (10 marks).

**Success:** All minimum lab requirements completed; `REPORT.md` answers the six final-analysis questions with citations to logged outputs.

### Acceptance criteria (lab-mapped)

| # | Criterion | Evidence artifact |
|---|-----------|-------------------|
| 1 | Base model tested before alignment | `artifacts/base_outputs.json` |
| 2 | Preference examples inspected | `artifacts/preference_inspection.md` |
| 3 | DPO alignment run (β=0.1) | `artifacts/dpo_beta_0.1/` (logs + adapter/checkpoint) |
| 4 | Aligned model tested on **same** prompts | `artifacts/dpo_0.1_outputs.json` |
| 5 | Base vs aligned comparison scored | `artifacts/comparison_table.md` |
| 6 | Second β experiment | `artifacts/dpo_beta_0.5/` + `artifacts/dpo_0.5_outputs.json` |
| 7 | Conclusion supported by results | `REPORT.md` § Final Analysis |

---

## Tech Stack

| Piece | Choice |
|-------|--------|
| Runtime | Google Colab + GPU (T4 or better) via Colab CLI |
| Base model | `Qwen/Qwen2.5-0.5B` |
| Dataset | `trl-lib/ultrafeedback_binarized` |
| Alignment | Hugging Face `trl` DPOTrainer |
| Training memory | LoRA / PEFT (full FT not required for 0.5B but LoRA keeps Colab stable) |
| Python deps | `transformers`, `trl`, `peft`, `datasets`, `accelerate`, `torch` |

---

## Experiment Design (agent-owned defaults)

### Prompts (≥5, ≥3 task types)

| ID | Task type | Prompt |
|----|-----------|--------|
| P1 | Explanation | Explain how a transformer attention layer decides which tokens matter, in plain language for a first-year CS student. |
| P2 | Advice | I have a midterm in three days and keep procrastinating. Give a concrete day-by-day plan I can follow. |
| P3 | Summarisation | Summarise the idea of overfitting in machine learning in exactly three short bullet points. |
| P4 | Professional writing | Write a short, polite email declining a Friday meeting because of a prior exam, and propose two alternative times. |
| P5 | Reasoning | A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost? Show the steps. |
| P6 | Question answering | What is the capital of Pakistan, and briefly why was it chosen over Karachi? |

### Evaluation rubric (1–5 each)

| Criterion | 1 | 5 |
|-----------|---|---|
| Helpfulness | Unusable / wrong | Directly solves the ask |
| Relevance | Off-topic | Stays on instruction |
| Clarity | Confusing | Easy to follow |
| Instruction following | Ignores constraints | Meets format/constraints |

**Winner rule:** Sum of four scores. Higher total wins; tie if equal. Record Base / DPO-0.1 / DPO-0.5 / Tie per prompt as applicable.

### Preference inspection

- Sample **5** train-split examples (fixed seed `42`).
- For each: prompt, chosen, rejected, and 2–4 sentences on why chosen looks preferred; note any repeated patterns.

### DPO configuration

| Setting | Experiment A | Experiment B |
|---------|--------------|--------------|
| beta | `0.1` | `0.5` |
| Purpose | Required baseline | Stronger KL / stay closer to reference |
| Dataset subset | First **1000** preference pairs (seed 42) | Same subset |
| Max steps | **200** (or 1 epoch on subset, whichever first) | Same |
| LoRA | r=16, alpha=32, dropout=0.05 | Same |
| Learning rate | `5e-5` | Same |
| Batch / grad accum | Fit GPU (target effective batch ≥4) | Same |
| Max seq length | 512 | Same |
| Seed | 42 | 42 |

Generation for eval: `max_new_tokens=256`, `temperature=0.7`, `do_sample=True`, same decoding for all models.

---

## Commands

```bash
# Auth / runtime (Colab CLI — exact binary confirmed at setup)
colab login
colab runtime create --gpu   # or project-equivalent

# Upload & execute notebook
colab upload lab10_dpo.ipynb
colab execute lab10_dpo.ipynb --timeout 10800

# Pull artifacts back to workspace
colab download artifacts/ ./artifacts/

# Local report assembly (after artifacts exist)
# (manual / agent write) REPORT.md
```

Notebook-internal install cell:

```python
%pip install -q transformers trl peft datasets accelerate bitsandbytes
```

---

## Project Structure

```
AssignmentLL2/
├── Lab_10_Open_Ended_Lab_Alignment_DPO.pdf
├── docs/intent/lab10-dpo.md      # confirmed intent
├── spec.md                      # this file
├── lab10_dpo.ipynb              # Colab experiment notebook
├── artifacts/                   # pulled from Colab
│   ├── preference_inspection.md
│   ├── base_outputs.json
│   ├── dpo_0.1_outputs.json
│   ├── dpo_0.5_outputs.json
│   ├── comparison_table.md
│   ├── dpo_beta_0.1/            # logs + adapter
│   └── dpo_beta_0.5/
└── REPORT.md                    # evidence-backed lab report
```

---

## Code Style

```python
# Clear section banners; fixed seeds; write every result to artifacts/
SEED = 42
PROMPTS = [
    {"id": "P1", "type": "explanation", "text": "..."},
    # ...
]

def generate(model, tokenizer, prompt: str) -> str:
    """Same decoding kwargs for base and all DPO checkpoints."""
    ...

def score_row(prompt_id: str, base: str, dpo: str) -> dict:
    """Returns per-criterion ints + winner label; filled during eval pass."""
    ...
```

- Prefer explicit paths under `/content/artifacts` in Colab, mirrored to `./artifacts` locally.
- Do not hardcode secrets; use Colab auth only.
- Log train loss / step to files under each `dpo_beta_*` folder.

---

## Testing Strategy

This lab is empirical, not unit-tested. Verification gates:

1. **Smoke:** Base model generates non-empty text for P1 before any DPO.
2. **Data:** Preference inspection file contains 5 examples with chosen ≠ rejected.
3. **Train:** Both DPO runs complete without OOM; loss logged for ≥1 step.
4. **Parity:** Eval prompt IDs and text identical across base / β=0.1 / β=0.5 JSON files.
5. **Report:** All six final-analysis questions answered with references to artifact paths or quoted outputs.

No coverage target. Fail the lab run if any gate above fails.

---

## Boundaries

**Always**
- Use the mandated model and dataset.
- Eval with the **same** six prompts and decoding settings.
- Keep training logs and configuration in artifacts.
- State whether DPO helped **from evidence**, not assumption.

**Ask first**
- Changing second beta away from 0.5.
- Increasing subset above 1000 or max steps above 200 (cost/time).
- Switching from LoRA to full fine-tune.
- Dropping any of P1–P6.

**Never**
- Claim aligned model is better without comparison scores.
- Copy the lab-manual example prompt as one of the five required originals.
- Commit Hugging Face / Google tokens.
- Quietly skip the second beta run.

---

## Success Criteria

- [ ] `lab10_dpo.ipynb` runs end-to-end on Colab GPU via CLI
- [ ] Artifacts for preference inspection, base, DPO×2, and comparison exist
- [ ] `REPORT.md` includes: design, preference analysis, training config/logs summary, before/after table, beta comparison, six final answers
- [ ] Marking rubric coverage: design (2), preference (2), DPO success (2), base vs aligned (2), beta + conclusion (2)

---

## Open Questions

Resolved on approval (2026-11-18):

1. Colab CLI already authenticated — no interactive login assumed at start.
2. Pull **logs + JSON outputs only** (not full adapters) unless training debug needs weights.
3. Keep prompts **P1–P6** as written.
