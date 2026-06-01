'use client';

import { useWorldStore } from '@/store/useWorldStore';
import { useUserStore } from '@/store/useUserStore';
import { saveWorld } from '@/lib/storage';
import { useState } from 'react';
import Link from 'next/link';

export default function ToolBar() {
  const {
    worldName,
    setWorldName,
    undo,
    redo,
    undoStack,
    redoStack,
    mode,
    setMode,
    toggleAI,
    showAI,
    getWorld,
    objects,
  } = useWorldStore();
  const addWorldToUser = useUserStore((s) => s.addWorldToUser);
  const user = useUserStore((s) => s.user);
  const [saved, setSaved] = useState(false);
  const [editing, setEditing] = useState(false);

  const handleSave = () => {
    const world = getWorld();
    world.createdBy = user?.name || 'Anonymous';
    saveWorld(world);
    addWorldToUser(world.id);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="flex items-center justify-between px-4 py-2 bg-white/95 backdrop-blur-sm border-b border-border shadow-sm">
      <div className="flex items-center gap-3">
        <Link
          href="/"
          className="text-xl font-black bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent"
        >
          DreamWorld
        </Link>
        <div className="h-6 w-px bg-border" />
        {editing ? (
          <input
            autoFocus
            value={worldName}
            onChange={(e) => setWorldName(e.target.value)}
            onBlur={() => setEditing(false)}
            onKeyDown={(e) => e.key === 'Enter' && setEditing(false)}
            className="text-sm font-bold bg-primary/10 rounded-lg px-3 py-1 outline-none border-2 border-primary"
          />
        ) : (
          <button
            onClick={() => setEditing(true)}
            className="text-sm font-bold text-foreground/80 hover:text-primary transition-colors"
          >
            {worldName} ✏️
          </button>
        )}
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={undo}
          disabled={undoStack.length === 0}
          className="p-2 rounded-xl hover:bg-gray-100 disabled:opacity-30 transition-all text-lg"
          title="Undo"
        >
          ↩️
        </button>
        <button
          onClick={redo}
          disabled={redoStack.length === 0}
          className="p-2 rounded-xl hover:bg-gray-100 disabled:opacity-30 transition-all text-lg"
          title="Redo"
        >
          ↪️
        </button>

        <div className="h-6 w-px bg-border mx-1" />

        <button
          onClick={() => setMode(mode === 'build' ? 'explore' : 'build')}
          className={`px-4 py-1.5 rounded-full text-sm font-bold transition-all ${
            mode === 'explore'
              ? 'bg-secondary text-white shadow-md'
              : 'bg-gray-100 text-foreground/70 hover:bg-gray-200'
          }`}
        >
          {mode === 'build' ? '👁️ Explore' : '🔨 Build'}
        </button>

        <button
          onClick={toggleAI}
          className={`px-4 py-1.5 rounded-full text-sm font-bold transition-all ${
            showAI
              ? 'bg-accent text-white shadow-md'
              : 'bg-gray-100 text-foreground/70 hover:bg-gray-200'
          }`}
        >
          ✨ AI Buddy
        </button>

        <div className="h-6 w-px bg-border mx-1" />

        <span className="text-xs text-muted font-semibold">
          {objects.length} objects
        </span>

        <button
          onClick={handleSave}
          className="child-button child-button-primary !py-1.5 !px-5 !text-sm"
        >
          {saved ? '✅ Saved!' : '💾 Save'}
        </button>
      </div>
    </div>
  );
}
