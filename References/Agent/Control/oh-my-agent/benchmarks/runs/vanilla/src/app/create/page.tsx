'use client';

import { useEffect } from 'react';
import { useUserStore } from '@/store/useUserStore';
import dynamic from 'next/dynamic';
import ToolBar from '@/components/builder/ToolBar';
import ObjectPalette from '@/components/builder/ObjectPalette';
import AICompanion from '@/components/builder/AICompanion';
import EnvironmentControls from '@/components/builder/EnvironmentControls';
import { useWorldStore } from '@/store/useWorldStore';

const Canvas3D = dynamic(() => import('@/components/builder/Canvas3D'), {
  ssr: false,
  loading: () => (
    <div className="flex-1 flex items-center justify-center bg-gradient-to-b from-sky-200 to-green-100">
      <div className="text-center animate-pulse-soft">
        <p className="text-6xl mb-4">🎨</p>
        <p className="text-xl font-bold text-foreground/60">Loading your canvas...</p>
      </div>
    </div>
  ),
});

export default function CreatePage() {
  const { loadUserFromStorage } = useUserStore();
  const showAI = useWorldStore((s) => s.showAI);
  const mode = useWorldStore((s) => s.mode);

  useEffect(() => {
    loadUserFromStorage();
  }, [loadUserFromStorage]);

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      <ToolBar />
      <div className="flex-1 flex overflow-hidden">
        {mode === 'build' && (
          <div className="w-48 flex-shrink-0 border-r border-border overflow-y-auto">
            <ObjectPalette />
          </div>
        )}
        <div className="flex-1 flex flex-col relative">
          <div className="flex-1">
            <Canvas3D />
          </div>
          {mode === 'build' && <EnvironmentControls />}
          {mode === 'explore' && (
            <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-white/90 backdrop-blur-sm rounded-2xl px-6 py-3 shadow-lg border border-border">
              <p className="text-sm font-bold text-foreground/70">
                🎮 Drag to look around. Scroll to zoom. Click objects to interact!
              </p>
            </div>
          )}
        </div>
        {showAI && (
          <div className="w-80 flex-shrink-0 overflow-hidden">
            <AICompanion />
          </div>
        )}
      </div>
    </div>
  );
}
