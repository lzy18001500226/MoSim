"use client";

import Link from "next/link";
import { useWorldStore } from "@/store/worldStore";
import { ENVIRONMENT_THEMES } from "@/lib/objects";

export default function GalleryPage() {
  const savedWorlds = useWorldStore((s) => s.savedWorlds);
  const loadWorld = useWorldStore((s) => s.loadWorld);
  const deleteWorld = useWorldStore((s) => s.deleteWorld);

  return (
    <main className="min-h-screen bg-gradient-to-b from-indigo-50 to-purple-50">
      <nav className="flex items-center justify-between border-b border-indigo-100 bg-white/80 px-8 py-4 backdrop-blur">
        <Link href="/" className="text-xl font-bold text-indigo-700">
          ✨ DreamWorlds
        </Link>
        <Link
          href="/onboarding"
          className="rounded-full bg-indigo-600 px-5 py-2 text-sm font-bold text-white hover:bg-indigo-700 transition"
        >
          + New World
        </Link>
      </nav>

      <div className="mx-auto max-w-6xl px-6 py-12">
        <h1 className="mb-2 text-4xl font-bold text-indigo-800">My Worlds</h1>
        <p className="mb-8 text-indigo-600">
          All the amazing worlds you&apos;ve created
        </p>

        {savedWorlds.length === 0 ? (
          <div className="flex flex-col items-center justify-center rounded-3xl bg-white/80 py-24 text-center shadow">
            <div className="mb-4 text-6xl">🌍</div>
            <h2 className="mb-2 text-2xl font-bold text-indigo-800">
              No worlds yet!
            </h2>
            <p className="mb-6 text-indigo-600">
              Create your first world and it will appear here
            </p>
            <Link
              href="/onboarding"
              className="rounded-full bg-indigo-600 px-8 py-3 font-bold text-white hover:bg-indigo-700 transition"
            >
              Create a World 🚀
            </Link>
          </div>
        ) : (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {savedWorlds.map((world) => {
              const env = ENVIRONMENT_THEMES.find(
                (e) => e.id === world.environment
              );
              return (
                <div
                  key={world.id}
                  className="group overflow-hidden rounded-2xl bg-white shadow-md hover:shadow-xl transition"
                >
                  <div
                    className="flex h-40 items-center justify-center text-6xl"
                    style={{ backgroundColor: env?.groundColor || "#90EE90" }}
                  >
                    {env?.icon || "🌍"}
                  </div>
                  <div className="p-5">
                    <h3 className="mb-1 text-lg font-bold text-indigo-800">
                      {world.name}
                    </h3>
                    <p className="mb-3 text-sm text-indigo-500">
                      {world.objects.length} objects • {env?.label}
                    </p>
                    <div className="flex gap-2">
                      <Link
                        href="/builder"
                        onClick={() => loadWorld(world.id)}
                        className="flex-1 rounded-lg bg-indigo-100 py-2 text-center text-sm font-medium text-indigo-700 hover:bg-indigo-200 transition"
                      >
                        Open ✏️
                      </Link>
                      <button
                        onClick={() => deleteWorld(world.id)}
                        className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-500 hover:bg-red-100 transition"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </main>
  );
}
