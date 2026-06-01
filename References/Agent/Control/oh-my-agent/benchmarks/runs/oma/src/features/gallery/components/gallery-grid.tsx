"use client";

import { WorldCard } from "./world-card";

interface ProjectItem {
  id: string;
  title: string;
  createdAt: string;
  isSample?: boolean;
}

interface GalleryGridProps {
  projects: ProjectItem[];
}

export function GalleryGrid({ projects }: GalleryGridProps) {
  if (projects.length === 0) {
    return (
      <div className="text-center py-16">
        <p className="text-4xl mb-4">🎨</p>
        <p className="text-[var(--color-text-muted)]">No worlds yet. Go create one!</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {projects.map((project) => (
        <WorldCard
          key={project.id}
          id={project.id}
          title={project.title}
          createdAt={project.createdAt}
          isSample={project.isSample}
        />
      ))}
    </div>
  );
}
