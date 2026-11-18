export type ModelId = "base" | "dpo-0.1" | "dpo-0.5";

export const MODELS: {
  id: ModelId;
  label: string;
  blurb: string;
  envKey: string;
  fallbackHfId: string;
}[] = [
  {
    id: "base",
    label: "Base",
    blurb: "Qwen2.5-0.5B before alignment",
    envKey: "HF_MODEL_BASE",
    fallbackHfId: "Qwen/Qwen2.5-0.5B",
  },
  {
    id: "dpo-0.1",
    label: "DPO β=0.1",
    blurb: "Aligned with stronger preference pull",
    envKey: "HF_MODEL_DPO_01",
    fallbackHfId: "Qwen/Qwen2.5-0.5B",
  },
  {
    id: "dpo-0.5",
    label: "DPO β=0.5",
    blurb: "Aligned with stronger KL to reference",
    envKey: "HF_MODEL_DPO_05",
    fallbackHfId: "Qwen/Qwen2.5-0.5B",
  },
];

export function resolveHfModelId(model: ModelId): string {
  const entry = MODELS.find((m) => m.id === model);
  if (!entry) return MODELS[0].fallbackHfId;
  return process.env[entry.envKey] || entry.fallbackHfId;
}

export function isModelId(value: string): value is ModelId {
  return MODELS.some((m) => m.id === value);
}
