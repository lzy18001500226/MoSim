"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useWorldStore } from "@/store/worldStore";
import { ENVIRONMENT_THEMES } from "@/lib/objects";
import type { EnvironmentTheme } from "@/types/world";

export default function OnboardingPage() {
  const [step, setStep] = useState(0);
  const [name, setName] = useState("");
  const [selectedEnv, setSelectedEnv] = useState<EnvironmentTheme>("meadow");
  const router = useRouter();
  const createWorld = useWorldStore((s) => s.createWorld);

  const handleStart = () => {
    const worldName = name.trim() || "My World";
    createWorld(worldName, selectedEnv);
    router.push("/builder");
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-gradient-to-b from-purple-100 via-blue-50 to-teal-100 p-4">
      <div className="w-full max-w-lg rounded-3xl bg-white/90 p-8 shadow-xl backdrop-blur">
        {step === 0 && (
          <div className="text-center">
            <div className="mb-6 text-6xl">👋</div>
            <h1 className="mb-4 text-3xl font-bold text-indigo-800">
              Hi there, Creator!
            </h1>
            <p className="mb-8 text-lg text-indigo-600">
              Ready to build your own world? Let&apos;s start with a name for it!
            </p>
            <input
              type="text"
              placeholder="My Amazing World..."
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="mb-6 w-full rounded-xl border-2 border-indigo-200 px-5 py-4 text-lg text-indigo-800 placeholder:text-indigo-300 focus:border-indigo-400 focus:outline-none"
              maxLength={30}
            />
            <button
              onClick={() => setStep(1)}
              className="w-full rounded-full bg-indigo-600 py-4 text-lg font-bold text-white shadow-md hover:bg-indigo-700 transition active:scale-95"
            >
              Next →
            </button>
          </div>
        )}

        {step === 1 && (
          <div className="text-center">
            <div className="mb-6 text-6xl">🎨</div>
            <h2 className="mb-4 text-2xl font-bold text-indigo-800">
              Pick Your World!
            </h2>
            <p className="mb-6 text-indigo-600">
              What kind of place do you want to build?
            </p>
            <div className="mb-8 grid grid-cols-2 gap-3">
              {ENVIRONMENT_THEMES.map((env) => (
                <button
                  key={env.id}
                  onClick={() => setSelectedEnv(env.id)}
                  className={`flex flex-col items-center gap-1 rounded-xl p-4 transition active:scale-95 ${
                    selectedEnv === env.id
                      ? "bg-indigo-100 ring-3 ring-indigo-500 shadow-md"
                      : "bg-gray-50 hover:bg-gray-100"
                  }`}
                >
                  <span className="text-3xl">{env.icon}</span>
                  <span className="text-sm font-medium text-indigo-700">
                    {env.label}
                  </span>
                </button>
              ))}
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => setStep(0)}
                className="flex-1 rounded-full bg-gray-100 py-4 font-bold text-indigo-600 hover:bg-gray-200 transition"
              >
                ← Back
              </button>
              <button
                onClick={handleStart}
                className="flex-1 rounded-full bg-indigo-600 py-4 font-bold text-white shadow-md hover:bg-indigo-700 transition active:scale-95"
              >
                Build! 🏗️
              </button>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
