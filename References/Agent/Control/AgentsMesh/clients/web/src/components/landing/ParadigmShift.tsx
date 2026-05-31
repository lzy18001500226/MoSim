"use client";

import { useTranslations } from "next-intl";

export function ParadigmShift() {
  const t = useTranslations();

  const beforeItems = [
    t("landing.paradigmShift.before.items.0"),
    t("landing.paradigmShift.before.items.1"),
    t("landing.paradigmShift.before.items.2"),
    t("landing.paradigmShift.before.items.3"),
  ];

  const afterItems = [
    t("landing.paradigmShift.after.items.0"),
    t("landing.paradigmShift.after.items.1"),
    t("landing.paradigmShift.after.items.2"),
    t("landing.paradigmShift.after.items.3"),
  ];

  return (
    <section className="py-32 relative overflow-hidden" id="paradigm-shift">
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] bg-[var(--azure-cyan)]/5 blur-[150px] rounded-full pointer-events-none" />

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center mb-20">
          <h2 className="font-headline text-4xl md:text-5xl font-bold mb-6 max-w-3xl mx-auto leading-tight">
            {t("landing.paradigmShift.title")}{" "}
            <span className="azure-gradient-text">{t("landing.paradigmShift.titleHighlight")}</span>
          </h2>
        </div>

        <div className="max-w-5xl mx-auto grid md:grid-cols-2 gap-8 mb-16">
          <div className="azure-glass p-8 rounded-3xl border border-white/5">
            <h3 className="font-headline text-[10px] font-black uppercase tracking-[0.25em] text-[var(--azure-text-muted)] mb-8">
              {t("landing.paradigmShift.before.label")}
            </h3>
            <ul className="space-y-5">
              {beforeItems.map((item) => (
                <li key={item} className="flex items-start gap-3">
                  <div className="mt-1.5 w-1.5 h-1.5 rounded-full bg-[var(--azure-text-muted)]/50 flex-shrink-0" />
                  <span className="text-[var(--azure-text-muted)] leading-relaxed">{item}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="azure-glass p-8 rounded-3xl border border-[var(--azure-cyan)]/20 azure-glow-cyan-lg">
            <h3 className="font-headline text-[10px] font-black uppercase tracking-[0.25em] text-[var(--azure-cyan)] mb-8">
              {t("landing.paradigmShift.after.label")}
            </h3>
            <ul className="space-y-5">
              {afterItems.map((item) => (
                <li key={item} className="flex items-start gap-3">
                  <div className="mt-2 w-1.5 h-1.5 rounded-full bg-[var(--azure-mint)] flex-shrink-0" />
                  <span className="text-foreground leading-relaxed">{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="text-center">
          <div className="inline-flex items-center gap-3 max-w-3xl mx-auto">
            <span className="hidden sm:block h-px w-12 bg-gradient-to-r from-transparent to-[var(--azure-cyan)]/40" />
            <p className="font-headline text-lg sm:text-xl md:text-2xl font-medium text-foreground/90 tracking-tight">
              {t("landing.paradigmShift.punchline")}
            </p>
            <span className="hidden sm:block h-px w-12 bg-gradient-to-l from-transparent to-[var(--azure-cyan)]/40" />
          </div>
        </div>
      </div>
    </section>
  );
}
