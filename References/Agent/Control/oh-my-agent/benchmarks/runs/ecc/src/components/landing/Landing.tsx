"use client";

import Link from "next/link";
import { Button } from "@/components/ui/Button";

export function Landing() {
  return (
    <main className="flex flex-col items-center min-h-screen overflow-hidden">
      <section className="relative flex flex-col items-center justify-center min-h-screen w-full px-6 text-center">
        <div className="absolute inset-0 bg-gradient-to-b from-sky/20 via-lavender/10 to-sun/10 -z-10" />

        <div className="absolute top-[10%] left-[10%] w-20 h-20 rounded-full bg-sun/40 animate-float" />
        <div className="absolute top-[20%] right-[15%] w-14 h-14 rounded-2xl bg-coral/30 animate-float [animation-delay:1s]" />
        <div className="absolute bottom-[25%] left-[20%] w-16 h-16 rounded-full bg-lavender/40 animate-float [animation-delay:0.5s]" />
        <div className="absolute bottom-[15%] right-[10%] w-12 h-12 rounded-xl bg-grass/30 animate-float [animation-delay:1.5s]" />

        <div className="animate-wiggle mb-6">
          <span className="text-6xl" role="img" aria-label="magic wand">
            🪄
          </span>
        </div>

        <h1
          className="font-bold tracking-tight leading-tight mb-4"
          style={{ fontSize: "var(--text-hero)" }}
        >
          <span className="text-sky">Build</span>{" "}
          <span className="text-coral">Your</span>{" "}
          <span className="text-grass">World</span>
        </h1>

        <p
          className="max-w-md mx-auto text-text-muted mb-10 leading-relaxed"
          style={{ fontSize: "var(--text-body)" }}
        >
          Imagine, create, and explore amazing 3D worlds. Your ideas become real places you can walk through!
        </p>

        <div className="flex flex-col sm:flex-row gap-4">
          <Link href="/onboarding">
            <Button size="lg" variant="primary">
              <span role="img" aria-hidden="true">🚀</span>
              Start Creating
            </Button>
          </Link>
          <Link href="/gallery">
            <Button size="lg" variant="ghost">
              <span role="img" aria-hidden="true">🌍</span>
              Explore Worlds
            </Button>
          </Link>
        </div>

        <div className="mt-16 grid grid-cols-1 sm:grid-cols-3 gap-6 max-w-2xl w-full">
          <FeatureCard
            emoji="🎨"
            title="Create"
            description="Drag and drop to build anything you imagine"
          />
          <FeatureCard
            emoji="🤖"
            title="AI Friend"
            description="A creative buddy helps you think of new ideas"
          />
          <FeatureCard
            emoji="🏃"
            title="Explore"
            description="Walk through your world and see it come alive"
          />
        </div>
      </section>
    </main>
  );
}

function FeatureCard({ emoji, title, description }: { emoji: string; title: string; description: string }) {
  return (
    <div className="bg-white/70 backdrop-blur-sm rounded-2xl p-6 border border-white shadow-sm hover:shadow-md transition-shadow">
      <span className="text-3xl block mb-2" role="img" aria-hidden="true">
        {emoji}
      </span>
      <h3 className="font-semibold text-lg mb-1">{title}</h3>
      <p className="text-sm text-text-muted">{description}</p>
    </div>
  );
}
