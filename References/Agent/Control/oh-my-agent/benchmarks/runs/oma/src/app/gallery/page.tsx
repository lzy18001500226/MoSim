"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useChildStore } from "@/stores/child-store";
import { GalleryGrid } from "@/features/gallery/components/gallery-grid";

interface ProjectItem {
  id: string;
  title: string;
  createdAt: string;
  isSample?: boolean;
}

export default function GalleryPage() {
  const profile = useChildStore((s) => s.profile);
  const [projects, setProjects] = useState<ProjectItem[]>([]);
  const [tab, setTab] = useState<"mine" | "samples">("mine");

  useEffect(() => {
    async function load() {
      const params =
        tab === "mine" && profile ? `?childId=${profile.id}` : "";
      const res = await fetch(`/api/projects${params}`);
      const data = await res.json();
      setProjects(data);
    }
    load();
  }, [tab, profile]);

  return (
    <main className="min-h-screen bg-[var(--color-bg)]">
      <header className="bg-[var(--color-surface)] border-b border-gray-200 px-4 py-4">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link href="/" className="text-xl font-bold text-[var(--color-primary)]">
              🌍
            </Link>
            <h1 className="text-lg font-bold">Gallery</h1>
          </div>
          <Link
            href="/builder"
            className="px-4 py-2 text-sm font-bold text-white bg-[var(--color-primary)] rounded-full hover:scale-105 transition-transform"
          >
            + New World
          </Link>
        </div>
      </header>

      <div className="max-w-5xl mx-auto px-4 py-6">
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setTab("mine")}
            className={`px-4 py-2 text-sm font-medium rounded-full transition-colors ${
              tab === "mine"
                ? "bg-[var(--color-primary)] text-white"
                : "bg-gray-100 text-[var(--color-text-muted)] hover:bg-gray-200"
            }`}
          >
            My Worlds
          </button>
          <button
            onClick={() => setTab("samples")}
            className={`px-4 py-2 text-sm font-medium rounded-full transition-colors ${
              tab === "samples"
                ? "bg-[var(--color-primary)] text-white"
                : "bg-gray-100 text-[var(--color-text-muted)] hover:bg-gray-200"
            }`}
          >
            Sample Worlds
          </button>
        </div>

        <GalleryGrid projects={projects} />
      </div>
    </main>
  );
}
