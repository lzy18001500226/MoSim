"use client";

import { useWorldStore } from "@/stores/world-store";
import { COLOR_PALETTE } from "@/lib/constants";

export function ColorPicker() {
  const selectedObjectId = useWorldStore((s) => s.selectedObjectId);
  const objects = useWorldStore((s) => s.objects);
  const updateObject = useWorldStore((s) => s.updateObject);

  const selectedObject = objects.find((o) => o.id === selectedObjectId);

  if (!selectedObject) {
    return (
      <div className="space-y-2">
        <p className="text-xs font-bold text-[var(--color-text-muted)]">Color</p>
        <p className="text-xs text-[var(--color-text-muted)] italic">Select an object first</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <p className="text-xs font-bold text-[var(--color-text-muted)]">Color</p>
      <div className="grid grid-cols-5 gap-1.5">
        {COLOR_PALETTE.map((color) => (
          <button
            key={color}
            onClick={() => updateObject(selectedObject.id, { color })}
            className={`w-7 h-7 rounded-full border-2 transition-transform hover:scale-110 ${
              selectedObject.color === color ? "border-[var(--color-text)] scale-110" : "border-transparent"
            }`}
            style={{ backgroundColor: color }}
            aria-label={`Color ${color}`}
          />
        ))}
      </div>
    </div>
  );
}
