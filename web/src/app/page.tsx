"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import { MODELS, type ModelId } from "@/lib/models";

type Role = "user" | "assistant" | "system";

type ChatMessage = {
  id: string;
  role: Role;
  content: string;
  model?: ModelId;
};

const STARTERS = [
  "Explain attention in plain language for a first-year CS student.",
  "Summarise overfitting in exactly three short bullet points.",
  "A bat and a ball cost $1.10. The bat costs $1 more than the ball. How much is the ball?",
];

export default function HomePage() {
  const [model, setModel] = useState<ModelId>("dpo-0.1");
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "system",
      content:
        "AlignLab chat — switch Base / DPO β=0.1 / DPO β=0.5 and compare how Lab 10 alignment changes replies.",
    },
  ]);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, busy]);

  async function send(text: string) {
    const trimmed = text.trim();
    if (!trimmed || busy) return;

    setError(null);
    setBusy(true);
    setInput("");

    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: trimmed,
    };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: trimmed, model }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.error || "Request failed");
      }
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: data.reply,
          model,
        },
      ]);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Something went wrong";
      setError(msg);
    } finally {
      setBusy(false);
    }
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    void send(input);
  }

  const active = MODELS.find((m) => m.id === model)!;

  return (
    <main className="relative mx-auto flex min-h-full w-full max-w-5xl flex-col px-4 py-6 sm:px-6 sm:py-10">
      <header className="anim-rise mb-8">
        <p
          className="mb-2 font-[family-name:var(--font-mono)] text-xs tracking-[0.22em] uppercase"
          style={{ color: "var(--accent-deep)" }}
        >
          Lab 10 · Preference alignment
        </p>
        <h1
          className="font-[family-name:var(--font-display)] text-5xl leading-none tracking-tight sm:text-6xl"
          style={{ color: "var(--ink)" }}
        >
          AlignLab
        </h1>
        <p className="anim-rise-delay mt-3 max-w-xl text-base leading-relaxed text-black/65 sm:text-lg">
          Chat with the same prompts across checkpoints. Pick a model, ask once, switch, ask again —
          evidence over vibes.
        </p>
      </header>

      <section
        className="anim-rise-delay flex min-h-[70vh] flex-1 flex-col overflow-hidden rounded-sm border"
        style={{
          borderColor: "var(--line)",
          background: "color-mix(in srgb, var(--panel) 92%, white)",
          boxShadow: "0 24px 60px rgba(14, 20, 24, 0.08)",
        }}
      >
        <div
          className="flex flex-col gap-3 border-b px-4 py-4 sm:flex-row sm:items-end sm:justify-between sm:px-5"
          style={{ borderColor: "var(--line)" }}
        >
          <div>
            <p className="font-[family-name:var(--font-mono)] text-[11px] tracking-widest uppercase text-black/45">
              Active checkpoint
            </p>
            <p className="mt-1 text-sm text-black/70">{active.blurb}</p>
          </div>
          <div className="flex flex-wrap gap-2" role="radiogroup" aria-label="Model">
            {MODELS.map((m) => {
              const on = m.id === model;
              return (
                <button
                  key={m.id}
                  type="button"
                  role="radio"
                  aria-checked={on}
                  onClick={() => setModel(m.id)}
                  className="rounded-sm px-3 py-2 font-[family-name:var(--font-mono)] text-xs tracking-wide transition-colors"
                  style={{
                    background: on ? "var(--ink)" : "transparent",
                    color: on ? "var(--paper)" : "var(--ink)",
                    border: `1px solid ${on ? "var(--ink)" : "var(--line)"}`,
                  }}
                >
                  {m.label}
                </button>
              );
            })}
          </div>
        </div>

        <div className="flex-1 space-y-4 overflow-y-auto px-4 py-5 sm:px-5">
          {messages.map((m) => (
            <article
              key={m.id}
              className={`max-w-[92%] sm:max-w-[80%] ${
                m.role === "user" ? "ml-auto text-right" : ""
              }`}
            >
              <p className="mb-1 font-[family-name:var(--font-mono)] text-[10px] tracking-widest uppercase text-black/40">
                {m.role === "user"
                  ? "You"
                  : m.role === "system"
                    ? "AlignLab"
                    : m.model || "assistant"}
              </p>
              <div
                className="whitespace-pre-wrap rounded-sm px-3.5 py-3 text-sm leading-relaxed sm:text-[15px]"
                style={{
                  background:
                    m.role === "user"
                      ? "var(--ink)"
                      : m.role === "system"
                        ? "rgba(31, 138, 110, 0.1)"
                        : "white",
                  color: m.role === "user" ? "var(--paper)" : "var(--ink)",
                  border: m.role === "user" ? "none" : `1px solid var(--line)`,
                }}
              >
                {m.content}
              </div>
            </article>
          ))}

          {busy && (
            <div className="flex items-center gap-1.5 text-black/50">
              <span className="typing-dot h-1.5 w-1.5 rounded-full bg-current" />
              <span className="typing-dot h-1.5 w-1.5 rounded-full bg-current" />
              <span className="typing-dot h-1.5 w-1.5 rounded-full bg-current" />
              <span className="ml-2 font-[family-name:var(--font-mono)] text-xs">
                generating with {active.label}
              </span>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        <div className="border-t px-4 py-3 sm:px-5" style={{ borderColor: "var(--line)" }}>
          <div className="mb-3 flex flex-wrap gap-2">
            {STARTERS.map((s) => (
              <button
                key={s}
                type="button"
                disabled={busy}
                onClick={() => void send(s)}
                className="max-w-full truncate rounded-sm border px-2.5 py-1.5 text-left text-xs text-black/65 transition hover:border-black/30 hover:text-black disabled:opacity-50"
                style={{ borderColor: "var(--line)" }}
              >
                {s}
              </button>
            ))}
          </div>

          {error && (
            <p
              className="mb-3 rounded-sm border px-3 py-2 text-sm"
              style={{
                borderColor: "rgba(180, 83, 9, 0.35)",
                background: "rgba(180, 83, 9, 0.08)",
                color: "var(--warn)",
              }}
              role="alert"
            >
              {error}
            </p>
          )}

          <form onSubmit={onSubmit} className="flex gap-2">
            <label className="sr-only" htmlFor="prompt">
              Prompt
            </label>
            <input
              id="prompt"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask the selected checkpoint…"
              disabled={busy}
              className="min-w-0 flex-1 rounded-sm border bg-white px-3 py-3 text-sm outline-none ring-[var(--glow)] focus:ring-2 disabled:opacity-60"
              style={{ borderColor: "var(--line)" }}
            />
            <button
              type="submit"
              disabled={busy || !input.trim()}
              className="rounded-sm px-4 py-3 font-[family-name:var(--font-display)] text-sm font-semibold tracking-wide text-white transition disabled:opacity-50"
              style={{ background: "var(--accent-deep)" }}
            >
              Send
            </button>
          </form>
        </div>
      </section>

      <footer className="mt-6 font-[family-name:var(--font-mono)] text-[11px] tracking-wide text-black/45">
        Qwen2.5-0.5B · UltraFeedback DPO · University of Gwadar Lab 10
      </footer>
    </main>
  );
}
