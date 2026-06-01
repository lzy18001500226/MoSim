"use client";

import { useState, useEffect, useRef } from "react";
import { useWorldStore } from "@/store/worldStore";
import { getAIResponse, createAIMessage, createChildMessage } from "@/lib/ai";

export function AICompanion() {
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const greetedRef = useRef(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const currentWorld = useWorldStore((s) => s.currentWorld);
  const aiMessages = useWorldStore((s) => s.aiMessages);
  const addAIMessage = useWorldStore((s) => s.addAIMessage);

  useEffect(() => {
    if (!greetedRef.current && aiMessages.length === 0 && currentWorld) {
      greetedRef.current = true;
      getAIResponse(
        undefined,
        currentWorld.objects.length,
        currentWorld.environment
      ).then((data) => {
        addAIMessage(createAIMessage(data.response, data.suggestions));
      });
    }
  }, [aiMessages.length, currentWorld, addAIMessage]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [aiMessages]);

  const handleSend = async () => {
    if (!input.trim()) return;
    const msg = input.trim();
    setInput("");
    addAIMessage(createChildMessage(msg));
    setIsLoading(true);
    const data = await getAIResponse(
      msg,
      currentWorld?.objects.length || 0,
      currentWorld?.environment || "meadow"
    );
    addAIMessage(createAIMessage(data.response, data.suggestions));
    setIsLoading(false);
  };

  const handleSuggestionClick = async (suggestion: string) => {
    addAIMessage(createChildMessage(suggestion));
    setIsLoading(true);
    const data = await getAIResponse(
      suggestion,
      currentWorld?.objects.length || 0,
      currentWorld?.environment || "meadow"
    );
    addAIMessage(createAIMessage(data.response, data.suggestions));
    setIsLoading(false);
  };

  return (
    <div className="flex h-full flex-col bg-gradient-to-b from-indigo-50 to-purple-50">
      <div className="border-b border-indigo-100 p-3">
        <div className="flex items-center gap-2">
          <span className="text-2xl">🤖</span>
          <div>
            <h3 className="text-sm font-bold text-indigo-800">Creative Buddy</h3>
            <p className="text-xs text-indigo-500">Your imagination helper</p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {aiMessages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.role === "child" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm ${
                msg.role === "child"
                  ? "bg-indigo-500 text-white"
                  : "bg-white text-indigo-800 shadow-sm"
              }`}
            >
              {msg.content}
              {msg.suggestions && msg.suggestions.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {msg.suggestions.slice(0, 2).map((s, i) => (
                    <button
                      key={i}
                      onClick={() => handleSuggestionClick(s)}
                      className="rounded-full bg-indigo-50 px-2.5 py-1 text-xs text-indigo-600 hover:bg-indigo-100 transition"
                    >
                      {s.length > 30 ? s.slice(0, 30) + "..." : s}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="rounded-2xl bg-white px-4 py-2.5 text-sm text-indigo-400 shadow-sm">
              <span className="animate-pulse">Thinking...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="border-t border-indigo-100 p-3">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Tell me about your world..."
            className="flex-1 rounded-full border border-indigo-200 px-4 py-2.5 text-sm text-indigo-800 placeholder:text-indigo-300 focus:border-indigo-400 focus:outline-none"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="rounded-full bg-indigo-500 px-4 py-2.5 text-sm font-medium text-white hover:bg-indigo-600 disabled:opacity-50 transition"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
