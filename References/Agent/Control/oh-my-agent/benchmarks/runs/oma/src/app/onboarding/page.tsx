"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useChildStore } from "@/stores/child-store";
import { AVATAR_OPTIONS } from "@/lib/constants";
import { cn } from "@/lib/utils";

export default function OnboardingPage() {
  const router = useRouter();
  const setProfile = useChildStore((s) => s.setProfile);
  const [name, setName] = useState("");
  const [selectedAvatar, setSelectedAvatar] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canContinue = name.trim().length > 0 && selectedAvatar !== null;

  async function handleStart() {
    if (!canContinue || isSubmitting) return;

    setIsSubmitting(true);
    setError(null);

    try {
      const res = await fetch("/api/children", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: name.trim(), avatarId: selectedAvatar }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error((data as { error?: string }).error ?? "Something went wrong");
      }

      const child = (await res.json()) as { id: string; name: string; avatarId: string };

      setProfile({ id: child.id, name: child.name, avatarId: child.avatarId });
      router.push("/builder");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong. Please try again!");
      setIsSubmitting(false);
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center px-4 py-8">
      <div className="w-full max-w-md space-y-8 text-center">
        <header>
          <h1 className="text-3xl font-bold mb-2">Welcome, Creator!</h1>
          <p style={{ color: "var(--color-text-muted)" }}>Tell us a little about you</p>
        </header>

        {/* Name Input */}
        <div className="space-y-2">
          <label htmlFor="name" className="block text-left font-medium text-sm">
            What should we call you?
          </label>
          <input
            id="name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Your name..."
            maxLength={20}
            autoComplete="given-name"
            className="w-full px-4 py-3 text-lg rounded-xl border-2 border-gray-200 transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2"
            style={
              {
                "--tw-ring-color": "var(--color-primary)",
              } as React.CSSProperties
            }
            onFocus={(e) => {
              e.currentTarget.style.borderColor = "var(--color-primary)";
            }}
            onBlur={(e) => {
              e.currentTarget.style.borderColor = name.trim() ? "var(--color-primary)" : "";
            }}
            aria-required="true"
          />
        </div>

        {/* Avatar Picker */}
        <div className="space-y-2">
          <p className="text-left font-medium text-sm" id="avatar-group-label">
            Pick your avatar
          </p>
          <div
            className="grid grid-cols-3 gap-3"
            role="group"
            aria-labelledby="avatar-group-label"
          >
            {AVATAR_OPTIONS.map((avatar) => (
              <button
                key={avatar.id}
                type="button"
                onClick={() => setSelectedAvatar(avatar.id)}
                aria-label={avatar.label}
                aria-pressed={selectedAvatar === avatar.id}
                className={cn(
                  "p-4 text-3xl rounded-xl border-2 transition-all hover:scale-105",
                  "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2",
                  selectedAvatar === avatar.id
                    ? "scale-105"
                    : "border-gray-200 hover:border-gray-300"
                )}
                style={
                  selectedAvatar === avatar.id
                    ? ({
                        borderColor: "var(--color-primary)",
                        backgroundColor: "color-mix(in srgb, var(--color-primary) 10%, transparent)",
                      } as React.CSSProperties)
                    : undefined
                }
              >
                {avatar.emoji}
              </button>
            ))}
          </div>
        </div>

        {/* Error message */}
        {error && (
          <p role="alert" className="text-sm font-medium" style={{ color: "#E74C3C" }}>
            {error}
          </p>
        )}

        {/* Start Button */}
        <button
          type="button"
          onClick={handleStart}
          disabled={!canContinue || isSubmitting}
          className="w-full py-4 text-lg font-bold text-white rounded-full disabled:opacity-40 disabled:cursor-not-allowed hover:scale-105 transition-transform shadow-lg focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-offset-2"
          style={
            {
              backgroundColor: "var(--color-primary)",
              "--tw-ring-color": "var(--color-primary)",
            } as React.CSSProperties
          }
          aria-disabled={!canContinue || isSubmitting}
        >
          {isSubmitting ? "Getting ready..." : "Let's Build! 🚀"}
        </button>
      </div>
    </main>
  );
}
