# Tasks: Lab 10 DPO

## Task 1: Verify Colab CLI + GPU runtime

**Description:** Confirm `colab` (or equivalent) is installed, authenticated, and can attach a GPU runtime.

**Acceptance criteria:**
- [ ] CLI responds (`colab --help` or documented equivalent)
- [ ] Auth works without a new interactive login (per spec)
- [ ] GPU runtime can be created or selected

**Verification:** Run CLI status/help; note GPU type available.

**Dependencies:** None  
**Files:** none (env check only)  
**Scope:** S

---

## Task 2: Scaffold `lab10_dpo.ipynb`

**Description:** Create notebook with install cell, seeds, PROMPTS P1–P6, artifact dirs, and shared generate helper.

**Acceptance criteria:**
- [ ] Notebook exists at repo root
- [ ] Spec prompts and decoding kwargs match `spec.md`
- [ ] Writes under `/content/artifacts`

**Verification:** Open notebook; smoke-run install + import cells on Colab.

**Dependencies:** Task 1  
**Files:** `lab10_dpo.ipynb`  
**Scope:** M

---

## Task 3: Preference inspection cell

**Description:** Load dataset subset, dump 5 examples (seed 42) with chosen/rejected and short analysis notes template.

**Acceptance criteria:**
- [ ] `artifacts/preference_inspection.md` has 5 examples
- [ ] chosen ≠ rejected for each

**Verification:** File non-empty; 5 sections present.

**Dependencies:** Task 2  
**Files:** `lab10_dpo.ipynb`, `artifacts/preference_inspection.md`  
**Scope:** S

---

## Task 4: Base model eval

**Description:** Load `Qwen/Qwen2.5-0.5B`, generate for P1–P6, save JSON.

**Acceptance criteria:**
- [ ] `artifacts/base_outputs.json` has all six prompt IDs + non-empty responses

**Verification:** JSON parse; six keys; smoke P1 non-empty before DPO.

**Dependencies:** Task 2  
**Files:** `lab10_dpo.ipynb`, `artifacts/base_outputs.json`  
**Scope:** S

---

### Checkpoint A (after Tasks 1–4)
- [ ] CLI + GPU OK
- [ ] Preference inspection + base outputs exist
- [ ] Review before starting DPO (time/cost gate)

---

## Task 5: DPO train β=0.1 + eval

**Description:** Train LoRA DPO with beta=0.1 on 1000 pairs / ≤200 steps; save logs; generate on P1–P6 with adapter.

**Acceptance criteria:**
- [ ] `artifacts/dpo_beta_0.1/` has loss/config logs
- [ ] `artifacts/dpo_0.1_outputs.json` has six responses
- [ ] Train completes without OOM

**Verification:** Log shows ≥1 step; JSON parity with base prompt IDs.

**Dependencies:** Tasks 3–4  
**Files:** `lab10_dpo.ipynb`, `artifacts/dpo_beta_0.1/`, `artifacts/dpo_0.1_outputs.json`  
**Scope:** M

---

## Task 6: DPO train β=0.5 + eval

**Description:** Same as Task 5 with beta=0.5; separate artifact folder.

**Acceptance criteria:**
- [ ] `artifacts/dpo_beta_0.5/` logs present
- [ ] `artifacts/dpo_0.5_outputs.json` has six responses

**Verification:** Same as Task 5 for 0.5 paths.

**Dependencies:** Task 5  
**Files:** `lab10_dpo.ipynb`, `artifacts/dpo_beta_0.5/`, `artifacts/dpo_0.5_outputs.json`  
**Scope:** M

---

### Checkpoint B (after Tasks 5–6)
- [ ] Both DPO runs finished
- [ ] Three output JSON files aligned on prompt IDs
- [ ] Pull logs + JSON only to local `artifacts/`

---

## Task 7: Comparison table + REPORT.md

**Description:** Build `comparison_table.md` (prompt, base, dpo0.1, dpo0.5, winner, reason); write full `REPORT.md` answering all six final-analysis questions with evidence.

**Acceptance criteria:**
- [ ] Comparison covers all six prompts
- [ ] Report covers design, preference analysis, training summary, before/after, beta compare, six Qs
- [ ] Conclusion cites artifact evidence (not assumed “DPO is better”)

**Verification:** Manual read against lab deliverables + marking rubric.

**Dependencies:** Checkpoint B  
**Files:** `artifacts/comparison_table.md`, `REPORT.md`  
**Scope:** M

---

### Checkpoint C — Done
- [ ] All `spec.md` success criteria checked
- [ ] Artifacts + report ready for submission
