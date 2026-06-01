"use client";

import { useState } from "react";
import { useAiStore } from "@/stores/ai-store";
import { useWorldStore } from "@/stores/world-store";

const STARTER_PROMPTS = [
  "What kind of world do you want to build?",
  "Who lives in this place?",
  "What happens here at night?",
  "Can you make it stranger?",
  "What if gravity changed?",
  "What feeling does your world show?",
  "What is missing from this place?",
  "What would happen if it rained candy?",
];

const SUGGESTION_CHIPS = [
  { label: "Add something weird", emoji: "🦑" },
  { label: "Change the mood", emoji: "🎭" },
  { label: "Tell me a story", emoji: "📖" },
  { label: "What if...", emoji: "💭" },
  { label: "Make it bigger!", emoji: "🔮" },
  { label: "Add a character", emoji: "🧙" },
];

export function AiCompanionPanel() {
  const { messages, isOpen, isLoading, addMessage, toggleOpen, setLoading } = useAiStore();
  const objects = useWorldStore((s) => s.project.objects);
  const theme = useWorldStore((s) => s.project.theme);
  const [inputValue, setInputValue] = useState("");

  const handleSend = async (text: string) => {
    if (!text.trim()) return;
    addMessage("user", text);
    setInputValue("");
    setLoading(true);

    try {
      const response = await fetch("/api/ai", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          context: {
            objectCount: objects.length,
            objectNames: objects.map((o) => o.name),
            theme,
          },
        }),
      });

      const data = await response.json();
      addMessage("assistant", data.reply);
    } catch {
      addMessage("assistant", getRandomPrompt());
    } finally {
      setLoading(false);
    }
  };

  const handleChipClick = (label: string) => {
    handleSend(label);
  };

  if (!isOpen) {
    return (
      <button
        onClick={toggleOpen}
        className="fixed bottom-6 right-6 w-14 h-14 rounded-full bg-lavender text-white shadow-lg shadow-lavender/40 flex items-center justify-center text-2xl hover:scale-110 transition-transform active:scale-95 z-50"
        aria-label="Open AI companion"
      >
        🤖
      </button>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 w-80 max-h-[70vh] bg-white rounded-2xl shadow-xl border border-lavender/20 flex flex-col overflow-hidden z-50">
      <header className="flex items-center justify-between px-4 py-3 bg-gradient-to-r from-lavender/20 to-sky/20 border-b border-lavender/10">
        <div className="flex items-center gap-2">
          <span className="text-xl">🤖</span>
          <span className="font-semibold text-sm">Creative Buddy</span>
        </div>
        <button
          onClick={toggleOpen}
          className="w-7 h-7 rounded-full bg-white/80 flex items-center justify-center text-text-muted hover:bg-white transition-colors"
          aria-label="Close AI companion"
        >
          ✕
        </button>
      </header>

      <div className="flex-1 overflow-y-auto p-3 space-y-3 min-h-[200px]">
        {messages.length === 0 && (
          <div className="text-center py-4">
            <p className="text-2xl mb-2">✨</p>
            <p className="text-sm text-text-muted">
              Hi! I&apos;m your creative buddy. Ask me anything about your world!
            </p>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[85%] px-3 py-2 rounded-2xl text-sm ${
                msg.role === "user"
                  ? "bg-sky text-white rounded-br-md"
                  : "bg-lavender/10 text-text rounded-bl-md"
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-lavender/10 px-3 py-2 rounded-2xl rounded-bl-md text-sm text-text-muted">
              Thinking...
            </div>
          </div>
        )}
      </div>

      <div className="px-3 py-2 border-t border-sky/10">
        <div className="flex flex-wrap gap-1.5 mb-2">
          {SUGGESTION_CHIPS.map((chip) => (
            <button
              key={chip.label}
              onClick={() => handleChipClick(chip.label)}
              className="flex items-center gap-1 px-2.5 py-1 rounded-full bg-lavender/10 text-xs font-medium text-lavender hover:bg-lavender/20 transition-colors"
            >
              <span>{chip.emoji}</span>
              {chip.label}
            </button>
          ))}
        </div>

        <div className="flex gap-2">
          <input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend(inputValue)}
            placeholder="Ask me anything..."
            className="flex-1 px-3 py-2 rounded-full bg-surface border border-sky/20 text-sm focus:outline-none focus:border-sky focus:ring-2 focus:ring-sky/20"
          />
          <button
            onClick={() => handleSend(inputValue)}
            disabled={!inputValue.trim() || isLoading}
            className="w-9 h-9 rounded-full bg-lavender text-white flex items-center justify-center text-sm hover:bg-lavender/80 transition-colors disabled:opacity-50"
          >
            ↑
          </button>
        </div>
      </div>
    </div>
  );
}

function getRandomPrompt(): string {
  return STARTER_PROMPTS[Math.floor(Math.random() * STARTER_PROMPTS.length)];
}
