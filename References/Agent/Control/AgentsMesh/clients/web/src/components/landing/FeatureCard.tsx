"use client";

import type { useTranslations } from "next-intl";
import { FeatureVisuals } from "./FeatureVisuals";

export interface FeatureData {
  number: string;
  title: string;
  subtitle: string;
  description: string;
  highlights: string[];
  align: string;
  podDemo?: boolean;
  diagram?: { nodes: Array<{ id: string; label: string; x: number; y: number }>; connections: Array<{ from: string; to: string; dashed?: boolean }> };
  kanban?: { columns: Array<{ titleKey: string; cards: string[] }> };
  schedule?: boolean;
  architecture?: boolean;
}

interface FeatureCardProps {
  feature: FeatureData;
  t: ReturnType<typeof useTranslations>;
}

export function FeatureCard({ feature, t }: FeatureCardProps) {
  const reverse = feature.align === "right";

  return (
    <div className={`grid lg:grid-cols-2 gap-12 lg:gap-16 items-center`}>
      <div className={reverse ? "lg:order-2" : ""}>
        <span className="font-headline text-[10px] font-black uppercase tracking-[0.3em] text-[var(--azure-cyan)] mb-3 block">
          Capability {feature.number} · {feature.subtitle}
        </span>
        <h3 className="font-headline text-3xl md:text-4xl font-bold mb-6 leading-tight">
          {feature.title}
        </h3>
        <p className="text-[var(--azure-text-muted)] text-lg leading-relaxed mb-8 font-light">
          {feature.description}
        </p>
        <ul className="space-y-3.5">
          {feature.highlights.map((highlight) => (
            <li key={highlight} className="flex items-start gap-3">
              <div className="mt-2 w-1.5 h-1.5 rounded-full bg-[var(--azure-mint)] flex-shrink-0" />
              <span className="text-foreground/85 leading-relaxed">{highlight}</span>
            </li>
          ))}
        </ul>
      </div>

      <div className={`relative group ${reverse ? "lg:order-1" : ""}`}>
        <div className="absolute -inset-6 bg-[var(--azure-cyan)]/20 blur-[60px] rounded-full opacity-30 group-hover:opacity-60 transition-opacity duration-700" />
        <div className="relative azure-glass rounded-3xl border border-white/5 p-3 sm:p-4 transition-all duration-500 group-hover:border-[var(--azure-cyan)]/20">
          <div className="rounded-2xl overflow-hidden bg-[var(--azure-bg-deeper)]/60">
            <FeatureVisuals feature={feature} t={t} />
          </div>
        </div>
      </div>
    </div>
  );
}
