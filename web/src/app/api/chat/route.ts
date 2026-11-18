import { NextRequest, NextResponse } from "next/server";
import { isModelId, resolveHfModelId, type ModelId } from "@/lib/models";

export const runtime = "nodejs";
export const maxDuration = 60;

type ChatBody = {
  message?: string;
  model?: string;
};

function buildPrompt(userMessage: string): string {
  return (
    "You are a helpful assistant answering clearly and directly.\n\n" +
    `User: ${userMessage}\nAssistant:`
  );
}

async function generateWithHf(modelId: ModelId, message: string): Promise<string> {
  const token = process.env.HF_TOKEN || process.env.HUGGING_FACE_HUB_TOKEN;
  if (!token) {
    throw new Error(
      "HF_TOKEN is not set. Add a Hugging Face token in Vercel env (and set HF_MODEL_DPO_01 / HF_MODEL_DPO_05 after pushing merged adapters)."
    );
  }

  const hfModel = resolveHfModelId(modelId);
  const prompt = buildPrompt(message);

  const endpoints = [
    `https://router.huggingface.co/hf-inference/models/${hfModel}`,
    `https://api-inference.huggingface.co/models/${hfModel}`,
  ];

  let lastError = "Unknown Hugging Face error";

  for (const url of endpoints) {
    const res = await fetch(url, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        inputs: prompt,
        parameters: {
          max_new_tokens: 256,
          temperature: 0.7,
          top_p: 0.9,
          return_full_text: false,
          do_sample: true,
        },
        options: { wait_for_model: true },
      }),
    });

    const raw = await res.text();
    let data: unknown = null;
    try {
      data = JSON.parse(raw);
    } catch {
      data = raw;
    }

    if (!res.ok) {
      lastError =
        typeof data === "object" && data && "error" in data
          ? String((data as { error: string }).error)
          : raw.slice(0, 400);
      // try next endpoint
      continue;
    }

    if (Array.isArray(data) && data[0]?.generated_text != null) {
      return String(data[0].generated_text).trim();
    }
    if (
      typeof data === "object" &&
      data &&
      "generated_text" in data &&
      (data as { generated_text: string }).generated_text != null
    ) {
      return String((data as { generated_text: string }).generated_text).trim();
    }
    lastError = `Unexpected HF response: ${raw.slice(0, 400)}`;
  }

  throw new Error(lastError);
}

export async function POST(req: NextRequest) {
  try {
    const body = (await req.json()) as ChatBody;
    const message = (body.message || "").trim();
    const model = body.model || "base";

    if (!message) {
      return NextResponse.json({ error: "Message is required." }, { status: 400 });
    }
    if (!isModelId(model)) {
      return NextResponse.json({ error: "Invalid model id." }, { status: 400 });
    }

    const reply = await generateWithHf(model, message);
    return NextResponse.json({
      reply,
      model,
      hfModel: resolveHfModelId(model),
    });
  } catch (err) {
    const msg = err instanceof Error ? err.message : "Chat failed";
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}
