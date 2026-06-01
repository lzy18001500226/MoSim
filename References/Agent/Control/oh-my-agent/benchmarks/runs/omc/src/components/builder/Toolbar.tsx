"use client";

import { useRouter } from "next/navigation";
import { useWorldStore } from "@/store/worldStore";
import { ENVIRONMENT_THEMES } from "@/lib/objects";
import type { EnvironmentTheme } from "@/types/world";

export function Toolbar() {
  const router = useRouter();
  const currentWorld = useWorldStore((s) => s.currentWorld);
  const isPlaying = useWorldStore((s) => s.isPlaying);
  const setPlaying = useWorldStore((s) => s.setPlaying);
  const saveWorld = useWorldStore((s) => s.saveWorld);
  const setEnvironment = useWorldStore((s) => s.setEnvironment);
  const undo = useWorldStore((s) => s.undo);
  const redo = useWorldStore((s) => s.redo);
  const undoStack = useWorldStore((s) => s.undoStack);
  const redoStack = useWorldStore((s) => s.redoStack);

  if (!currentWorld) return null;

  return (
    <div className="flex items-center justify-between border-b border-indigo-100 bg-white/95 px-4 py-2 backdrop-blur">
      <div className="flex items-center gap-3">
        <button
          onClick={() => router.push("/")}
          className="rounded-lg px-3 py-1.5 text-sm text-indigo-600 hover:bg-indigo-50 transition"
        >
          ← Home
        </button>
        <h2 className="text-lg font-bold text-indigo-800">
          {currentWorld.name}
        </h2>
        <select
          value={currentWorld.environment}
          onChange={(e) => setEnvironment(e.target.value as EnvironmentTheme)}
          className="rounded-lg border border-indigo-200 px-2 py-1 text-sm text-indigo-700 focus:outline-none"
        >
          {ENVIRONMENT_THEMES.map((env) => (
            <option key={env.id} value={env.id}>
              {env.icon} {env.label}
            </option>
          ))}
        </select>
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={undo}
          disabled={undoStack.length === 0}
          className="rounded-lg px-3 py-1.5 text-sm text-indigo-600 hover:bg-indigo-50 disabled:opacity-30 transition"
          title="Undo"
        >
          ↩️
        </button>
        <button
          onClick={redo}
          disabled={redoStack.length === 0}
          className="rounded-lg px-3 py-1.5 text-sm text-indigo-600 hover:bg-indigo-50 disabled:opacity-30 transition"
          title="Redo"
        >
          ↪️
        </button>

        <div className="mx-2 h-6 w-px bg-indigo-100" />

        <button
          onClick={() => setPlaying(!isPlaying)}
          className={`rounded-lg px-4 py-1.5 text-sm font-medium transition ${
            isPlaying
              ? "bg-amber-100 text-amber-700 hover:bg-amber-200"
              : "bg-green-100 text-green-700 hover:bg-green-200"
          }`}
        >
          {isPlaying ? "✏️ Edit" : "▶️ Explore"}
        </button>

        <button
          onClick={() => {
            saveWorld();
          }}
          className="rounded-lg bg-indigo-100 px-4 py-1.5 text-sm font-medium text-indigo-700 hover:bg-indigo-200 transition"
        >
          💾 Save
        </button>

        <button
          onClick={() => router.push("/gallery")}
          className="rounded-lg px-3 py-1.5 text-sm text-indigo-600 hover:bg-indigo-50 transition"
        >
          🖼️ Gallery
        </button>
      </div>
    </div>
  );
}
