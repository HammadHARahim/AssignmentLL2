# Lab 10 — DPO Alignment + AlignLab Chat

Open-ended DPO experiment on `Qwen/Qwen2.5-0.5B` with **two demos** (same pattern as Infinitic):

| Demo | Host | Path |
|------|------|------|
| Streamlit chat (Python + Hub weights) | Streamlit Community Cloud | `apps/streamlit/` |
| Browser chat (WASM) | Vercel | `web/` |

See **[docs/DEPLOY.md](docs/DEPLOY.md)** for both deploys.

## Lab artifacts

- `REPORT.md` — evidence-backed write-up  
- `artifacts/` — outputs, comparison, training logs  
- `lab10_dpo.py` / `lab10_dpo.ipynb` — Colab experiment  

## Hub checkpoints

- Base: `Qwen/Qwen2.5-0.5B`
- DPO β=0.1: [`HammadHARahim/qwen25-0.5b-dpo-beta01`](https://huggingface.co/HammadHARahim/qwen25-0.5b-dpo-beta01)
- DPO β=0.5: [`HammadHARahim/qwen25-0.5b-dpo-beta05`](https://huggingface.co/HammadHARahim/qwen25-0.5b-dpo-beta05)

## Quick start (Streamlit)

```bash
pip install -r apps/streamlit/requirements.txt
streamlit run apps/streamlit/app.py
```

## Quick start (Vercel / local Next)

```bash
cd web && npm install && npm run dev
```
