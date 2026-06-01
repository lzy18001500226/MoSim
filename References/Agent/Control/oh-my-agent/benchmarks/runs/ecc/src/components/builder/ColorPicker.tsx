"use client";

import { useWorldStore } from "@/stores/world-store";
import { COLOR_PALETTE } from "@/lib/object-catalog";

export function ColorPicker() {
  const selectedObjectId = useWorldStore((s) => s.selectedObjectId);
  const objects = useWorldStore((s) => s.project.objects);
  const updateObject = useWorldStore((s) => s.updateObject);

  const selectedObject = objects.find((o) => o.id === selectedObjectId);

  if (!selectedObject) return null;

  return (
    <div className="flex flex-col gap-2 p-3 bg-white rounded-xl shadow-lg border border-sky/10">
      <h4 className="text-xs font-semibold text-text-muted">Color</h4>
      <div className="grid grid-cols-5 gap-1.5">
        {COLOR_PALETTE.map((color) => (
          <button
            key={color}
            onClick={() => updateObject(selectedObject.id, { color })}
            className={`w-7 h-7 rounded-full border-2 transition-transform hover:scale-110 active:scale-95 ${
              selectedObject.color === color ? "border-text ring-2 ring-sky/40" : "border-transparent"
            }`}
            style={{ backgroundColor: color }}
            aria-label={`Color ${color}`}
          />
        ))}
      </div>
    </div>
  );
}
