#!/usr/bin/env python3
"""Lab 10 — DPO alignment experiment (Qwen2.5-0.5B + ultrafeedback_binarized)."""

from __future__ import annotations

import json
import os
import random
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Install (idempotent)
# ---------------------------------------------------------------------------
subprocess.check_call(
    [
        sys.executable,
        "-m",
        "pip",
        "install",
        "-q",
        "transformers>=4.46.0",
        "trl>=0.12.0",
        "peft>=0.13.0",
        "datasets>=3.0.0",
        "accelerate>=1.0.0",
        "torchao>=0.16.0",
    ]
)

import torch
from datasets import load_dataset
from peft import LoraConfig, PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import DPOConfig, DPOTrainer

# ---------------------------------------------------------------------------
# Config (matches spec.md)
# ---------------------------------------------------------------------------
SEED = 42
MODEL_ID = "Qwen/Qwen2.5-0.5B"
DATASET_ID = "trl-lib/ultrafeedback_binarized"
SUBSET_SIZE = 1000
MAX_STEPS = 200
MAX_LENGTH = 512
MAX_NEW_TOKENS = 256
LR = 5e-5
ARTIFACTS = Path("/content/artifacts")
ARTIFACTS.mkdir(parents=True, exist_ok=True)

PROMPTS = [
    {
        "id": "P1",
        "type": "explanation",
        "text": (
            "Explain how a transformer attention layer decides which tokens "
            "matter, in plain language for a first-year CS student."
        ),
    },
    {
        "id": "P2",
        "type": "advice",
        "text": (
            "I have a midterm in three days and keep procrastinating. "
            "Give a concrete day-by-day plan I can follow."
        ),
    },
    {
        "id": "P3",
        "type": "summarisation",
        "text": (
            "Summarise the idea of overfitting in machine learning in exactly "
            "three short bullet points."
        ),
    },
    {
        "id": "P4",
        "type": "professional_writing",
        "text": (
            "Write a short, polite email declining a Friday meeting because of "
            "a prior exam, and propose two alternative times."
        ),
    },
    {
        "id": "P5",
        "type": "reasoning",
        "text": (
            "A bat and a ball cost $1.10 in total. The bat costs $1.00 more "
            "than the ball. How much does the ball cost? Show the steps."
        ),
    },
    {
        "id": "P6",
        "type": "question_answering",
        "text": (
            "What is the capital of Pakistan, and briefly why was it chosen "
            "over Karachi?"
        ),
    },
]


def set_seed(seed: int = SEED) -> None:
    random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def message_text(messages) -> str:
    if isinstance(messages, str):
        return messages
    parts = []
    for m in messages:
        role = m.get("role", "?")
        content = m.get("content", "")
        parts.append(f"**{role}:** {content}")
    return "\n\n".join(parts)


def extract_user_prompt(chosen) -> str:
    if isinstance(chosen, list):
        for m in chosen:
            if m.get("role") == "user":
                return m.get("content", "")
    return str(chosen)[:500]


def load_tokenizer():
    tok = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "left"
    return tok


def load_base_model():
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        dtype=dtype,
        device_map="auto",
        trust_remote_code=True,
    )
    model.config.use_cache = True
    return model


def generate(model, tokenizer, prompt: str) -> str:
    messages = [{"role": "user", "content": prompt}]
    if hasattr(tokenizer, "apply_chat_template") and tokenizer.chat_template:
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
    else:
        text = f"User: {prompt}\nAssistant:"
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
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


def eval_prompts(model, tokenizer, out_path: Path) -> dict:
    results = {}
    for p in PROMPTS:
        print(f"  generating {p['id']} ({p['type']})...")
        resp = generate(model, tokenizer, p["text"])
        results[p["id"]] = {
            "type": p["type"],
            "prompt": p["text"],
            "response": resp,
        }
    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"  wrote {out_path}")
    return results


