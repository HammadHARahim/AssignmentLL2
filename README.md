# Lab 10 — DPO Alignment + AlignLab Chat

Open-ended DPO experiment on `Qwen/Qwen2.5-0.5B` with a Vercel chat demo (Base / β=0.1 / β=0.5).

## Report & artifacts

- `REPORT.md` — evidence-backed lab write-up  
- `artifacts/` — outputs, comparison table, training logs  
- `lab10_dpo.py` / `lab10_dpo.ipynb` — Colab experiment  

## Chat demo (`web/`)

```bash
cd web
cp .env.example .env.local   # add HF_TOKEN + model repo ids
npm install
npm run dev
```

### Deploy

1. Export adapters / merged weights: `scripts/export_adapters_for_deploy.py` on Colab GPU  
2. `hf auth login` then push merged folders (script auto-pushes if `HF_TOKEN` + `HF_USERNAME` are set)  
3. Set Vercel env: `HF_TOKEN`, `HF_MODEL_DPO_01`, `HF_MODEL_DPO_05`  
4. Root directory: `web` → deploy  

```bash
cd web && vercel --prod
```
