"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { useWorldStore } from "@/stores/world-store";
import type { EnvironmentTheme } from "@/types/world";
import { ENVIRONMENT_THEMES } from "@/lib/object-catalog";

type Step = "welcome" | "name" | "theme";

const AVATARS = ["🧒", "👧", "🧒🏽", "👧🏾", "🧒🏻", "👧🏼", "🧙", "🦸", "🧚", "🤖", "🐱", "🐼"];

export function OnboardingFlow() {
  const [step, setStep] = useState<Step>("welcome");
  const [name, setName] = useState("");
  const [avatar, setAvatar] = useState("🧒");
  const router = useRouter();
  const setTheme = useWorldStore((s) => s.setTheme);
  const setProjectName = useWorldStore((s) => s.setProjectName);

  const handleThemeSelect = (theme: EnvironmentTheme) => {
    setTheme(theme);
    setProjectName(name ? `${name}'s World` : "My World");
    router.push("/builder");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-sky/10 via-lavender/5 to-sun/10 p-6">
      <div className="w-full max-w-md">
        {step === "welcome" && (
          <div className="flex flex-col items-center text-center space-y-6 animate-[fadeIn_0.3s_ease-out]">
            <span className="text-6xl animate-wiggle">🪄</span>
            <h1 className="text-3xl font-bold">
              Ready to build <span className="text-coral">amazing</span> worlds?
            </h1>
            <p className="text-text-muted text-lg">
              Let&apos;s get you started in just a few seconds!
            </p>
            <Button size="lg" onClick={() => setStep("name")}>
              Let&apos;s Go!
            </Button>
          </div>
        )}

        {step === "name" && (
          <div className="flex flex-col items-center text-center space-y-6 animate-[fadeIn_0.3s_ease-out]">
            <div className="flex flex-wrap justify-center gap-2 max-w-xs">
              {AVATARS.map((a) => (
                <button
                  key={a}
                  onClick={() => setAvatar(a)}
                  className={`w-12 h-12 rounded-full text-2xl flex items-center justify-center transition-all ${
                    avatar === a
                      ? "bg-sky/20 ring-2 ring-sky scale-110"
                      : "bg-white hover:bg-sky/10 border border-sky/10"
                  }`}
                >
                  {a}
                </button>
              ))}
            </div>

            <h2 className="text-2xl font-bold">
              <span className="text-3xl mr-2">{avatar}</span>
              What&apos;s your name?
            </h2>

            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Type your name..."
              className="w-full max-w-xs px-5 py-3 rounded-full text-center text-lg border-2 border-sky/30 focus:border-sky focus:ring-4 focus:ring-sky/20 focus:outline-none bg-white"
              autoFocus
            />

            <Button size="lg" onClick={() => setStep("theme")} disabled={!name.trim()}>
              Next →
            </Button>
          </div>
        )}

        {step === "theme" && (
          <div className="flex flex-col items-center text-center space-y-6 animate-[fadeIn_0.3s_ease-out]">
            <h2 className="text-2xl font-bold">
              Pick a world to start in, {name}!
            </h2>
            <p className="text-text-muted">You can always change it later.</p>

            <div className="grid grid-cols-2 gap-3 w-full">
              {ENVIRONMENT_THEMES.map((theme) => (
                <button
                  key={theme.id}
                  onClick={() => handleThemeSelect(theme.id)}
                  className="flex flex-col items-center gap-2 p-4 rounded-2xl bg-white border-2 border-transparent hover:border-sky hover:shadow-lg transition-all active:scale-95"
                >
                  <span className="text-3xl">{theme.emoji}</span>
                  <span className="font-medium text-sm">{theme.name}</span>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