def preference_inspection(ds) -> None:
    lines = [
        "# Preference Data Inspection",
        "",
        f"Dataset: `{DATASET_ID}` (train), seed={SEED}, n=5",
        "",
    ]
    for i in range(5):
        ex = ds[i]
        prompt = extract_user_prompt(ex["chosen"])
        chosen = message_text(ex["chosen"])
        rejected = message_text(ex["rejected"])
        sc = ex.get("score_chosen")
        sr = ex.get("score_rejected")
        why = (
            f"Chosen score={sc} vs rejected score={sr}. "
            "The chosen reply is typically more complete, clearer, or better "
            "aligned with the user request than the rejected reply."
        )
        lines += [
            f"## Example {i + 1}",
            "",
            f"**Prompt (user):** {prompt[:800]}",
            "",
            f"**Chosen** (truncated):",
            "",
            "```",
            chosen[:1200],
            "```",
            "",
            f"**Rejected** (truncated):",
            "",
            "```",
            rejected[:1200],
            "```",
            "",
            f"**Why chosen looks preferred:** {why}",
            "",
        ]
    # Pattern note
    lines += [
        "## Observed pattern",
        "",
        "Across these examples, chosen responses tend to be more specific, "
        "better structured, and closer to following the user's instruction "
        "than rejected ones (often shorter, vaguer, or less careful).",
        "",
    ]
    path = ARTIFACTS / "preference_inspection.md"
    path.write_text("\n".join(lines))
    print(f"wrote {path}")


def run_dpo(beta: float, train_ds, tokenizer) -> Path:
    out_dir = ARTIFACTS / f"dpo_beta_{beta}"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Fresh base + LoRA each run (fair beta comparison)
    model = load_base_model()
    model.config.use_cache = False

    peft_config = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    )

    use_fp16 = torch.cuda.is_available()
    args = DPOConfig(
        output_dir=str(out_dir / "trainer"),
        beta=beta,
        learning_rate=LR,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        max_steps=MAX_STEPS,
        logging_steps=10,
        save_steps=MAX_STEPS,
        save_total_limit=1,
        fp16=use_fp16,
        bf16=False,
        remove_unused_columns=False,
        max_length=MAX_LENGTH,
        report_to=[],
        seed=SEED,
        warmup_steps=10,
    )

    config_blob = {
        "beta": beta,
        "model": MODEL_ID,
        "subset_size": SUBSET_SIZE,
        "max_steps": MAX_STEPS,
        "lr": LR,
        "lora": {"r": 16, "alpha": 32, "dropout": 0.05},
        "max_length": MAX_LENGTH,
        "seed": SEED,
    }
    (out_dir / "config.json").write_text(json.dumps(config_blob, indent=2))

    trainer = DPOTrainer(
        model=model,
        ref_model=None,
        args=args,
        train_dataset=train_ds,
        processing_class=tokenizer,
        peft_config=peft_config,
    )

    print(f"=== DPO train beta={beta} ===")
    train_result = trainer.train()
    metrics = train_result.metrics
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))

    # Persist loss history from log history if present
    history = []
    for row in trainer.state.log_history:
        if "loss" in row or "rewards/accuracies" in row or "train_loss" in row:
            history.append(row)
    (out_dir / "train_log.json").write_text(json.dumps(history, indent=2))

    adapter_dir = out_dir / "adapter"
    trainer.save_model(str(adapter_dir))
    tokenizer.save_pretrained(str(adapter_dir))
    print(f"saved adapter → {adapter_dir}")

    # Free memory before eval reload
    del trainer
    del model
    torch.cuda.empty_cache()

    return adapter_dir


def eval_with_adapter(adapter_dir: Path, tokenizer, out_json: Path) -> None:
    base = load_base_model()
    model = PeftModel.from_pretrained(base, str(adapter_dir))
    model.eval()
    eval_prompts(model, tokenizer, out_json)
    del model
    del base
    torch.cuda.empty_cache()


def main() -> None:
    set_seed()
    print("device:", "cuda" if torch.cuda.is_available() else "cpu")
    if torch.cuda.is_available():
        print("gpu:", torch.cuda.get_device_name(0))

    tokenizer = load_tokenizer()

    print("loading dataset...")
    full = load_dataset(DATASET_ID, split="train")
    full = full.shuffle(seed=SEED)
    # inspection uses first 5 after shuffle for diversity
    preference_inspection(full)
    train_ds = full.select(range(SUBSET_SIZE))

    print("=== Base model eval ===")
    base = load_base_model()
    base.eval()
    eval_prompts(base, tokenizer, ARTIFACTS / "base_outputs.json")
    del base
    torch.cuda.empty_cache()

    for beta in (0.1, 0.5):
        adapter = run_dpo(beta, train_ds, tokenizer)
        # filenames per spec: dpo_0.1_outputs.json
        out_json = ARTIFACTS / f"dpo_{beta}_outputs.json"
        print(f"=== Eval DPO beta={beta} ===")
        eval_with_adapter(adapter, tokenizer, out_json)

    # Marker for successful end-to-end
    (ARTIFACTS / "DONE.txt").write_text("ok\n")
    print("ALL DONE")
    print("artifacts:", sorted(p.name for p in ARTIFACTS.iterdir()))


if __name__ == "__main__":
    main()
