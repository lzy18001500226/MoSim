"use client";

import { useCallback } from "react";
import dynamic from "next/dynamic";
import Link from "next/link";
import { useWorldStore } from "@/stores/world-store";
import { useChildStore } from "@/stores/child-store";
import { ToolPalette } from "@/features/builder/components/tool-palette";
import { PropertiesPanel } from "@/features/builder/components/properties-panel";
import { OBJECT_CATALOG } from "@/lib/constants";
import type { ObjectShape } from "@/types/world";

const SceneCanvas = dynamic(
  () => import("@/features/builder/components/scene-canvas").then((m) => m.SceneCanvas),
  { ssr: false }
);

const CompanionSidebar = dynamic(
  () => import("@/features/companion/components/companion-sidebar").then((m) => m.CompanionSidebar),
  { ssr: false }
);

export default function BuilderPage() {
  const addObject = useWorldStore((s) => s.addObject);
  const profile = useChildStore((s) => s.profile);

  const handleDrop = useCallback(
    (shape: ObjectShape, normalizedX: number, normalizedY: number) => {
      const catalogItem = OBJECT_CATALOG.find((item) => item.shape === shape);
      const worldX = normalizedX * 8;
      const worldZ = normalizedY * -8;

      addObject({
        id: crypto.randomUUID(),
        shape,
        label: catalogItem?.label || shape,
        position: { x: worldX, y: 0.5, z: worldZ },
        rotation: { x: 0, y: 0, z: 0 },
        scale: { x: 1, y: 1, z: 1 },
        color: catalogItem?.defaultColor || "#FF6B6B",
      });
    },
    [addObject]
  );

  return (
    <div className="h-screen flex flex-col">
      <header className="h-12 bg-[var(--color-surface)] border-b border-gray-200 flex items-center px-4 justify-between shrink-0">
        <div className="flex items-center gap-3">
          <Link href="/" className="text-lg font-bold text-[var(--color-primary)]">
            🌍
          </Link>
          <span className="text-sm font-medium">
            {profile?.name ? `${profile.name}'s World` : "My World"}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <Link
            href="/gallery"
            className="px-3 py-1.5 text-xs font-medium text-[var(--color-text-muted)] border border-gray-200 rounded-lg hover:bg-gray-50"
          >
            Gallery
          </Link>
          <SaveButton />
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        <ToolPalette />
        <div className="flex-1 flex flex-col relative">
          <SceneCanvas onDrop={handleDrop} />
        </div>
        <PropertiesPanel />
      </div>

      <CompanionSidebar />
    </div>
  );
}

function SaveButton() {
  const getWorldState = useWorldStore((s) => s.getWorldState);
  const profile = useChildStore((s) => s.profile);

  async function handleSave() {
    if (!profile) return;
    const state = getWorldState();
    if (state.objects.length === 0) return;

    await fetch("/api/projects", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title: `${profile.name}'s World`,
        worldData: state,
        childId: profile.id,
      }),
    });
    alert("World saved!");
  }

  return (
    <button
      onClick={handleSave}
      className="px-3 py-1.5 text-xs font-bold text-white bg-[var(--color-primary)] rounded-lg hover:opacity-90"
    >
      Save 💾
    </button>
  );
}
