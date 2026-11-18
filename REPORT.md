# Lab 10 Report — Alignment Experiment (DPO)

**Student environment:** Google Colab CLI · Tesla T4 · session `lab10dpo`  
**Base model:** `Qwen/Qwen2.5-0.5B`  
**Dataset:** `trl-lib/ultrafeedback_binarized`  
**Method:** Direct Preference Optimization (LoRA)  
**Artifacts:** `artifacts/` · Notebook/script: `lab10_dpo.ipynb`, `lab10_dpo.py`  
**Intent / spec:** `docs/intent/lab10-dpo.md`, `spec.md`

---

## 1. Experiment design and prompts

### Goal
Test whether DPO on UltraFeedback preferences improves `Qwen2.5-0.5B` on six hand-written prompts, and whether β=0.5 behaves differently from β=0.1.

### Prompts (6 prompts · 6 task types)

| ID | Type | Prompt |
|----|------|--------|
| P1 | Explanation | Explain how a transformer attention layer decides which tokens matter, in plain language for a first-year CS student. |
| P2 | Advice | I have a midterm in three days and keep procrastinating. Give a concrete day-by-day plan I can follow. |
| P3 | Summarisation | Summarise the idea of overfitting in machine learning in exactly three short bullet points. |
| P4 | Professional writing | Write a short, polite email declining a Friday meeting because of a prior exam, and propose two alternative times. |
| P5 | Reasoning | A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost? Show the steps. |
| P6 | Question answering | What is the capital of Pakistan, and briefly why was it chosen over Karachi? |

### Evaluation rubric
Each response scored 1–5 on **Helpfulness**, **Relevance**, **Clarity**, **Instruction following**. Winner = higher sum (max 20). Full table: `artifacts/comparison_table.md`.

### Training setup (both β runs)

| Setting | Value |
|---------|--------|
| Preference subset | 1000 pairs, seed 42 |
| Max steps | 200 |
| LoRA | r=16, α=32, dropout=0.05 · targets q/k/v/o |
| LR | 5e-5 · batch 1 · grad accum 4 |
| max_length | 512 |
| β | **0.1** (A) and **0.5** (B) |
| Decode (all models) | max_new_tokens=256, temperature=0.7, top_p=0.9 |

---

## 2. Preference-data analysis

Source: `artifacts/preference_inspection.md` (5 shuffled train examples, seed 42).

**What makes chosen better (observed):**
1. **Higher reward scores** when scores differ (e.g. Ex.1 chosen 8.5 vs rejected 7.0).
2. **More complete / structured answers** on technical asks (Ex.3 stationarity: chosen develops mean-reversion + methods; rejected stays shallower).
3. **Repeated pattern:** preferred replies tend to be longer, more specific, and closer to following multi-part instructions — not merely “nicer tone.”

**Caveat:** Some pairs have near-identical truncated text in the inspection dump (formatting/length limits); score gaps and fuller assistant turns still indicate the preference signal UltraFeedback encodes.

---

## 3. DPO training evidence

| Run | β | train_loss | runtime (s) | log path |
|-----|---|------------|-------------|----------|
| A | 0.1 | **0.667** | 310.2 | `artifacts/dpo_beta_0.1/` |
| B | 0.5 | **0.713** | 307.5 | `artifacts/dpo_beta_0.5/` |

Loss traces (`train_log.json`):
- β=0.1: first logged loss ≈ **0.693** → last ≈ **0.661** (mild decrease).
- β=0.5: first ≈ **0.727** → last ≈ **0.757** (no clear decrease; higher KL constraint / different optimum).

Both runs completed 200 steps without OOM on T4. Config mirrors are in each `config.json`.

---

## 4. Base vs aligned outputs (summary)

Raw text: `artifacts/base_outputs.json`, `dpo_0.1_outputs.json`, `dpo_0.5_outputs.json`.

| Prompt | Better model | One-line evidence |
|--------|--------------|-------------------|
| P1 | DPO 0.1 | Cleaner analogy; base repeats template junk |
| P2 | **Base** | Only base keeps a real 3-day plan |
| P3 | **Base** | DPO 0.1 emits `irebase`; none hit “exactly 3 bullets” well |
| P4 | DPO 0.1 | Clearer decline + alternatives |
| P5 | DPO 0.1 | Completes correct **$0.05** solution |
| P6 | DPO 0.5 | States **Islamabad**; base/0.1 say Karachi |

Win counts: Base **2** · DPO 0.1 **3** · DPO 0.5 **1**.  
Mean rubric sum: Base **~11.2** · DPO 0.1 **~10.8** · DPO 0.5 **~9.5**.

---

## 5. Beta comparison

Higher β (0.5) keeps the policy closer to the reference. In this short LoRA run:

- **β=0.1** changed behaviour most where it helped (P5 solved; P1 cleaner) but also **degraded** instruction following (P3 collapse, weaker P2).
- **β=0.5** was more cautious / mixed: fixed the Islamabad fact on P6, but **broke** the bat-and-ball algebra and stayed weak on structured advice/summary.
- Mean quality was **highest for the base** under our rubric; β=0.1 won more *individual* prompts but introduced sharp failure modes.

---

## 6. Final analysis (required six questions)

### 1. Did DPO improve the model overall?
**No — not overall under this rubric.** DPO β=0.1 won 3/6 prompts and produced the best single answer (P5), but mean score stayed at or below the base because of regressions on P2/P3. Evidence: win table and means in `artifacts/comparison_table.md`.

### 2. Which types of prompts improved the most?
**Reasoning (P5)** and, secondarily, **explanation (P1)** and **professional writing (P4)** under β=0.1.

### 3. Were there prompts where the base model performed better?
**Yes — P2 (advice) and P3 (summarisation).** Base alone kept a usable day-by-day plan; DPO 0.1 destroyed the summary into nonsense.

### 4. What characteristics did you notice in chosen preference responses?
Chosen replies tend to be **more complete, specific, and instruction-aligned**, often with **higher preference scores** when scores differ (see preference inspection).

### 5. How did changing beta affect the model?
β=0.1 → lower train loss, more aggressive preference fitting, bigger wins *and* bigger fails.  
β=0.5 → higher train loss, different error profile (better P6 fact, worse P5 math). Neither β dominated the base on average.

### 6. What do you think DPO actually changed?
With only 200 LoRA steps on a 0.5B model, DPO mainly **nudged surface style and occasional factual/reasoning paths** rather than reliably installing “helpful assistant” behaviour. It can amplify UltraFeedback patterns (verbosity, stepwise math) but also **destabilize** fragile instruction following — so improvement is **prompt-dependent**, not automatic.

---

## Deliverables checklist

| Deliverable | Location |
|-------------|----------|
| Experiment design + prompts | this report §1 |
| Base outputs | `artifacts/base_outputs.json` |
| Preference examples + analysis | `artifacts/preference_inspection.md` + §2 |
| DPO logs / config | `artifacts/dpo_beta_0.1/`, `dpo_beta_0.5/` |
| Aligned outputs | `artifacts/dpo_0.1_outputs.json`, `dpo_0.5_outputs.json` |
| Before/after comparison | `artifacts/comparison_table.md` |
| Beta experiment + conclusion | §5–§6 |
| Runnable experiment | `lab10_dpo.py` / `lab10_dpo.ipynb` |
| Colab run log | `artifacts/colab_run.log` |

---

## Reproduction

```bash
colab new -s lab10dpo --gpu T4
colab exec -s lab10dpo --timeout 10800 -f lab10_dpo.py
colab download -s lab10dpo /content/artifacts/<file> ./artifacts/<file>
colab stop -s lab10dpo
```
