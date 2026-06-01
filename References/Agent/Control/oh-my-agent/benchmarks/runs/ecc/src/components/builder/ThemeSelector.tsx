"use client";

import { useWorldStore } from "@/stores/world-store";
import { ENVIRONMENT_THEMES } from "@/lib/object-catalog";

export function ThemeSelector() {
  const currentTheme = useWorldStore((s) => s.project.theme);
  const setTheme = useWorldStore((s) => s.setTheme);

  return (
    <div className="flex gap-1.5 overflow-x-auto py-1 px-1">
      {ENVIRONMENT_THEMES.map((theme) => (
        <button
          key={theme.id}
          onClick={() => setTheme(theme.id)}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium whitespace-nowrap transition-all ${
            currentTheme === theme.id
              ? "bg-sky text-white shadow-md"
              : "bg-white/80 text-text-muted hover:bg-sky/10 border border-sky/20"
          }`}
        >
          <span>{theme.emoji}</span>
          <span>{theme.name}</span>
        </button>
      ))}
    </div>
  );
}
