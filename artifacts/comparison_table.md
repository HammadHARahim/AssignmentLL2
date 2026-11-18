# Before vs After Alignment — Comparison

Scoring: Helpfulness / Relevance / Clarity / Instruction-following, each 1–5.  
Winner by sum (max 20). Same prompts and decoding settings for all models.

| Prompt | Type | Base (sum) | DPO β=0.1 (sum) | DPO β=0.5 (sum) | Winner | Evidence / reason |
|--------|------|------------|-----------------|-----------------|--------|-------------------|
| P1 | Explanation | 2+3+2+2=**9** | 3+4+4+3=**14** | 3+3+3+3=**12** | **DPO 0.1** | Base loops/chat-template junk; 0.1 gives a cleaner student-friendly analogy |
| P2 | Advice | 4+4+4+4=**16** | 2+2+3+2=**9** | 2+2+3+2=**9** | **Base** | Base is a real 3-day plan; both DPO runs lose the day-by-day structure |
| P3 | Summarisation | 3+4+4+2=**13** | 1+1+1+1=**4** | 2+3+2+2=**9** | **Base** | Asked for exactly 3 bullets; base is prose but usable; 0.1 collapses to `irebase` |
| P4 | Professional writing | 2+2+3+2=**9** | 3+3+3+3=**12** | 2+2+3+2=**9** | **DPO 0.1** | 0.1 better frames decline + alternatives; base/0.5 weak on exam reason / alternatives |
| P5 | Reasoning | 3+4+4+3=**14** | 5+5+5+5=**20** | 1+2+2+1=**6** | **DPO 0.1** | 0.1 finishes correctly ($0.05); base incomplete; 0.5 algebra breaks |
| P6 | QA | 1+2+2+1=**6** | 1+2+2+1=**6** | 3+3+2+3=**11** | **DPO 0.5** | Only 0.5 names **Islamabad**; base & 0.1 wrongly say Karachi (all have some junk tokens) |

## Win counts

| Model | Prompt wins |
|-------|-------------|
| Base | 2 (P2, P3) |
| DPO β=0.1 | 3 (P1, P4, P5) |
| DPO β=0.5 | 1 (P6) |

**Mean score:** Base ≈ 11.2 · DPO 0.1 ≈ 10.8 · DPO 0.5 ≈ 9.5  

DPO β=0.1 wins the most prompts but does **not** raise the average above base, because of a severe failure on P3 and weaker advice on P2.
