#!/usr/bin/env python3
"""Export DPO merges to ONNX layout usable by @huggingface/transformers in-browser."""

from __future__ import annotations

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
        "-U",
        "huggingface_hub",
        "transformers>=4.46.0",
        "accelerate",
        "onnx",
        "onnxruntime",
        "optimum[onnxruntime]",
        "diffusers",
    ]
)

from huggingface_hub import HfApi, login
from optimum.onnxruntime import ORTModelForCausalLM
from transformers import AutoTokenizer

TOKEN = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
USER = os.environ.get("HF_USERNAME", "HammadHARahim")
assert TOKEN, "HF_TOKEN required"

login(token=TOKEN)
api = HfApi(token=TOKEN)

SOURCES = {
    "0.1": f"{USER}/qwen25-0.5b-dpo-beta01",
    "0.5": f"{USER}/qwen25-0.5b-dpo-beta05",
}


def convert_one(beta: str, src: str) -> str:
    out = Path(f"/content/onnx_beta_{beta}")
    out.mkdir(parents=True, exist_ok=True)
    print("exporting", src)
    model = ORTModelForCausalLM.from_pretrained(src, export=True)
    tok = AutoTokenizer.from_pretrained(src, trust_remote_code=True)
    # Save into onnx/ subfolder naming expected by many web loaders
    onnx_dir = out / "onnx"
    onnx_dir.mkdir(exist_ok=True)
    model.save_pretrained(out)
    # Move/copy model.onnx into onnx/
    for p in out.glob("*.onnx"):
        target = onnx_dir / ("model.onnx" if p.name == "model.onnx" else p.name)
        p.replace(target)
    # Also provide fp16 alias if only model.onnx exists
    main = onnx_dir / "model.onnx"
    if main.exists() and not (onnx_dir / "model_fp16.onnx").exists():
        (onnx_dir / "model_fp16.onnx").write_bytes(main.read_bytes())
    tok.save_pretrained(out)
    # Ensure config present
    repo_id = f"{USER}/qwen25-0.5b-dpo-beta{beta.replace('.', '')}-onnx"
    api.create_repo(repo_id, exist_ok=True, private=False, token=TOKEN)
    api.upload_folder(folder_path=str(out), repo_id=repo_id, repo_type="model", token=TOKEN)
    print("pushed", repo_id)
    return repo_id


def main() -> None:
    repos = {"base_onnx": "onnx-community/Qwen2.5-0.5B"}
    for beta, src in SOURCES.items():
        repos[f"dpo_{beta}_onnx"] = convert_one(beta, src)
    Path("/content/onnx_repos.json").write_text(__import__("json").dumps(repos, indent=2))
    print("ONNX_OK", repos)


if __name__ == "__main__":
    main()
