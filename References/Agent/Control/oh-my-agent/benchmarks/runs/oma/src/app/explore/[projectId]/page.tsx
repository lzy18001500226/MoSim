"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import dynamic from "next/dynamic";
import Link from "next/link";
import type { WorldState } from "@/types/world";

const ExploreScene = dynamic(
  () =>
    import("@/features/explore/components/explore-scene").then(
      (m) => m.ExploreScene
    ),
  { ssr: false }
);

export default function ExplorePage() {
  const params = useParams();
  const projectId = params.projectId as string;
  const [worldState, setWorldState] = useState<WorldState | null>(null);
  const [title, setTitle] = useState("");
  const [error, setError] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch(`/api/projects/${projectId}`);
        if (!res.ok) throw new Error("Not found");
        const data = await res.json();
        setWorldState(data.worldData);
        setTitle(data.title);
      } catch {
        setError(true);
      }
    }
    load();
  }, [projectId]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center flex-col gap-4">
        <p className="text-xl">World not found</p>
        <Link
          href="/gallery"
          className="text-[var(--color-primary)] underline"
        >
          Back to Gallery
        </Link>
      </div>
    );
  }

  if (!worldState) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl animate-pulse">Loading world...</div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col">
      <header className="h-12 bg-[var(--color-surface)] border-b border-gray-200 flex items-center px-4 justify-between shrink-0">
        <div className="flex items-center gap-3">
          <Link
            href="/gallery"
            className="text-sm text-[var(--color-primary)] hover:underline"
            aria-label="Back to Gallery"
          >
            &larr; Back
          </Link>
          <span className="text-sm font-medium">{title}</span>
        </div>
        <span className="text-xs text-[var(--color-text-muted)]">
          Explore Mode
        </span>
      </header>
      <main className="flex-1">
        <ExploreScene worldState={worldState} />
      </main>
    </div>
  );
}
