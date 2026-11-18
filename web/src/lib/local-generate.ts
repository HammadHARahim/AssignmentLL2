"use client";

import { env, pipeline, type TextGenerationPipeline } from "@huggingface/transformers";
import { hfIdFor, type ModelId } from "@/lib/models";

// Always fetch remote weights in the browser
env.allowLocalModels = false;
env.useBrowserCache = true;

const cache = new Map<ModelId, TextGenerationPipeline>();

export type LoadProgress = {
  status: string;
  progress?: number;
  file?: string;
};

export async function getGenerator(
  model: ModelId,
  onProgress?: (p: LoadProgress) => void
): Promise<TextGenerationPipeline> {
  const hit = cache.get(model);
  if (hit) return hit;

  const modelId = hfIdFor(model);
  const generator = await pipeline("text-generation", modelId, {
    dtype: "q4",
    device: "wasm",
    progress_callback: (info: {
      status?: string;
      progress?: number;
      file?: string;
    }) => {
      onProgress?.({
        status: info.status || "loading",
        progress: info.progress,
        file: info.file,
      });
    },
  });

  cache.set(model, generator as TextGenerationPipeline);
  return generator as TextGenerationPipeline;
}

export async function generateLocal(
  model: ModelId,
  message: string,
  onProgress?: (p: LoadProgress) => void
): Promise<string> {
  const generator = await getGenerator(model, onProgress);
  const prompt =
    "You are a helpful assistant answering clearly and directly.\n\n" +
    `User: ${message}\nAssistant:`;

  const out = await generator(prompt, {
    max_new_tokens: 160,
    temperature: 0.7,
    top_p: 0.9,
    do_sample: true,
    return_full_text: false,
  });

  const row = Array.isArray(out) ? out[0] : out;
  const text =
    row && typeof row === "object" && "generated_text" in row
      ? String((row as { generated_text: string }).generated_text)
      : String(out);

  return text.replace(prompt, "").trim();
}
