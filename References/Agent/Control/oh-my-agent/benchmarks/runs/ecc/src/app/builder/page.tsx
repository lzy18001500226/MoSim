"use client";

import dynamic from "next/dynamic";
import { ObjectPalette } from "@/components/builder/ObjectPalette";
import { ThemeSelector } from "@/components/builder/ThemeSelector";
import { ColorPicker } from "@/components/builder/ColorPicker";
import { ToolBar } from "@/components/builder/ToolBar";
import { AiCompanionPanel } from "@/components/ai-companion/AiCompanionPanel";
import { ProjectActions } from "@/components/builder/ProjectActions";
import { useWorldStore } from "@/stores/world-store";

const WorldCanvas = dynamic(
  () => import("@/components/builder/WorldCanvas").then((m) => ({ default: m.WorldCanvas })),
  { ssr: false, loading: () => <CanvasLoader /> }
);

export default function BuilderPage() {
  const projectName = useWorldStore((s) => s.project.name);
  const setProjectName = useWorldStore((s) => s.setProjectName);

  return (
    <div className="flex h-screen bg-surface overflow-hidden">
      <aside className="w-56 bg-white/80 backdrop-blur-sm border-r border-sky/10 overflow-y-auto flex-shrink-0">
        <div className="p-3 border-b border-sky/10">
          <input
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
            className="w-full px-3 py-2 rounded-xl bg-surface border border-sky/20 text-sm font-semibold focus:outline-none focus:border-sky focus:ring-2 focus:ring-sky/20"
            placeholder="My World"
          />
        </div>
        <ObjectPalette />
      </aside>

      <main className="flex-1 flex flex-col min-w-0">
        <header className="flex items-center justify-between px-4 py-2 bg-white/60 backdrop-blur-sm border-b border-sky/10">
          <ThemeSelector />
          <div className="flex items-center gap-2">
            <ToolBar />
            <ProjectActions />
          </div>
        </header>

        <div className="flex-1 relative p-3">
          <WorldCanvas />
          <div className="absolute bottom-4 left-4 z-10">
            <ColorPicker />
          </div>
        </div>
      </main>

      <AiCompanionPanel />
    </div>
  );
}

function CanvasLoader() {
  return (
    <div className="w-full h-full flex items-center justify-center bg-sky/5 rounded-2xl">
      <div className="flex flex-col items-center gap-3">
        <span className="text-4xl animate-float">🌍</span>
        <p className="text-sm text-text-muted font-medium">Loading your world...</p>
      </div>
    </div>
  );
}
