# Plan: Lab 10 chat demo (Vercel)

## Architecture
1. Colab: retrain DPO β=0.1 & 0.5 (same recipe) → save LoRA adapters → merge into full weights
2. Push merged models to Hugging Face Hub (`*-dpo-beta01`, `*-dpo-beta05`); base stays `Qwen/Qwen2.5-0.5B`
3. Next.js app on Vercel: chat UI + `/api/chat` proxy to HF Inference API with `model` switcher
4. GitHub repo → `vercel --prod`

## Blocker
`HF_TOKEN` (+ HF username) required for push and inference.
