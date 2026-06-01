"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import dynamic from "next/dynamic";
import { useWorldStore } from "@/store/world-store";
import Toolbar from "@/components/world-builder/toolbar";
import ObjectPalette from "@/components/world-builder/object-palette";
import PropertyPanel from "@/components/world-builder/property-panel";
import ThemePicker from "@/components/world-builder/theme-picker";
import AIPanel from "@/components/ai-companion/ai-panel";

const WorldCanvas = dynamic(() => import("@/components/three/world-canvas"), {
  ssr: false,
  loading: () => (
    <div className="flex-1 flex items-center justify-center bg-gradient-to-b from-sky-100 to-sky-200">
      <div className="text-purple-400 text-lg animate-pulse">Loading your world...</div>
    </div>
  ),
});

export default function BuilderPage() {
  const router = useRouter();
  const currentWorld = useWorldStore((s) => s.currentWorld);

  useEffect(() => {
    if (!currentWorld) {
      router.push("/");
    }
  }, [currentWorld, router]);

  if (!currentWorld) return null;

  return (
    <div className="h-screen flex flex-col bg-gray-100 overflow-hidden">
      <div className="p-2">
        <Toolbar />
      </div>

      <div className="flex-1 flex gap-2 p-2 pt-0 min-h-0">
        <div className="w-52 flex flex-col gap-2 overflow-y-auto flex-shrink-0">
          <ObjectPalette />
          <ThemePicker />
        </div>

        <div className="flex-1 rounded-2xl overflow-hidden shadow-lg">
          <WorldCanvas />
        </div>

        <div className="w-72 flex flex-col gap-2 overflow-y-auto flex-shrink-0">
          <PropertyPanel />
          <AIPanel />
        </div>
      </div>
    </div>
  );
}
