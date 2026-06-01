"use client";

import { useRouter } from "next/navigation";
import { useWorldStore } from "@/store/world-store";
import OnboardingFlow from "@/components/onboarding/onboarding-flow";
import { CHALLENGES } from "@/lib/challenges";
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

const CHALLENGE_COLORS: Record<string, string> = {
  storytelling: "from-blue-400 to-indigo-400",
  habitat: "from-cyan-400 to-teal-400",
  dream: "from-purple-400 to-pink-400",
  book: "from-amber-400 to-orange-400",
  emotion: "from-rose-400 to-pink-400",
};

export default function HomePage() {
  const router = useRouter();
  const hasOnboarded = useWorldStore((s) => s.hasOnboarded);
  const userName = useWorldStore((s) => s.userName);
  const savedWorlds = useWorldStore((s) => s.savedWorlds);
  const createNewWorld = useWorldStore((s) => s.createNewWorld);

  if (!hasOnboarded) {
    return <OnboardingFlow />;
  }

  const handleNewWorld = () => {
    createNewWorld(`${userName}'s New World`, "meadow");
    router.push("/builder");
  };

  const handleChallenge = (challenge: (typeof CHALLENGES)[0]) => {
    createNewWorld(challenge.title, challenge.theme ?? "meadow");
    router.push("/builder");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-100 via-pink-50 to-blue-100">
      <div className="max-w-4xl mx-auto p-6">
        <header className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              WonderWorld
            </h1>
            <p className="text-gray-500">
              Welcome back, <span className="font-bold text-purple-600">{userName}</span>!
            </p>
          </div>
          <button
            onClick={() => router.push("/gallery")}
            className="px-4 py-2 rounded-2xl bg-white/80 text-purple-600 font-bold text-sm hover:bg-white shadow-lg transition-colors"
          >
            My Worlds ({savedWorlds.length})
          </button>
        </header>

        <section className="mb-8">
          <button
            onClick={handleNewWorld}
            className="w-full p-6 rounded-3xl bg-gradient-to-r from-purple-500 to-pink-500 text-white hover:from-purple-600 hover:to-pink-600 transition-all shadow-lg group"
          >
            <div className="text-4xl mb-2 group-hover:scale-110 transition-transform inline-block">
              ✦
            </div>
            <h2 className="text-2xl font-bold">Start a New World</h2>
            <p className="text-white/80 mt-1">
              Open a blank canvas and let your imagination run free
            </p>
          </button>
        </section>

        <section className="mb-8">
          <h2 className="text-xl font-bold text-purple-700 mb-4">Creative Challenges</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {CHALLENGES.map((challenge) => (
              <button
                key={challenge.id}
                onClick={() => handleChallenge(challenge)}
                className="text-left p-4 rounded-2xl bg-white/80 backdrop-blur hover:bg-white hover:shadow-lg transition-all group"
              >
                <div
                  className={`w-10 h-10 rounded-xl bg-gradient-to-br ${
                    CHALLENGE_COLORS[challenge.category]
                  } flex items-center justify-center text-xl mb-2`}
                >
                  {challenge.theme ? THEME_EMOJIS[challenge.theme] : "✨"}
                </div>
                <h3 className="font-bold text-purple-700 group-hover:text-purple-800">
                  {challenge.title}
                </h3>
                <p className="text-sm text-gray-500 mt-0.5">{challenge.description}</p>
              </button>
            ))}
          </div>
        </section>

        {savedWorlds.length > 0 && (
          <section>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-purple-700">Recent Worlds</h2>
              <button
                onClick={() => router.push("/gallery")}
                className="text-sm text-purple-500 hover:text-purple-700 font-medium"
              >
                See all →
              </button>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {savedWorlds.slice(-3).reverse().map((world) => (
                <button
                  key={world.id}
                  onClick={() => {
                    useWorldStore.getState().loadWorld(world.id);
                    router.push("/builder");
                  }}
                  className="text-left p-4 rounded-2xl bg-white/80 backdrop-blur hover:bg-white hover:shadow-lg transition-all"
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xl">{THEME_EMOJIS[world.theme]}</span>
                    <h3 className="font-bold text-purple-700 truncate">{world.name}</h3>
                  </div>
                  <p className="text-xs text-gray-400">
                    {world.objects.length} objects • {new Date(world.updatedAt).toLocaleDateString()}
                  </p>
                </button>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
