"use client";

import { useTranslations } from "next-intl";
import { useServerUrl } from "@/hooks/useServerUrl";

interface Step {
  number: string;
  title: string;
  description: string;
  code: string;
  accent: "cyan" | "mint";
}

export function HowItWorks() {
  const t = useTranslations();
  const serverUrl = useServerUrl();

  const steps: Step[] = [
    {
      number: "01",
      title: t("landing.howItWorks.step1.title"),
      description: t("landing.howItWorks.step1.description"),
      accent: "cyan",
      code: `curl -fsSL ${serverUrl}/install.sh | sh
agentsmesh-runner register --token <YOUR_TOKEN>
agentsmesh-runner run`,
    },
    {
      number: "02",
      title: t("landing.howItWorks.step2.title"),
      description: t("landing.howItWorks.step2.description"),
      accent: "mint",
      code: `# In the web console
> Workspace → New Pod
> Select Runner & Agent
> Choose Repository → Create`,
    },
    {
      number: "03",
      title: t("landing.howItWorks.step3.title"),
      description: t("landing.howItWorks.step3.description"),
      accent: "cyan",
      code: `# Watch them ship
- Pods stream live to your browser
- Agents coordinate via channels
- Review MRs, merge when ready`,
    },
  ];

  return (
    <section className="py-32 relative bg-[var(--azure-bg-deeper)]">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-20">
          <h2 className="font-headline text-4xl md:text-5xl font-bold mb-4">
            {t("landing.howItWorks.title")}{" "}
            <span className="azure-gradient-text">{t("landing.howItWorks.titleHighlight")}</span>
          </h2>
          <p className="text-[var(--azure-text-muted)] font-headline tracking-[0.2em] uppercase text-xs">
            {t("landing.howItWorks.description")}
          </p>
        </div>

        <div className="relative space-y-12 md:space-y-16">
          <div className="absolute left-1/2 top-0 bottom-0 w-px bg-gradient-to-b from-transparent via-[var(--azure-cyan)]/30 to-transparent transform -translate-x-1/2 hidden md:block" />

          {steps.map((step, index) => {
            const onLeft = index % 2 === 0;
            const accentColor = step.accent === "cyan" ? "var(--azure-cyan)" : "var(--azure-mint)";

            return (
              <div key={step.number} className="flex flex-col md:flex-row items-center gap-8">
                <div className={`flex-1 w-full ${onLeft ? "md:text-right md:order-1" : "md:order-3"}`}>
                  <h4 className="font-headline text-2xl font-bold mb-3 text-foreground">{step.title}</h4>
                  <p className="text-[var(--azure-text-muted)] leading-relaxed">{step.description}</p>
                </div>

                <div className="md:order-2 z-10 flex-shrink-0">
                  <div
                    className="w-14 h-14 rounded-full bg-[var(--azure-bg-high)] border-2 flex items-center justify-center font-headline font-bold"
                    style={{ borderColor: accentColor, color: accentColor }}
                  >
                    {step.number}
                  </div>
                </div>

                <div className={`flex-1 w-full min-w-0 ${onLeft ? "md:order-3" : "md:order-1"}`}>
                  <div className="azure-glass rounded-2xl border border-white/5 p-4 sm:p-5 font-mono text-xs leading-relaxed text-[var(--azure-text-muted)] overflow-x-auto">
                    <pre className="whitespace-pre-wrap break-all sm:break-words">{step.code}</pre>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
