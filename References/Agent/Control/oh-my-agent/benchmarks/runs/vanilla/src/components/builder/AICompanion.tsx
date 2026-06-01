'use client';

import { useState, useRef, useEffect } from 'react';
import { useWorldStore } from '@/store/useWorldStore';
import { getContextualPrompt, respondToChild } from '@/lib/ai';
import { v4 as uuid } from 'uuid';

export default function AICompanion() {
  const { messages, addMessage, objects, theme, showAI } = useWorldStore();
  const [input, setInput] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages]);

  if (!showAI) return null;

  const handleSend = () => {
    if (!input.trim()) return;
    addMessage({
      id: uuid(),
      role: 'child',
      content: input.trim(),
      timestamp: new Date().toISOString(),
    });
    setTimeout(() => {
      const response = respondToChild(input.trim(), objects, theme);
      addMessage(response);
    }, 500);
    setInput('');
  };

  const handleSuggestion = (text: string) => {
    addMessage({
      id: uuid(),
      role: 'child',
      content: text,
      timestamp: new Date().toISOString(),
    });
    setTimeout(() => {
      const response = respondToChild(text, objects, theme);
      addMessage(response);
    }, 500);
  };

  const handleInspire = () => {
    const prompt = getContextualPrompt(objects, theme, messages.length);
    addMessage(prompt);
  };

  return (
    <div className="flex flex-col h-full bg-gradient-to-b from-amber-50 to-orange-50/50 border-l border-border">
      <div className="p-3 border-b border-border/50 bg-white/50">
        <div className="flex items-center justify-between">
          <h3 className="font-bold text-sm text-foreground/80">
            ✨ AI Creative Buddy
          </h3>
          <button
            onClick={handleInspire}
            className="px-3 py-1 bg-accent/20 text-accent rounded-full text-xs font-bold hover:bg-accent/30 transition-colors"
          >
            💡 Inspire me!
          </button>
        </div>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto p-3 space-y-3">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`animate-slide-up ${
              msg.role === 'ai' ? 'flex justify-start' : 'flex justify-end'
            }`}
          >
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-2.5 ${
                msg.role === 'ai'
                  ? 'bg-white shadow-sm border border-border/50'
                  : 'bg-primary text-white'
              }`}
            >
              {msg.role === 'ai' && (
                <span className="text-xs font-bold text-accent block mb-0.5">
                  ✨ AI Buddy
                </span>
              )}
              <p className="text-sm leading-relaxed">{msg.content}</p>
              {msg.suggestions && msg.suggestions.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mt-2">
                  {msg.suggestions.map((s, i) => (
                    <button
                      key={i}
                      onClick={() => handleSuggestion(s)}
                      className="px-3 py-1 bg-primary/10 text-primary rounded-full text-xs font-bold hover:bg-primary/20 transition-colors"
                    >
                      {s}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="p-3 border-t border-border/50 bg-white/50">
        <div className="flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Type your ideas..."
            className="flex-1 px-4 py-2.5 rounded-2xl bg-white border-2 border-border focus:border-primary outline-none text-sm font-semibold transition-colors"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim()}
            className="px-4 py-2.5 bg-primary text-white rounded-2xl font-bold text-sm disabled:opacity-40 hover:bg-primary/90 transition-colors"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
