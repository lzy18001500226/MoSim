"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import dynamic from "next/dynamic";
import { useWorldStore } from "@/store/world-store";
import { getReflectionPrompts } from "@/lib/ai-prompts";

const WorldCanvas = dynamic(() => import("@/components/three/world-canvas"), {
  ssr: false,
  loading: () => (
    <div className="flex-1 flex items-center justify-center bg-gradient-to-b from-sky-100 to-sky-200">
      <div className="text-purple-400 text-lg animate-pulse">Entering your world...</div>
    </div>
  ),
});

export default function PlayPage() {
  const router = useRouter();
  const currentWorld = useWorldStore((s) => s.currentWorld);
  const setPlaying = useWorldStore((s) => s.setPlaying);
  const [reflectionIndex, setReflectionIndex] = useState(0);
  const [showReflection, setShowReflection] = useState(false);

  const reflections = getReflectionPrompts();

  useEffect(() => {
    if (!currentWorld) {
      router.push("/");
    }
    return () => setPlaying(false);
  }, [currentWorld, router, setPlaying]);

  if (!currentWorld) return null;

  return (
    <div className="h-screen flex flex-col bg-gray-900 overflow-hidden relative">
      <div className="absolute top-4 left-4 right-4 z-10 flex items-center justify-between">
        <button
          onClick={() => {
            setPlaying(false);
            router.push("/builder");
          }}
          className="px-4 py-2 rounded-2xl bg-white/90 backdrop-blur text-purple-600 font-bold text-sm hover:bg-white shadow-lg transition-colors"
        >
          ← Back to Building
        </button>

        <div className="bg-white/90 backdrop-blur rounded-2xl px-4 py-2 shadow-lg">
          <h2 className="font-bold text-purple-700">{currentWorld.name}</h2>
        </div>

        <button
          onClick={() => {
            setShowReflection(!showReflection);
            setReflectionIndex(Math.floor(Math.random() * reflections.length));
          }}
          className="px-4 py-2 rounded-2xl bg-white/90 backdrop-blur text-purple-600 font-bold text-sm hover:bg-white shadow-lg transition-colors"
        >
          Think About It ✦
        </button>
      </div>

      {showReflection && (
        <div className="absolute bottom-24 left-1/2 -translate-x-1/2 z-10 bg-white/95 backdrop-blur rounded-2xl px-6 py-4 shadow-xl max-w-md text-center">
          <p className="text-purple-600 font-medium text-lg mb-2">
            {reflections[reflectionIndex]}
          </p>
          <button
            onClick={() => setReflectionIndex((i) => (i + 1) % reflections.length)}
            className="text-sm text-purple-400 hover:text-purple-600"
          >
            Another question →
          </button>
        </div>
      )}

      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-10 bg-white/80 backdrop-blur rounded-full px-4 py-2 text-sm text-gray-500">
        Click and drag to explore • Scroll to zoom
      </div>

      <div className="flex-1">
        <WorldCanvas isPlayMode />
      </div>
    </div>
  );
}
