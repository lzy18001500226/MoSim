"use client";

import { useWorldStore } from "@/stores/world-store";

export function ToolBar() {
  const selectedObjectId = useWorldStore((s) => s.selectedObjectId);
  const removeObject = useWorldStore((s) => s.removeObject);
  const mode = useWorldStore((s) => s.mode);
  const setMode = useWorldStore((s) => s.setMode);

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={() => setMode(mode === "build" ? "play" : "build")}
        className={`flex items-center gap-1.5 px-4 py-2 rounded-full font-medium text-sm transition-all ${
          mode === "play"
            ? "bg-grass text-white shadow-md"
            : "bg-white border border-grass/30 text-grass hover:bg-grass/10"
        }`}
      >
        <span>{mode === "play" ? "🔨" : "🏃"}</span>
        {mode === "play" ? "Build" : "Explore"}
      </button>

      {selectedObjectId && mode === "build" && (
        <button
          onClick={() => removeObject(selectedObjectId)}
          className="flex items-center gap-1.5 px-4 py-2 rounded-full bg-white border border-coral/30 text-coral hover:bg-coral/10 font-medium text-sm transition-all"
        >
          <span>🗑️</span>
          Delete
        </button>
      )}
    </div>
  );
}
