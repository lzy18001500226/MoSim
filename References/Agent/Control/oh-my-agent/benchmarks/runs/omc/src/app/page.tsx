"use client";

import Link from "next/link";

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-indigo-100 via-purple-50 to-pink-100">
      <nav className="flex items-center justify-between px-8 py-6">
        <h1 className="text-2xl font-bold text-indigo-700">
          ✨ DreamWorlds
        </h1>
        <Link
          href="/gallery"
          className="rounded-full bg-white/80 px-5 py-2 text-sm font-medium text-indigo-600 shadow-sm hover:bg-white transition"
        >
          Gallery
        </Link>
      </nav>

      <section className="flex flex-col items-center justify-center px-4 pt-16 pb-24 text-center">
        <div className="mb-8 text-7xl animate-bounce">🌈</div>
        <h2 className="mb-4 text-5xl font-extrabold text-indigo-800 md:text-6xl">
          Build Your Own World
        </h2>
        <p className="mb-8 max-w-xl text-xl text-indigo-600">
          Imagine it. Build it. Explore it. Create amazing 3D worlds with your
          imagination and a friendly AI helper!
        </p>
        <Link
          href="/onboarding"
          className="rounded-full bg-indigo-600 px-10 py-5 text-xl font-bold text-white shadow-lg hover:bg-indigo-700 hover:scale-105 transition-all active:scale-95"
        >
          Start Creating! 🚀
        </Link>
      </section>

      <section className="mx-auto max-w-5xl px-4 pb-24">
        <div className="grid gap-6 md:grid-cols-3">
          <FeatureCard
            icon="🎨"
            title="Create"
            description="Drag and drop to build colorful 3D worlds with trees, houses, characters, and more!"
          />
          <FeatureCard
            icon="🤖"
            title="Imagine"
            description="Your AI friend asks fun questions to spark your creativity and help you think bigger!"
          />
          <FeatureCard
            icon="🌍"
            title="Explore"
            description="Walk through your world, click on things, and see your creations come to life!"
          />
        </div>
      </section>

      <section className="mx-auto max-w-4xl px-4 pb-24">
        <h3 className="mb-8 text-center text-3xl font-bold text-indigo-800">
          Creative Challenges
        </h3>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <ChallengeCard icon="📖" label="Story World" />
          <ChallengeCard icon="🌿" label="Habitat" />
          <ChallengeCard icon="💭" label="Dream World" />
          <ChallengeCard icon="💛" label="Emotion World" />
        </div>
      </section>

      <footer className="bg-indigo-900 py-8 text-center text-indigo-200">
        <p>Made with imagination ✨ A creative learning platform for young builders</p>
      </footer>
    </main>
  );
}

function FeatureCard({ icon, title, description }: { icon: string; title: string; description: string }) {
  return (
    <div className="rounded-2xl bg-white/80 p-8 text-center shadow-md hover:shadow-lg transition">
      <div className="mb-4 text-5xl">{icon}</div>
      <h3 className="mb-2 text-xl font-bold text-indigo-800">{title}</h3>
      <p className="text-indigo-600">{description}</p>
    </div>
  );
}

function ChallengeCard({ icon, label }: { icon: string; label: string }) {
  return (
    <Link
      href="/onboarding"
      className="flex flex-col items-center gap-2 rounded-xl bg-white/80 p-6 shadow hover:shadow-md hover:scale-105 transition-all"
    >
      <span className="text-4xl">{icon}</span>
      <span className="font-semibold text-indigo-700">{label}</span>
    </Link>
  );
}
