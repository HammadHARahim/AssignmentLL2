# Deploy Streamlit and Vercel

Same dual-demo pattern as your Infinitic classifier: **Streamlit** runs the Python models; **Vercel** hosts the browser UI. Vercel does not provide free LLM inference and cannot run a Streamlit server.

| Target | Runtime | Model loading |
|--------|---------|---------------|
| Streamlit Community Cloud | Python + Transformers | Downloads Base / DPO merges from the Hub |
| Vercel (`web/`) | Next.js + transformers.js | In-browser WASM (ONNX when available) |

## Models on Hugging Face

| Switcher | Hub id |
|----------|--------|
| Base | `Qwen/Qwen2.5-0.5B` |
| DPO β=0.1 | `HammadHARahim/qwen25-0.5b-dpo-beta01` |
| DPO β=0.5 | `HammadHARahim/qwen25-0.5b-dpo-beta05` |

## Streamlit Community Cloud

1. Open [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
2. Create app from `HammadHARahim/AssignmentLL2`.
3. Set:
   - Branch: `main`
   - Main file path: `apps/streamlit/app.py`
   - Python version: **3.12**
4. In **Advanced settings → Secrets**, add:

```toml
HF_TOKEN = "hf_..."
```

5. Deploy. First message per checkpoint downloads ~1 GB weights (CPU is slow; free tier may OOM — if so, use a larger Cloud tier or run locally).

### Local

```bash
pip install -r apps/streamlit/requirements.txt
export HF_TOKEN=hf_...   # optional if already `hf auth login`
streamlit run apps/streamlit/app.py
```

## Vercel (browser AlignLab)

Root directory: **`web`**.

```bash
cd web
vercel --prod
```

Live: https://web-kappa-ten-99.vercel.app

GitHub integration: import `AssignmentLL2`, set Root Directory to `web`, deploy on push to `main`.
