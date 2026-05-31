"use client";

import Link from "next/link";
import { useTranslations } from "next-intl";

export function FinalCTA() {
  const t = useTranslations();

  return (
    <section className="py-32 relative overflow-hidden bg-[var(--azure-bg-deeper)]">
      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[900px] h-[500px] bg-[var(--azure-cyan)]/15 blur-[140px] rounded-full azure-orb pointer-events-none" />
      <div
        className="absolute top-1/4 right-1/4 w-[300px] h-[300px] bg-[var(--azure-mint)]/8 blur-[100px] rounded-full azure-orb pointer-events-none"
        style={{ animationDelay: "2s" }}
      />

      <div
        className="absolute inset-0 opacity-[0.04] pointer-events-none"
        style={{
          backgroundImage:
            "linear-gradient(var(--azure-cyan) 1px, transparent 1px), linear-gradient(90deg, var(--azure-cyan) 1px, transparent 1px)",
          backgroundSize: "60px 60px",
        }}
      />

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center max-w-3xl mx-auto">
          <h2 className="font-headline text-4xl md:text-6xl font-bold leading-[1.05] mb-6">
            {t("landing.finalCta.title1")}
            <br />
            <span className="azure-gradient-text">{t("landing.finalCta.title2")}</span>
          </h2>

          <p className="text-[var(--azure-text-muted)] text-lg mb-10 font-light">
            {t("landing.finalCta.description")}
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/register" className="w-full sm:w-auto">
              <button className="w-full sm:w-auto px-10 py-4 azure-gradient-bg azure-cta-glow rounded-full font-headline text-xs sm:text-sm font-black uppercase tracking-[0.18em] transition-all hover:-translate-y-0.5">
                {t("landing.finalCta.getStartedFree")}
              </button>
            </Link>
            <Link href="/login" className="w-full sm:w-auto">
              <button className="w-full sm:w-auto px-10 py-4 border border-[var(--azure-outline-variant)] hover:border-[var(--azure-cyan)]/60 text-foreground rounded-full font-headline text-xs sm:text-sm font-bold uppercase tracking-[0.18em] transition-all">
                {t("landing.finalCta.signInConsole")}
              </button>
            </Link>
          </div>

          <p className="mt-6 text-sm text-[var(--azure-text-muted)]/70">
            {t("landing.finalCta.enterpriseNote")}{" "}
            <Link href="/demo" className="underline underline-offset-4 hover:text-[var(--azure-cyan)] transition-colors">
              {t("landing.finalCta.contactUs")}
            </Link>
          </p>

          <div className="mt-12 flex flex-wrap justify-center gap-x-8 gap-y-3 text-sm text-[var(--azure-text-muted)]">
            <div className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-[var(--azure-mint)]" />
              {t("landing.finalCta.freeTier")}
            </div>
            <div className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-[var(--azure-mint)]" />
              {t("landing.finalCta.noCreditCard")}
            </div>
            <div className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-[var(--azure-mint)]" />
              {t("landing.finalCta.selfHostedOption")}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
