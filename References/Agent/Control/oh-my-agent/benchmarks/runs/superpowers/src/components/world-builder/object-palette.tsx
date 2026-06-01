"use client";

import { useWorldStore } from "@/store/world-store";
import type { ObjectShape } from "@/types/world";

const OBJECTS: { shape: ObjectShape; label: string; emoji: string }[] = [
  { shape: "box", label: "Block", emoji: "🟥" },
  { shape: "sphere", label: "Ball", emoji: "🔵" },
  { shape: "cylinder", label: "Pillar", emoji: "🟡" },
  { shape: "cone", label: "Cone", emoji: "🔶" },
  { shape: "torus", label: "Ring", emoji: "💜" },
  { shape: "tree", label: "Tree", emoji: "🌳" },
  { shape: "house", label: "House", emoji: "🏠" },
  { shape: "character", label: "Person", emoji: "🧑" },
  { shape: "rock", label: "Rock", emoji: "🪨" },
  { shape: "flower", label: "Flower", emoji: "🌸" },
  { shape: "cloud", label: "Cloud", emoji: "☁️" },
  { shape: "star", label: "Star", emoji: "⭐" },
];

export default function ObjectPalette() {
  const addObject = useWorldStore((s) => s.addObject);

  return (
    <div className="bg-white/90 backdrop-blur rounded-2xl p-3 shadow-lg">
      <h3 className="text-sm font-bold text-purple-600 mb-2 text-center">Things to Add</h3>
      <div className="grid grid-cols-3 gap-1.5">
        {OBJECTS.map((item) => (
          <button
            key={item.shape}
            onClick={() => addObject(item.shape)}
            className="flex flex-col items-center gap-0.5 p-2 rounded-xl hover:bg-purple-100 active:bg-purple-200 transition-colors"
            title={`Add ${item.label}`}
          >
            <span className="text-2xl">{item.emoji}</span>
            <span className="text-[10px] font-medium text-gray-600">{item.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
