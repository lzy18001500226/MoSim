"use client";

import { useWorldStore } from "@/stores/world-store";
import { useCallback } from "react";

const STORAGE_KEY = "worldcraft-projects";

export function ProjectActions() {
  const project = useWorldStore((s) => s.project);
  const loadProject = useWorldStore((s) => s.loadProject);
  const resetProject = useWorldStore((s) => s.resetProject);

  const handleSave = useCallback(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    const projects = stored ? JSON.parse(stored) : [];
    const existing = projects.findIndex((p: { id: string }) => p.id === project.id);

    const updated = { ...project, updatedAt: new Date().toISOString() };

    if (existing >= 0) {
      projects[existing] = updated;
    } else {
      projects.push(updated);
    }

    localStorage.setItem(STORAGE_KEY, JSON.stringify(projects));
  }, [project]);

  const handleNew = () => {
    resetProject();
  };

  return (
    <div className="flex items-center gap-1.5">
      <button
        onClick={handleSave}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-sky text-white text-sm font-medium hover:bg-sky/80 transition-colors"
      >
        <span>💾</span>
        Save
      </button>
      <button
        onClick={handleNew}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white border border-sky/20 text-text-muted text-sm font-medium hover:bg-sky/10 transition-colors"
      >
        <span>✨</span>
        New
      </button>
    </div>
  );
}
