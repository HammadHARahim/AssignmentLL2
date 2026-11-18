export type ModelId = "base" | "dpo-0.1" | "dpo-0.5";

export const MODELS: {
  id: ModelId;
  label: string;
  blurb: string;
  /** Hugging Face model id for @huggingface/transformers (ONNX) */
  hfId: string;
}[] = [
  {
    id: "base",
    label: "Base",
    blurb: "Qwen2.5-0.5B before alignment",
    hfId: "onnx-community/Qwen2.5-0.5B",
  },
  {
    id: "dpo-0.1",
    label: "DPO β=0.1",
    blurb: "Aligned with stronger preference pull",
    hfId: "HammadHARahim/qwen25-0.5b-dpo-beta01-onnx",
  },
  {
    id: "dpo-0.5",
    label: "DPO β=0.5",
    blurb: "Aligned with stronger KL to reference",
    hfId: "HammadHARahim/qwen25-0.5b-dpo-beta05-onnx",
  },
];

export function hfIdFor(model: ModelId): string {
  return MODELS.find((m) => m.id === model)?.hfId ?? MODELS[0].hfId;
}

export function isModelId(value: string): value is ModelId {
  return MODELS.some((m) => m.id === value);
}
