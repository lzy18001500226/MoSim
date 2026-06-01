"use client";

import { useWorldStore } from "@/store/world-store";

const COLORS = [
  "#FF6B6B", "#FF8E53", "#FBBF24", "#4ADE80", "#4ECDC4",
  "#60A5FA", "#A78BFA", "#F472B6", "#9CA3AF", "#FFFFFF",
  "#1E293B", "#8B5A2B",
];

const ANIMATIONS = [
  { value: "", label: "None" },
  { value: "bounce", label: "Bounce" },
  { value: "spin", label: "Spin" },
  { value: "float", label: "Float" },
  { value: "pulse", label: "Pulse" },
];

export default function PropertyPanel() {
  const selectedId = useWorldStore((s) => s.selectedObjectId);
  const objects = useWorldStore((s) => s.currentWorld?.objects ?? []);
  const updateObject = useWorldStore((s) => s.updateObject);
  const removeObject = useWorldStore((s) => s.removeObject);
  const pushUndo = useWorldStore((s) => s.pushUndo);

  const selected = objects.find((o) => o.id === selectedId);
  if (!selected) return null;

  return (
    <div className="bg-white/90 backdrop-blur rounded-2xl p-4 shadow-lg space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-bold text-purple-600">{selected.name}</h3>
        <button
          onClick={() => removeObject(selected.id)}
          className="text-xs text-red-400 hover:text-red-600 font-medium px-2 py-1 rounded-lg hover:bg-red-50"
        >
          Remove
        </button>
      </div>

      <div>
        <label className="text-xs font-medium text-gray-500 mb-1 block">Color</label>
        <div className="flex flex-wrap gap-1.5">
          {COLORS.map((color) => (
            <button
              key={color}
              onClick={() => {
                pushUndo();
                updateObject(selected.id, { color });
              }}
              className={`w-7 h-7 rounded-full border-2 transition-transform hover:scale-110 ${
                selected.color === color ? "border-purple-500 scale-110" : "border-gray-200"
              }`}
              style={{ backgroundColor: color }}
            />
          ))}
        </div>
      </div>

      <div>
        <label className="text-xs font-medium text-gray-500 mb-1 block">Size</label>
        <input
          type="range"
          min="0.3"
          max="3"
          step="0.1"
          value={selected.scale[0]}
          onChange={(e) => {
            const s = parseFloat(e.target.value);
            updateObject(selected.id, { scale: [s, s, s] });
          }}
          onMouseDown={pushUndo}
          className="w-full accent-purple-500"
        />
        <div className="flex justify-between text-[10px] text-gray-400">
          <span>Small</span>
          <span>Big</span>
        </div>
      </div>

      <div>
        <label className="text-xs font-medium text-gray-500 mb-1 block">Animation</label>
        <div className="flex flex-wrap gap-1">
          {ANIMATIONS.map((anim) => (
            <button
              key={anim.value}
              onClick={() => {
                pushUndo();
                updateObject(selected.id, {
                  animated: anim.value !== "",
                  animationType: anim.value as WorldObject["animationType"],
                });
              }}
              className={`text-xs px-2.5 py-1 rounded-full transition-colors ${
                (selected.animationType ?? "") === anim.value
                  ? "bg-purple-500 text-white"
                  : "bg-gray-100 text-gray-600 hover:bg-purple-100"
              }`}
            >
              {anim.label}
            </button>
          ))}
        </div>
      </div>

      <div>
        <label className="text-xs font-medium text-gray-500 mb-1 block">Move</label>
        <div className="grid grid-cols-3 gap-1">
          {(["x", "y", "z"] as const).map((axis, i) => (
            <div key={axis} className="flex flex-col items-center">
              <span className="text-[10px] text-gray-400 uppercase">{axis}</span>
              <div className="flex gap-0.5">
                <button
                  onClick={() => {
                    pushUndo();
                    const pos = [...selected.position] as [number, number, number];
                    pos[i] -= 0.5;
                    updateObject(selected.id, { position: pos });
                  }}
                  className="w-6 h-6 rounded bg-gray-100 hover:bg-purple-100 text-sm font-bold"
                >
                  -
                </button>
                <button
                  onClick={() => {
                    pushUndo();
                    const pos = [...selected.position] as [number, number, number];
                    pos[i] += 0.5;
                    updateObject(selected.id, { position: pos });
                  }}
                  className="w-6 h-6 rounded bg-gray-100 hover:bg-purple-100 text-sm font-bold"
                >
                  +
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

type WorldObject = import("@/types/world").WorldObject;
