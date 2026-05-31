"use client";

import Link from "next/link";

interface HeroContentProps {
  t: (key: string) => string;
  onWatchDemo: () => void;
}

export function HeroContent({ t, onWatchDemo }: HeroContentProps) {
  return (
    <div className="text-center max-w-5xl mx-auto">
      <div className="inline-flex items-center gap-2 px-3 sm:px-4 py-1.5 rounded-full bg-[var(--azure-bg-high)] border border-[var(--azure-outline-variant)]/40 mb-6 sm:mb-10">
        <span className="relative flex h-2 w-2">
          <span className="absolute inline-flex h-full w-full rounded-full bg-[var(--azure-mint)] opacity-75 animate-ping" />
          <span className="relative inline-flex h-2 w-2 rounded-full bg-[var(--azure-mint)]" />
        </span>
        <span className="font-headline text-[10px] sm:text-[11px] font-bold tracking-[0.2em] uppercase text-[var(--azure-text-muted)]">
          {t("landing.hero.badge")}
        </span>
      </div>

      <h1 className="font-headline text-[2.25rem] leading-[1.05] sm:text-5xl md:text-6xl lg:text-7xl sm:leading-[0.95] font-bold mb-6 sm:mb-8">
        <span className="text-foreground">{t("landing.hero.slogan1")}</span>
        <br />
        <span className="azure-gradient-text">{t("landing.hero.slogan2")}</span>
      </h1>

      <p className="text-[var(--azure-text-muted)] text-base sm:text-lg md:text-xl max-w-2xl mx-auto mb-8 sm:mb-12 font-light leading-relaxed">
        {t("landing.hero.description")}
      </p>

      <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
        <Link href="/register" className="w-full sm:w-auto">
          <button className="w-full sm:w-auto px-10 py-4 azure-gradient-bg azure-cta-glow rounded-full font-headline text-xs sm:text-sm font-black uppercase tracking-[0.18em] transition-all transform hover:-translate-y-0.5">
            {t("landing.hero.getStartedFree")}
          </button>
        </Link>
        <button
          type="button"
          onClick={onWatchDemo}
          className="w-full sm:w-auto px-10 py-4 border border-[var(--azure-outline-variant)] hover:border-[var(--azure-cyan)]/60 text-foreground rounded-full font-headline text-xs sm:text-sm font-bold uppercase tracking-[0.18em] transition-all inline-flex items-center justify-center gap-2.5"
        >
          <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path d="M8 5v14l11-7z" />
          </svg>
          {t("landing.hero.viewDocs")}
        </button>
      </div>

      <p className="mt-6 text-sm text-[var(--azure-text-muted)]/70">
        {t("landing.hero.enterpriseNote")}{" "}
        <Link href="/demo" className="underline underline-offset-4 hover:text-[var(--azure-cyan)] transition-colors">
          {t("landing.hero.contactUs")}
        </Link>
      </p>
    </div>
  );
}

export default HeroContent;
