"use client";

import { useState } from "react";
import { useCompanionStore } from "@/stores/companion-store";
import { useWorldStore } from "@/stores/world-store";
import type { CompanionMessage } from "@/types/companion";

export function CompanionSidebar() {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState("");
  const { messages, suggestions, isLoading, addMessage, setLoading } = useCompanionStore();
  const objects = useWorldStore((s) => s.objects);
  const environment = useWorldStore((s) => s.environment);

  async function sendMessage(text?: string) {
    const userText = text || input.trim();
    if (!userText && !text) return;

    if (userText && !text) {
      const userMsg: CompanionMessage = {
        id: crypto.randomUUID(),
        role: "user",
        content: userText,
        timestamp: Date.now(),
      };
      addMessage(userMsg);
      setInput("");
    }

    setLoading(true);

    try {
      const res = await fetch("/api/ai/companion", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          objectCount: objects.length,
          objectTypes: objects.map((o) => o.label),
          environment: environment.theme,
          userMessage: userText || undefined,
          history: messages.slice(-6).map((m) => ({
            role: m.role,
            content: m.content,
          })),
        }),
      });

      const data = await res.json();
      const assistantMsg: CompanionMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: data.message,
        timestamp: Date.now(),
      };
      addMessage(assistantMsg);
    } catch {
      const errorMsg: CompanionMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: "Hmm, I got confused for a moment. Try again!",
        timestamp: Date.now(),
      };
      addMessage(errorMsg);
    } finally {
      setLoading(false);
    }
  }

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 w-14 h-14 bg-[var(--color-primary)] text-white rounded-full shadow-lg hover:scale-110 transition-transform flex items-center justify-center text-2xl z-50"
        aria-label="Open AI companion"
      >
        ✨
      </button>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 w-80 h-[28rem] bg-[var(--color-surface)] rounded-2xl shadow-xl border border-gray-200 flex flex-col z-50">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
        <div className="flex items-center gap-2">
          <span className="text-xl">✨</span>
          <span className="font-bold text-sm">Spark</span>
        </div>
        <button
          onClick={() => setIsOpen(false)}
          className="w-7 h-7 flex items-center justify-center rounded-full hover:bg-gray-100 text-gray-400"
        >
          ✕
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {messages.length === 0 && (
          <div className="text-center py-4">
            <p className="text-2xl mb-2">👋</p>
            <p className="text-sm text-[var(--color-text-muted)]">
              Hi! I&apos;m Spark, your creative buddy!
            </p>
          </div>
        )}
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`text-sm px-3 py-2 rounded-xl max-w-[85%] ${
              msg.role === "assistant"
                ? "bg-[var(--color-primary)]/10 text-[var(--color-text)] mr-auto"
                : "bg-gray-100 text-[var(--color-text)] ml-auto"
            }`}
          >
            {msg.content}
          </div>
        ))}
        {isLoading && (
          <div className="text-sm px-3 py-2 rounded-xl bg-[var(--color-primary)]/10 mr-auto animate-pulse">
            thinking...
          </div>
        )}
      </div>

      {/* Suggestions */}
      {messages.length === 0 && (
        <div className="px-3 pb-2 flex flex-wrap gap-1.5">
          {suggestions.map((s) => (
            <button
              key={s}
              onClick={() => sendMessage(s)}
              className="px-2.5 py-1 text-xs bg-[var(--color-primary)]/10 text-[var(--color-primary)] rounded-full hover:bg-[var(--color-primary)]/20 transition-colors"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="p-3 border-t border-gray-100">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Ask Spark anything..."
            className="flex-1 px-3 py-2 text-sm rounded-lg border border-gray-200 focus:border-[var(--color-primary)] focus:outline-none"
            disabled={isLoading}
          />
          <button
            onClick={() => sendMessage()}
            disabled={isLoading || !input.trim()}
            className="px-3 py-2 text-sm font-bold text-white bg-[var(--color-primary)] rounded-lg disabled:opacity-40"
          >
            →
          </button>
        </div>
      </div>
    </div>
  );
}
