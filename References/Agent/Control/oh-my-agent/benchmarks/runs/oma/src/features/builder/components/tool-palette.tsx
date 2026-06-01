"use client";

import { OBJECT_CATALOG } from "@/lib/constants";

const SHAPE_ICONS: Record<string, string> = {
  box: "📦",
  sphere: "⚽",
  cylinder: "🧪",
  cone: "🔺",
  torus: "💍",
  tree: "🌲",
  house: "🏠",
  star: "⭐",
};

export function ToolPalette() {
  return (
    <div className="w-20 md:w-24 bg-[var(--color-surface)] border-r border-gray-200 flex flex-col items-center py-4 gap-2 overflow-y-auto">
      <p className="text-xs font-bold text-[var(--color-text-muted)] mb-2">Objects</p>
      {OBJECT_CATALOG.map((item) => (
        <button
          key={item.id}
          draggable
          onDragStart={(e) => {
            e.dataTransfer.setData("object-shape", item.shape);
            e.dataTransfer.effectAllowed = "copy";
          }}
          className="w-14 h-14 md:w-16 md:h-16 flex flex-col items-center justify-center rounded-xl border-2 border-gray-200 hover:border-[var(--color-primary)] hover:bg-[var(--color-primary)]/5 transition-all cursor-grab active:cursor-grabbing"
          title={item.label}
        >
          <span className="text-2xl">{SHAPE_ICONS[item.shape] || "📦"}</span>
          <span className="text-[10px] text-[var(--color-text-muted)] mt-0.5">{item.label}</span>
        </button>
      ))}
    </div>
  );
}
