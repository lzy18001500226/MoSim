'use client';

import { useEffect, useState } from 'react';
import { World } from '@/types';
import { loadAllWorlds, deleteWorld } from '@/lib/storage';
import { useWorldStore } from '@/store/useWorldStore';
import { ENVIRONMENT_THEMES } from '@/lib/objects';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function GalleryPage() {
  const [worlds, setWorlds] = useState<World[]>([]);
  const [loaded, setLoaded] = useState(false);
  const router = useRouter();
  const loadWorld = useWorldStore((s) => s.loadWorld);

  useEffect(() => {
    setWorlds(loadAllWorlds());
    setLoaded(true);
  }, []);

  const handleOpen = (world: World) => {
    loadWorld(world);
    router.push('/create');
  };

  const handleDelete = (id: string) => {
    deleteWorld(id);
    setWorlds(loadAllWorlds());
  };

  const getThemeEmoji = (theme: string) => {
    return ENVIRONMENT_THEMES.find((t) => t.id === theme)?.emoji || '🌍';
  };

  const getThemeGradient = (theme: string) => {
    const gradients: Record<string, string> = {
      meadow: 'from-green-300 to-blue-300',
      night: 'from-indigo-800 to-purple-900',
      underwater: 'from-cyan-400 to-blue-600',
      space: 'from-gray-800 to-black',
      desert: 'from-yellow-300 to-orange-400',
      snow: 'from-blue-100 to-white',
      sunset: 'from-orange-300 to-pink-400',
      candy: 'from-pink-300 to-purple-300',
    };
    return gradients[theme] || 'from-gray-200 to-gray-300';
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-purple-50">
      <header className="bg-white/80 backdrop-blur-sm border-b border-border sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link
            href="/"
            className="text-2xl font-black bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent"
          >
            DreamWorld
          </Link>
          <div className="flex gap-3">
            <Link href="/create" className="child-button child-button-primary !py-2 !px-6 !text-sm">
              + New World
            </Link>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-10">
        <div className="text-center mb-10">
          <h1 className="text-4xl font-black text-foreground mb-2">
            🎨 My Gallery
          </h1>
          <p className="text-lg text-muted font-semibold">
            All the amazing worlds you&apos;ve created
          </p>
        </div>

        {!loaded ? (
          <div className="text-center py-20">
            <p className="text-4xl animate-bounce-soft">🎨</p>
            <p className="text-muted font-bold mt-4">Loading...</p>
          </div>
        ) : worlds.length === 0 ? (
          <div className="text-center py-20">
            <p className="text-6xl mb-4">🌍</p>
            <h2 className="text-2xl font-bold text-foreground/70 mb-2">No worlds yet!</h2>
            <p className="text-muted font-semibold mb-6">
              Start creating your first 3D world
            </p>
            <Link href="/create" className="child-button child-button-primary">
              Start Creating
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {worlds.map((world) => (
              <div key={world.id} className="child-card group cursor-pointer" onClick={() => handleOpen(world)}>
                <div
                  className={`h-40 rounded-xl bg-gradient-to-br ${getThemeGradient(
                    world.theme
                  )} flex items-center justify-center mb-4 relative overflow-hidden`}
                >
                  <span className="text-5xl">{getThemeEmoji(world.theme)}</span>
                  <div className="absolute bottom-2 right-2 bg-white/80 rounded-full px-2 py-0.5 text-xs font-bold text-foreground/60">
                    {world.objects.length} objects
                  </div>
                </div>
                <h3 className="text-lg font-bold text-foreground mb-1">{world.name}</h3>
                <div className="flex items-center justify-between">
                  <p className="text-xs text-muted font-semibold">
                    by {world.createdBy || 'Anonymous'} &middot;{' '}
                    {new Date(world.updatedAt).toLocaleDateString()}
                  </p>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDelete(world.id);
                    }}
                    className="opacity-0 group-hover:opacity-100 text-xs px-2 py-1 bg-danger/10 text-danger rounded-full font-bold hover:bg-danger/20 transition-all"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
