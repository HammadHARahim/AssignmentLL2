"""AlignLab — Streamlit chat demo for Lab 10 DPO checkpoints."""

from __future__ import annotations

import os

import streamlit as st
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODELS = {
    "Base": "Qwen/Qwen2.5-0.5B",
    "DPO β=0.1": "HammadHARahim/qwen25-0.5b-dpo-beta01",
    "DPO β=0.5": "HammadHARahim/qwen25-0.5b-dpo-beta05",
}

# DPO Hub uploads saved a broken tokenizer_config (extra_special_tokens as list).
# Always tokenize with the base Qwen tokenizer — vocab matches the fine-tunes.
TOKENIZER_ID = "Qwen/Qwen2.5-0.5B"

STARTERS = [
    "Explain attention in plain language for a first-year CS student.",
    "Summarise overfitting in exactly three short bullet points.",
    "A bat and a ball cost $1.10. The bat costs $1 more than the ball. How much is the ball?",
]

MAX_NEW_TOKENS = 160


def _hf_token() -> str | None:
    # Streamlit Cloud secrets first, then env / local hf login
    try:
        token = st.secrets.get("HF_TOKEN")  # type: ignore[attr-defined]
        if token:
            return str(token)
    except Exception:
        pass
    return os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")


@st.cache_resource(show_spinner=False)
def load_tokenizer():
    """Shared base tokenizer for all checkpoints."""
    token = _hf_token()
    tok = AutoTokenizer.from_pretrained(
        TOKENIZER_ID, trust_remote_code=True, token=token
    )
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    return tok


@st.cache_resource(show_spinner=False)
def load_model(model_id: str):
    """Load one causal LM checkpoint (cached per Hub id)."""
    token = _hf_token()
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        dtype=dtype,
        device_map="auto" if torch.cuda.is_available() else None,
        low_cpu_mem_usage=True,
        trust_remote_code=True,
        token=token,
    )
    if not torch.cuda.is_available():
        model = model.to("cpu")
    model.eval()
    return model


def generate(model, tokenizer, user_message: str) -> str:
    prompt = (
        "You are a helpful assistant answering clearly and directly.\n\n"
        f"User: {user_message}\nAssistant:"
    )
    inputs = tokenizer(prompt, return_tensors="pt")
    device = next(model.parameters()).device
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        out = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )
    gen = out[0][inputs["input_ids"].shape[-1] :]
    return tokenizer.decode(gen, skip_special_tokens=True).strip()


st.set_page_config(
    page_title="AlignLab — Lab 10 DPO Chat",
    page_icon="🧪",
    layout="centered",
)

st.title("AlignLab")
st.caption(
    "Lab 10 · Qwen2.5-0.5B · UltraFeedback DPO · switch Base / β=0.1 / β=0.5"
)

label = st.radio(
    "Checkpoint",
    list(MODELS.keys()),
    horizontal=True,
    index=1,
)
model_id = MODELS[label]
st.caption(f"Hub: [`{model_id}`](https://huggingface.co/{model_id})")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Pick a checkpoint, then ask the same prompt on each one to compare "
                "alignment. First load per model downloads weights from Hugging Face."
            ),
            "model": None,
        }
    ]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("model"):
            st.caption(msg["model"])
        st.markdown(msg["content"])

cols = st.columns(len(STARTERS))
for col, starter in zip(cols, STARTERS):
    if col.button(starter[:42] + ("…" if len(starter) > 42 else ""), use_container_width=True):
        st.session_state._pending = starter

prompt = st.chat_input("Ask the selected checkpoint…")
if "_pending" in st.session_state:
    prompt = st.session_state.pop("_pending")

if prompt:
    st.session_state.messages.append(
        {"role": "user", "content": prompt, "model": None}
    )
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner(f"Loading / generating · {label}"):
            try:
                tokenizer = load_tokenizer()
                model = load_model(model_id)
                reply = generate(model, tokenizer, prompt) or "(empty generation)"
            except Exception as exc:  # noqa: BLE001 — show Hub/OOM errors in UI
                reply = f"**Error:** {exc}"
        st.caption(label)
        st.markdown(reply)

    st.session_state.messages.append(
        {"role": "assistant", "content": reply, "model": label}
    )

st.divider()
st.markdown(
    "Report: [`REPORT.md`](https://github.com/HammadHARahim/AssignmentLL2/blob/main/REPORT.md) · "
    "Browser (Vercel): [web-kappa-ten-99.vercel.app](https://web-kappa-ten-99.vercel.app) · "
    "Code: [GitHub](https://github.com/HammadHARahim/AssignmentLL2)"
)
