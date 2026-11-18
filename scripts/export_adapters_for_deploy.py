#!/usr/bin/env python3
"""Retrain DPO (both betas), save LoRA adapters under /content/artifacts for download.

Optional: set HF_TOKEN + HF_USERNAME in the environment to merge + push to the Hub.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

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
        "huggingface_hub>=0.26.0",
    ]
)

import torch
from datasets import load_dataset
from peft import LoraConfig, PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import DPOConfig, DPOTrainer

SEED = 42
MODEL_ID = "Qwen/Qwen2.5-0.5B"
DATASET_ID = "trl-lib/ultrafeedback_binarized"
SUBSET_SIZE = 1000
MAX_STEPS = 200
MAX_LENGTH = 512
LR = 5e-5
ARTIFACTS = Path("/content/artifacts")
ARTIFACTS.mkdir(parents=True, exist_ok=True)


def set_seed(seed: int = SEED) -> None:
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def load_tokenizer():
    tok = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    return tok


def load_base_model():
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    return AutoModelForCausalLM.from_pretrained(
        MODEL_ID, dtype=dtype, device_map="auto", trust_remote_code=True
    )


def run_dpo(beta: float, train_ds, tokenizer) -> Path:
    out_dir = ARTIFACTS / f"dpo_beta_{beta}"
    out_dir.mkdir(parents=True, exist_ok=True)
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
    args = DPOConfig(
        output_dir=str(out_dir / "trainer"),
        beta=beta,
        learning_rate=LR,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        max_steps=MAX_STEPS,
        logging_steps=20,
        save_steps=MAX_STEPS,
        save_total_limit=1,
        fp16=torch.cuda.is_available(),
        bf16=False,
        remove_unused_columns=False,
        max_length=MAX_LENGTH,
        report_to=[],
        seed=SEED,
        warmup_steps=10,
    )
    (out_dir / "config.json").write_text(
        json.dumps({"beta": beta, "model": MODEL_ID, "max_steps": MAX_STEPS}, indent=2)
    )
    trainer = DPOTrainer(
        model=model,
        ref_model=None,
        args=args,
        train_dataset=train_ds,
        processing_class=tokenizer,
        peft_config=peft_config,
    )
    print(f"=== DPO train beta={beta} ===")
    result = trainer.train()
    (out_dir / "metrics.json").write_text(json.dumps(result.metrics, indent=2))
    adapter_dir = out_dir / "adapter"
    trainer.save_model(str(adapter_dir))
    tokenizer.save_pretrained(str(adapter_dir))
    del trainer, model
    torch.cuda.empty_cache()
    return adapter_dir


def merge_and_maybe_push(beta: float, adapter_dir: Path, tokenizer) -> None:
    merged_dir = ARTIFACTS / f"merged_beta_{beta}"
    print(f"=== merge beta={beta} ===")
    base = load_base_model()
    model = PeftModel.from_pretrained(base, str(adapter_dir))
    merged = model.merge_and_unload()
    merged_dir.mkdir(parents=True, exist_ok=True)
    merged.save_pretrained(str(merged_dir), safe_serialization=True)
    tokenizer.save_pretrained(str(merged_dir))
    del merged, model, base
    torch.cuda.empty_cache()

    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    username = os.environ.get("HF_USERNAME")
    if not token or not username:
        print("HF_TOKEN/HF_USERNAME not set — skipped Hub push for", merged_dir)
        return

    from huggingface_hub import HfApi, login

    login(token=token)
    repo_id = f"{username}/qwen25-0.5b-dpo-beta{str(beta).replace('.', '')}"
    api = HfApi()
    api.create_repo(repo_id, exist_ok=True, private=False)
    api.upload_folder(folder_path=str(merged_dir), repo_id=repo_id, repo_type="model")
    print("pushed", repo_id)
    (ARTIFACTS / "hub_repos.json").write_text(
        json.dumps(
            {
                "base": MODEL_ID,
                f"dpo_{beta}": repo_id,
            },
            indent=2,
        )
    )


def main() -> None:
    set_seed()
    tokenizer = load_tokenizer()
    full = load_dataset(DATASET_ID, split="train").shuffle(seed=SEED)
    train_ds = full.select(range(SUBSET_SIZE))
    repos = {"base": MODEL_ID}
    for beta in (0.1, 0.5):
        adapter = run_dpo(beta, train_ds, tokenizer)
        merge_and_maybe_push(beta, adapter, tokenizer)
        repos[f"dpo_{beta}"] = f"merged_beta_{beta}"
    (ARTIFACTS / "EXPORT_DONE.txt").write_text(json.dumps(repos, indent=2))
    print("EXPORT_DONE", repos)


if __name__ == "__main__":
    main()
