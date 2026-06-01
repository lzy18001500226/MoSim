"use client";

import { useWorldStore } from "@/store/world-store";
import type { EnvironmentTheme } from "@/types/world";

const THEMES: { theme: EnvironmentTheme; label: string; emoji: string }[] = [
  { theme: "meadow", label: "Meadow", emoji: "🌿" },
  { theme: "desert", label: "Desert", emoji: "🏜️" },
  { theme: "ocean", label: "Ocean", emoji: "🌊" },
  { theme: "space", label: "Space", emoji: "🚀" },
  { theme: "forest", label: "Forest", emoji: "🌲" },
  { theme: "snow", label: "Snow", emoji: "❄️" },
  { theme: "candy", label: "Candy", emoji: "🍬" },
  { theme: "volcano", label: "Volcano", emoji: "🌋" },
];

export default function ThemePicker() {
  const currentTheme = useWorldStore((s) => s.currentWorld?.theme);
  const setTheme = useWorldStore((s) => s.setTheme);

  return (
    <div className="bg-white/90 backdrop-blur rounded-2xl p-3 shadow-lg">
      <h3 className="text-sm font-bold text-purple-600 mb-2 text-center">World Theme</h3>
      <div className="grid grid-cols-4 gap-1.5">
        {THEMES.map((t) => (
          <button
            key={t.theme}
            onClick={() => setTheme(t.theme)}
            className={`flex flex-col items-center gap-0.5 p-1.5 rounded-xl transition-colors ${
              currentTheme === t.theme
                ? "bg-purple-100 ring-2 ring-purple-400"
                : "hover:bg-purple-50"
            }`}
          >
            <span className="text-xl">{t.emoji}</span>
            <span className="text-[10px] font-medium text-gray-600">{t.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
