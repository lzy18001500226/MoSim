"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useWorldStore } from "@/store/worldStore";
import { Canvas3D } from "@/components/builder/Canvas3D";
import { ObjectPalette } from "@/components/builder/ObjectPalette";
import { AICompanion } from "@/components/builder/AICompanion";
import { Toolbar } from "@/components/builder/Toolbar";

export default function BuilderPage() {
  const router = useRouter();
  const currentWorld = useWorldStore((s) => s.currentWorld);
  const isPlaying = useWorldStore((s) => s.isPlaying);

  useEffect(() => {
    if (!currentWorld) {
      router.push("/onboarding");
    }
  }, [currentWorld, router]);

  if (!currentWorld) return null;

  return (
    <div className="flex h-screen flex-col">
      <Toolbar />
      <div className="flex flex-1 overflow-hidden">
        {!isPlaying && (
          <aside className="w-64 overflow-y-auto border-r border-indigo-100">
            <ObjectPalette />
          </aside>
        )}

        <main className="flex-1">
          <Canvas3D />
        </main>

        <aside className="w-72 overflow-hidden border-l border-indigo-100">
          <AICompanion />
        </aside>
      </div>
    </div>
  );
}
