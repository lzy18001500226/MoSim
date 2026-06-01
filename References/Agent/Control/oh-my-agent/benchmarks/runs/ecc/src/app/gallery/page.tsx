"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import type { WorldProject } from "@/types/world";

const STORAGE_KEY = "worldcraft-projects";

export default function GalleryPage() {
  const [projects, setProjects] = useState<WorldProject[]>([]);

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      setProjects(JSON.parse(stored));
    }
  }, []);

  return (
    <div className="min-h-screen bg-surface">
      <header className="flex items-center justify-between px-6 py-4 bg-white/80 backdrop-blur-sm border-b border-sky/10">
        <div className="flex items-center gap-3">
          <Link href="/" className="text-2xl hover:scale-110 transition-transform">
            🪄
          </Link>
          <h1 className="text-xl font-bold">My Worlds</h1>
        </div>
        <Link href="/builder">
          <Button variant="primary" size="sm">
            <span>🚀</span>
            New World
          </Button>
        </Link>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-8">
        {projects.length === 0 ? (
          <EmptyGallery />
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <ProjectCard key={project.id} project={project} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

function ProjectCard({ project }: { project: WorldProject }) {
  const themeEmoji: Record<string, string> = {
    meadow: "🌿",
    ocean: "🌊",
    space: "🚀",
    forest: "🌲",
    desert: "🏜️",
    snow: "❄️",
    night: "🌙",
    candy: "🍬",
  };

  return (
    <Card hoverable>
      <div className="aspect-video bg-gradient-to-br from-sky/20 to-lavender/20 flex items-center justify-center">
        <span className="text-5xl">{themeEmoji[project.theme] ?? "🌍"}</span>
      </div>
      <div className="p-4">
        <h3 className="font-semibold text-base mb-1">{project.name}</h3>
        <p className="text-xs text-text-muted">
          {project.objects.length} object{project.objects.length !== 1 ? "s" : ""} ·{" "}
          {new Date(project.updatedAt).toLocaleDateString()}
        </p>
        <div className="mt-3 flex gap-2">
          <Link href="/builder" className="flex-1">
            <button className="w-full py-1.5 rounded-lg bg-sky/10 text-sky text-xs font-medium hover:bg-sky/20 transition-colors">
              Open
            </button>
          </Link>
        </div>
      </div>
    </Card>
  );
}

function EmptyGallery() {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <span className="text-6xl mb-4 animate-float">🌌</span>
      <h2 className="text-xl font-bold mb-2">No worlds yet!</h2>
      <p className="text-text-muted mb-6 max-w-sm">
        You haven&apos;t created any worlds yet. Start building and your creations will appear here.
      </p>
      <Link href="/builder">
        <Button variant="primary">
          <span>🚀</span>
          Create Your First World
        </Button>
      </Link>
    </div>
  );
}
