"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useWorldStore } from "@/store/world-store";
import type { EnvironmentTheme } from "@/types/world";

const THEMES: { theme: EnvironmentTheme; label: string; emoji: string; color: string }[] = [
  { theme: "meadow", label: "Sunny Meadow", emoji: "🌿", color: "from-green-400 to-emerald-400" },
  { theme: "ocean", label: "Deep Ocean", emoji: "🌊", color: "from-blue-400 to-cyan-400" },
  { theme: "space", label: "Outer Space", emoji: "🚀", color: "from-indigo-500 to-purple-500" },
  { theme: "forest", label: "Magic Forest", emoji: "🌲", color: "from-green-500 to-lime-400" },
  { theme: "snow", label: "Snowy Land", emoji: "❄️", color: "from-blue-200 to-sky-300" },
  { theme: "candy", label: "Candy World", emoji: "🍬", color: "from-pink-400 to-rose-400" },
  { theme: "desert", label: "Sandy Desert", emoji: "🏜️", color: "from-amber-400 to-orange-400" },
  { theme: "volcano", label: "Volcano Land", emoji: "🌋", color: "from-red-500 to-orange-500" },
];

export default function OnboardingFlow() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [name, setName] = useState("");
  const [worldName, setWorldName] = useState("");
  const [selectedTheme, setSelectedTheme] = useState<EnvironmentTheme>("meadow");
  const { setUserName, setOnboarded, createNewWorld } = useWorldStore();

  const handleStart = () => {
    if (!name.trim()) return;
    setUserName(name.trim());
    setStep(1);
  };

  const handleCreateWorld = () => {
    const finalWorldName = worldName.trim() || `${name}'s World`;
    setOnboarded();
    createNewWorld(finalWorldName, selectedTheme);
    router.push("/builder");
  };

  if (step === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-100 via-pink-50 to-blue-100 flex items-center justify-center p-4">
        <div className="bg-white/80 backdrop-blur rounded-3xl shadow-xl p-8 max-w-md w-full text-center space-y-6">
          <div className="text-6xl">✦</div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
            Welcome to WonderWorld!
          </h1>
          <p className="text-gray-600 text-lg">
            A place where your imagination comes alive!
          </p>
          <div className="space-y-3">
            <label className="text-sm font-medium text-purple-600 block text-left">
              What is your name?
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleStart()}
              placeholder="Type your name here..."
              className="w-full px-4 py-3 rounded-2xl bg-purple-50 border-2 border-purple-200 focus:border-purple-400 outline-none text-lg text-center"
              autoFocus
              maxLength={30}
            />
            <button
              onClick={handleStart}
              disabled={!name.trim()}
              className="w-full py-3 rounded-2xl bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold text-lg hover:from-purple-600 hover:to-pink-600 disabled:opacity-40 transition-all"
            >
              Let&apos;s Go!
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-100 via-pink-50 to-blue-100 flex items-center justify-center p-4">
      <div className="bg-white/80 backdrop-blur rounded-3xl shadow-xl p-8 max-w-lg w-full space-y-6">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-purple-700">
            Hi {name}! Let&apos;s build a world!
          </h2>
          <p className="text-gray-500 mt-1">Choose a name and pick a theme</p>
        </div>

        <div>
          <label className="text-sm font-medium text-purple-600 block mb-1">
            Name your world
          </label>
          <input
            type="text"
            value={worldName}
            onChange={(e) => setWorldName(e.target.value)}
            placeholder={`${name}'s World`}
            className="w-full px-4 py-3 rounded-2xl bg-purple-50 border-2 border-purple-200 focus:border-purple-400 outline-none text-lg"
            maxLength={40}
          />
        </div>

        <div>
          <label className="text-sm font-medium text-purple-600 block mb-2">
            Pick a world theme
          </label>
          <div className="grid grid-cols-2 gap-2">
            {THEMES.map((t) => (
              <button
                key={t.theme}
                onClick={() => setSelectedTheme(t.theme)}
                className={`flex items-center gap-3 p-3 rounded-2xl transition-all ${
                  selectedTheme === t.theme
                    ? "ring-3 ring-purple-400 bg-purple-50 scale-[1.02]"
                    : "bg-white hover:bg-gray-50"
                }`}
              >
                <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${t.color} flex items-center justify-center text-xl`}>
                  {t.emoji}
                </div>
                <span className="font-medium text-gray-700 text-sm">{t.label}</span>
              </button>
            ))}
          </div>
        </div>

        <button
          onClick={handleCreateWorld}
          className="w-full py-3 rounded-2xl bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold text-lg hover:from-purple-600 hover:to-pink-600 transition-all"
        >
          Start Building!
        </button>
      </div>
    </div>
  );
}
