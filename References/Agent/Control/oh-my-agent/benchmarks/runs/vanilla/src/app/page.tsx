'use client';

import Link from 'next/link';
import { CHALLENGES } from '@/lib/ai';

const features = [
  {
    emoji: '🏗️',
    title: 'Build 3D Worlds',
    description: 'Place trees, houses, animals, and more to create your own magical 3D world!',
    color: 'from-purple-400 to-purple-600',
  },
  {
    emoji: '🤖',
    title: 'AI Creative Buddy',
    description: 'Your friendly AI helper gives you fun ideas and asks cool "what if" questions!',
    color: 'from-cyan-400 to-cyan-600',
  },
  {
    emoji: '🎮',
    title: 'Explore & Play',
    description: 'Walk through your creations, discover hidden surprises, and play in your world!',
    color: 'from-amber-400 to-amber-600',
  },
  {
    emoji: '🌟',
    title: 'Share & Inspire',
    description: 'Show your world to friends and family, and get inspired by what others have built!',
    color: 'from-emerald-400 to-emerald-600',
  },
];

const challengeEmojis: Record<string, string> = {
  meadow: '🌳',
  underwater: '🌊',
  space: '🚀',
  candy: '🍭',
  sunset: '🌅',
  night: '🌙',
  desert: '🏜️',
  snow: '❄️',
};

export default function Home() {
  const displayedChallenges = CHALLENGES.slice(0, 3);

  return (
    <div className="min-h-screen flex flex-col">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-[var(--primary)] via-purple-500 to-[var(--secondary)] px-6 py-20 md:py-32 text-center text-white">
        {/* Floating decorations */}
        <span className="animate-float absolute top-10 left-[10%] text-4xl md:text-5xl select-none" aria-hidden="true">✨</span>
        <span className="animate-bounce-soft absolute top-20 right-[12%] text-4xl md:text-5xl select-none" aria-hidden="true">🚀</span>
        <span className="animate-wiggle absolute bottom-16 left-[15%] text-4xl md:text-5xl select-none" aria-hidden="true">🎨</span>
        <span className="animate-float absolute bottom-24 right-[10%] text-4xl md:text-5xl select-none" style={{ animationDelay: '1s' }} aria-hidden="true">🌈</span>
        <span className="animate-bounce-soft absolute top-1/2 left-[5%] text-3xl select-none hidden md:block" style={{ animationDelay: '0.5s' }} aria-hidden="true">⭐</span>
        <span className="animate-wiggle absolute top-1/3 right-[5%] text-3xl select-none hidden md:block" style={{ animationDelay: '1.5s' }} aria-hidden="true">🎮</span>

        <div className="relative z-10 max-w-4xl mx-auto">
          <h1 className="text-5xl md:text-7xl font-black mb-4 drop-shadow-lg animate-slide-up">
            DreamWorld
          </h1>
          <p className="text-2xl md:text-3xl font-bold mb-8 drop-shadow-md animate-slide-up" style={{ animationDelay: '0.1s' }}>
            Build Your Imagination in 3D!
          </p>
          <p className="text-lg md:text-xl mb-12 max-w-2xl mx-auto opacity-90 animate-slide-up" style={{ animationDelay: '0.2s' }}>
            A magical creative playground where kids explore, build, and learn with the power of AI and 3D.
          </p>

          <div className="flex flex-col sm:flex-row gap-5 justify-center items-center animate-slide-up" style={{ animationDelay: '0.3s' }}>
            <Link href="/create" className="child-button child-button-accent text-xl px-10 py-5">
              🎨 Start Creating
            </Link>
            <Link href="/gallery" className="child-button child-button-secondary text-xl px-10 py-5">
              🖼️ Explore Gallery
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="px-6 py-16 md:py-24 max-w-6xl mx-auto w-full">
        <h2 className="text-3xl md:text-5xl font-extrabold text-center mb-4 text-[var(--foreground)]">
          What Can You Do?
        </h2>
        <p className="text-lg md:text-xl text-center text-[var(--muted)] mb-12 max-w-2xl mx-auto">
          So many ways to create, play, and learn!
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 md:gap-8">
          {features.map((feature) => (
            <div key={feature.title} className="child-card flex flex-col items-center text-center p-8">
              <span className="text-6xl mb-4">{feature.emoji}</span>
              <h3 className="text-2xl font-bold mb-3 text-[var(--foreground)]">
                {feature.title}
              </h3>
              <p className="text-lg text-[var(--muted)] leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Challenge Showcase Section */}
      <section className="px-6 py-16 md:py-24 bg-gradient-to-b from-purple-50 to-cyan-50">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl md:text-5xl font-extrabold text-center mb-4 text-[var(--foreground)]">
            Try a Challenge!
          </h2>
          <p className="text-lg md:text-xl text-center text-[var(--muted)] mb-12 max-w-2xl mx-auto">
            Pick a fun challenge and start building something amazing.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
            {displayedChallenges.map((challenge) => (
              <Link key={challenge.id} href="/create" className="block">
                <div className="child-card h-full flex flex-col items-center text-center p-8 cursor-pointer">
                  <span className="text-6xl mb-4">
                    {challengeEmojis[challenge.theme] || '🌟'}
                  </span>
                  <h3 className="text-2xl font-bold mb-3 text-[var(--foreground)]">
                    {challenge.title}
                  </h3>
                  <p className="text-lg text-[var(--muted)] leading-relaxed mb-4">
                    {challenge.description}
                  </p>
                  <span className="child-button child-button-primary mt-auto text-base px-6 py-3">
                    Try This Challenge
                  </span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="px-6 py-10 text-center bg-[var(--foreground)]">
        <p className="text-2xl font-extrabold text-white">
          DreamWorld
        </p>
        <p className="text-[var(--muted)] mt-2 text-base">
          Where imagination comes to life in 3D
        </p>
      </footer>
    </div>
  );
}
