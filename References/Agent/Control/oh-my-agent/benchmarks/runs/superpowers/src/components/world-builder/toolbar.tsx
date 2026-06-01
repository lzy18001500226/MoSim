"use client";

import { useRouter } from "next/navigation";
import { useWorldStore } from "@/store/world-store";

export default function Toolbar() {
  const router = useRouter();
  const worldName = useWorldStore((s) => s.currentWorld?.name ?? "");
  const setWorldName = useWorldStore((s) => s.setWorldName);
  const saveCurrentWorld = useWorldStore((s) => s.saveCurrentWorld);
  const undo = useWorldStore((s) => s.undo);
  const redo = useWorldStore((s) => s.redo);
  const undoStack = useWorldStore((s) => s.undoStack);
  const redoStack = useWorldStore((s) => s.redoStack);
  const setPlaying = useWorldStore((s) => s.setPlaying);

  const handleSave = () => {
    saveCurrentWorld();
  };

  const handlePlay = () => {
    saveCurrentWorld();
    setPlaying(true);
    router.push("/play");
  };

  return (
    <div className="bg-white/90 backdrop-blur shadow-lg rounded-2xl px-4 py-2 flex items-center gap-3">
      <button
        onClick={() => router.push("/")}
        className="text-purple-500 hover:text-purple-700 font-bold text-lg"
        title="Home"
      >
        ✦
      </button>

      <input
        type="text"
        value={worldName}
        onChange={(e) => setWorldName(e.target.value)}
        className="bg-transparent font-bold text-purple-700 text-lg outline-none min-w-0 flex-shrink"
        placeholder="Name your world..."
      />

      <div className="flex-1" />

      <button
        onClick={undo}
        disabled={undoStack.length === 0}
        className="px-2 py-1 rounded-lg text-sm font-medium bg-gray-100 hover:bg-gray-200 disabled:opacity-30 transition-colors"
        title="Undo"
      >
        ↩
      </button>
      <button
        onClick={redo}
        disabled={redoStack.length === 0}
        className="px-2 py-1 rounded-lg text-sm font-medium bg-gray-100 hover:bg-gray-200 disabled:opacity-30 transition-colors"
        title="Redo"
      >
        ↪
      </button>

      <button
        onClick={handleSave}
        className="px-3 py-1.5 rounded-xl text-sm font-bold bg-purple-100 text-purple-600 hover:bg-purple-200 transition-colors"
      >
        Save
      </button>

      <button
        onClick={handlePlay}
        className="px-3 py-1.5 rounded-xl text-sm font-bold bg-green-500 text-white hover:bg-green-600 transition-colors"
      >
        Play ▶
      </button>
    </div>
  );
}
