# Lab 10 — DPO Alignment + AlignLab Chat

Open-ended DPO experiment on `Qwen/Qwen2.5-0.5B` with a Vercel chat demo (Base / β=0.1 / β=0.5).

## Report & artifacts

- `REPORT.md` — evidence-backed lab write-up  
- `artifacts/` — outputs, comparison table, training logs  
- `lab10_dpo.py` / `lab10_dpo.ipynb` — Colab experiment  

## Chat demo (`web/`)

AlignLab runs checkpoints **in the browser** via `@huggingface/transformers` (WASM).

| Switcher | Weights |
|----------|---------|
| Base | `onnx-community/Qwen2.5-0.5B` |
| DPO β=0.1 | `HammadHARahim/qwen25-0.5b-dpo-beta01-onnx` |
| DPO β=0.5 | `HammadHARahim/qwen25-0.5b-dpo-beta05-onnx` |

Merged PyTorch checkpoints (server-side):  
`HammadHARahim/qwen25-0.5b-dpo-beta01` · `…-beta05`

```bash
cd web
npm install
npm run dev
```

### Deploy

```bash
cd web && vercel --prod
```

HF token is stored locally via `hf auth login` (also in `~/.zshrc` as `HF_TOKEN`). ONNX export: `scripts/convert_onnx_for_web.py` on Colab.
