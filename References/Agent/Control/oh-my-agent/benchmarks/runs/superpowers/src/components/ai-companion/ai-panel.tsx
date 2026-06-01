"use client";

import { useState, useRef, useEffect } from "react";
import { useWorldStore } from "@/store/world-store";
import { getCreativePrompt, getWhatIfPrompts, getReflectionPrompts, getSystemPrompt } from "@/lib/ai-prompts";

const QUICK_PROMPTS = [
  { label: "What if...?", type: "whatif" },
  { label: "Tell me more!", type: "more" },
  { label: "Help me think", type: "reflect" },
];

export default function AIPanel() {
  const [isOpen, setIsOpen] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const aiMessages = useWorldStore((s) => s.aiMessages);
  const addAIMessage = useWorldStore((s) => s.addAIMessage);
  const currentWorld = useWorldStore((s) => s.currentWorld);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [aiMessages]);

  useEffect(() => {
    if (currentWorld && aiMessages.length === 0) {
      handleAIResponse("greet");
    }
  }, [currentWorld?.id]);

  const handleAIResponse = async (type: string, userMessage?: string) => {
    if (!currentWorld) return;
    setIsLoading(true);

    try {
      const response = await fetch("/api/ai", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          type,
          userMessage,
          worldContext: getCreativePrompt(currentWorld),
          systemPrompt: getSystemPrompt(),
        }),
      });

      if (response.ok) {
        const data = await response.json();
        addAIMessage({ role: "assistant", content: data.message });
      } else {
        const fallback = getFallbackMessage(type);
        addAIMessage({ role: "assistant", content: fallback });
      }
    } catch {
      const fallback = getFallbackMessage(type);
      addAIMessage({ role: "assistant", content: fallback });
    }

    setIsLoading(false);
  };

  const getFallbackMessage = (type: string): string => {
    if (type === "greet") {
      return `Hi there! I'm Sparky, your creative buddy! I love your world "${currentWorld?.name}". What will you build first?`;
    }
    if (type === "whatif") {
      const prompts = getWhatIfPrompts();
      return prompts[Math.floor(Math.random() * prompts.length)];
    }
    if (type === "reflect") {
      const prompts = getReflectionPrompts();
      return prompts[Math.floor(Math.random() * prompts.length)];
    }
    const objectCount = currentWorld?.objects.length ?? 0;
    if (objectCount === 0) return "Your world is waiting! What do you want to add first?";
    if (objectCount < 3) return "Nice start! What else belongs in this world?";
    if (objectCount < 6) return "Your world is growing! Who lives here?";
    return "Wow, what an amazing world! What story does it tell?";
  };

  const handleSend = () => {
    if (!input.trim()) return;
    addAIMessage({ role: "user", content: input });
    handleAIResponse("chat", input);
    setInput("");
  };

  const handleQuickPrompt = (type: string) => {
    handleAIResponse(type);
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-4 right-4 w-14 h-14 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 text-white text-2xl shadow-lg hover:scale-110 transition-transform z-50 flex items-center justify-center"
      >
        ✦
      </button>
    );
  }

  return (
    <div className="w-72 bg-white/95 backdrop-blur rounded-2xl shadow-xl flex flex-col max-h-[500px] overflow-hidden">
      <div className="bg-gradient-to-r from-purple-500 to-pink-500 p-3 rounded-t-2xl flex items-center gap-2">
        <span className="text-white text-xl">✦</span>
        <span className="text-white font-bold text-sm flex-1">Sparky</span>
        <button
          onClick={() => setIsOpen(false)}
          className="text-white/70 hover:text-white text-lg"
        >
          ×
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-2 min-h-[200px]">
        {aiMessages.map((msg) => (
          <div
            key={msg.id}
            className={`text-sm rounded-2xl px-3 py-2 max-w-[90%] ${
              msg.role === "assistant"
                ? "bg-purple-50 text-purple-800 self-start"
                : "bg-blue-50 text-blue-800 self-end ml-auto"
            }`}
          >
            {msg.content}
          </div>
        ))}
        {isLoading && (
          <div className="bg-purple-50 text-purple-400 text-sm rounded-2xl px-3 py-2 max-w-[90%] animate-pulse">
            Sparky is thinking...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-2 border-t border-gray-100">
        <div className="flex gap-1 mb-2">
          {QUICK_PROMPTS.map((p) => (
            <button
              key={p.type}
              onClick={() => handleQuickPrompt(p.type)}
              disabled={isLoading}
              className="text-[10px] font-medium px-2 py-1 rounded-full bg-purple-100 text-purple-600 hover:bg-purple-200 disabled:opacity-50 transition-colors"
            >
              {p.label}
            </button>
          ))}
        </div>
        <div className="flex gap-1">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Talk to Sparky..."
            className="flex-1 text-sm bg-gray-50 rounded-xl px-3 py-1.5 outline-none focus:ring-2 ring-purple-300"
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="px-3 py-1.5 rounded-xl bg-purple-500 text-white text-sm font-bold hover:bg-purple-600 disabled:opacity-50 transition-colors"
          >
            ↑
          </button>
        </div>
      </div>
    </div>
  );
}
