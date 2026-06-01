"use client";

import { OBJECT_CATALOG } from "@/lib/object-catalog";

export function ObjectPalette() {
  const handleDragStart = (e: React.DragEvent, item: (typeof OBJECT_CATALOG)[0]) => {
    e.dataTransfer.setData("object-shape", item.shape);
    e.dataTransfer.setData("object-color", item.defaultColor);
    e.dataTransfer.setData("object-name", item.name);
    e.dataTransfer.effectAllowed = "copy";
  };

  return (
    <div className="flex flex-col gap-2 p-3">
      <h3 className="text-sm font-semibold text-text-muted px-1">Objects</h3>
      <div className="grid grid-cols-2 gap-2">
        {OBJECT_CATALOG.map((item) => (
          <button
            key={item.shape}
            draggable
            onDragStart={(e) => handleDragStart(e, item)}
            className="flex flex-col items-center gap-1 p-3 rounded-xl bg-white border-2 border-transparent hover:border-sky/50 hover:shadow-md transition-all cursor-grab active:cursor-grabbing active:scale-95 select-none"
          >
            <span className="text-2xl">{item.emoji}</span>
            <span className="text-xs font-medium text-text-muted">{item.name}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
