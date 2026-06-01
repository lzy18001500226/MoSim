"use client";

import { useRouter } from "next/navigation";
import { useWorldStore } from "@/store/world-store";
import type { EnvironmentTheme } from "@/types/world";

const THEME_EMOJIS: Record<EnvironmentTheme, string> = {
  meadow: "🌿",
  desert: "🏜️",
  ocean: "🌊",
  space: "🚀",
  forest: "🌲",
  snow: "❄️",
  candy: "🍬",
  volcano: "🌋",
};

const THEME_GRADIENTS: Record<EnvironmentTheme, string> = {
  meadow: "from-green-400 to-emerald-300",
  desert: "from-amber-400 to-orange-300",
  ocean: "from-blue-400 to-cyan-300",
  space: "from-indigo-500 to-purple-400",
  forest: "from-green-500 to-lime-300",
  snow: "from-blue-200 to-sky-200",
  candy: "from-pink-400 to-rose-300",
  volcano: "from-red-500 to-orange-400",
};

export default function GalleryPage() {
  const router = useRouter();
  const savedWorlds = useWorldStore((s) => s.savedWorlds);
  const loadWorld = useWorldStore((s) => s.loadWorld);
  const deleteWorld = useWorldStore((s) => s.deleteWorld);
  const userName = useWorldStore((s) => s.userName);

  const handleOpen = (id: string) => {
    loadWorld(id);
    router.push("/builder");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-100 via-pink-50 to-blue-100 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              My Worlds
            </h1>
            <p className="text-gray-500 mt-1">
              {userName ? `${userName}'s` : "Your"} amazing creations
            </p>
          </div>
          <button
            onClick={() => router.push("/")}
            className="px-4 py-2 rounded-2xl bg-white/80 text-purple-600 font-bold text-sm hover:bg-white shadow-lg transition-colors"
          >
            ← Home
          </button>
        </div>

        {savedWorlds.length === 0 ? (
          <div className="text-center py-20">
            <div className="text-6xl mb-4">🌍</div>
            <h2 className="text-xl font-bold text-gray-400 mb-2">No worlds yet!</h2>
            <p className="text-gray-400 mb-6">Start building to see your creations here</p>
            <button
              onClick={() => router.push("/")}
              className="px-6 py-3 rounded-2xl bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold hover:from-purple-600 hover:to-pink-600 transition-all"
            >
              Create Your First World
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {savedWorlds.map((world) => (
              <div
                key={world.id}
                className="bg-white/80 backdrop-blur rounded-2xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow group"
              >
                <div
                  className={`h-32 bg-gradient-to-br ${THEME_GRADIENTS[world.theme]} flex items-center justify-center relative`}
                >
                  <span className="text-5xl">{THEME_EMOJIS[world.theme]}</span>
                  <div className="absolute bottom-2 right-2 bg-white/80 rounded-full px-2 py-0.5 text-xs text-gray-600">
                    {world.objects.length} objects
                  </div>
                </div>
                <div className="p-4">
                  <h3 className="font-bold text-purple-700 text-lg truncate">{world.name}</h3>
                  <p className="text-xs text-gray-400 mt-0.5">
                    {new Date(world.updatedAt).toLocaleDateString()}
                  </p>
                  <div className="flex gap-2 mt-3">
                    <button
                      onClick={() => handleOpen(world.id)}
                      className="flex-1 py-2 rounded-xl bg-purple-500 text-white font-bold text-sm hover:bg-purple-600 transition-colors"
                    >
                      Open
                    </button>
                    <button
                      onClick={() => {
                        if (confirm("Delete this world?")) {
                          deleteWorld(world.id);
                        }
                      }}
                      className="px-3 py-2 rounded-xl bg-gray-100 text-gray-400 text-sm hover:bg-red-50 hover:text-red-400 transition-colors"
                    >
                      ✕
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
