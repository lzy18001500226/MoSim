"use client";

import { useServerUrl } from "@/hooks/useServerUrl";
import { useTranslations } from "next-intl";

export function UpdateMethods() {
  const serverUrl = useServerUrl();
  const t = useTranslations("docs.tutorials.runnerSetup.updating");

  return (
    <div className="space-y-4">
      <MethodCard
        badge="A"
        title={t("ui.title")}
        description={t("ui.description")}
        bullets={[t("ui.step1"), t("ui.step2"), t("ui.step3")]}
        note={t("ui.note")}
      />

      <MethodCard
        badge="B"
        title={t("command.title")}
        description={t("command.description")}
        code={`agentsmesh-runner update              # ${t("command.hintInteractive")}
agentsmesh-runner update --check      # ${t("command.hintCheck")}
agentsmesh-runner update -y           # ${t("command.hintSilent")}
agentsmesh-runner update -v v1.2.3    # ${t("command.hintVersion")}`}
        note={t("command.note")}
      />

      <MethodCard
        badge="C"
        title={t("reinstall.title")}
        description={t("reinstall.description")}
        code={`# macOS / Linux
curl -fsSL ${serverUrl}/install.sh | sh

# Windows (PowerShell)
irm ${serverUrl}/install.ps1 | iex`}
        extraCodeLabel={t("reinstall.restartLabel")}
        extraCode={`# System service
sudo agentsmesh-runner service restart

# CLI mode
pkill agentsmesh-runner && agentsmesh-runner run`}
        note={t("reinstall.note")}
      />
    </div>
  );
}

function MethodCard({
  badge,
  title,
  description,
  bullets,
  code,
  extraCode,
  extraCodeLabel,
  note,
}: {
  badge: string;
  title: string;
  description: string;
  bullets?: string[];
  code?: string;
  extraCode?: string;
  extraCodeLabel?: string;
  note?: string;
}) {
  return (
    <div className="azure-light-card rounded-xl p-6">
      <div className="flex items-center gap-3 mb-3">
        <span className="w-7 h-7 rounded-full azure-light-chip flex items-center justify-center text-xs font-bold">
          {badge}
        </span>
        <h3 className="text-lg font-semibold text-[var(--azure-light-ink)]">
          {title}
        </h3>
      </div>
      <p className="text-sm text-[var(--azure-light-ink-muted)] leading-relaxed mb-3">
        {description}
      </p>
      {bullets && (
        <ol className="list-decimal list-inside text-sm text-[var(--azure-light-ink-muted)] space-y-1 mb-3">
          {bullets.map((b) => (
            <li key={b}>{b}</li>
          ))}
        </ol>
      )}
      {code && (
        <pre className="bg-[var(--azure-light-surface-high)] rounded-lg p-3 font-mono text-xs overflow-x-auto text-[var(--azure-light-cyan-ink)]">
          {code}
        </pre>
      )}
      {extraCodeLabel && (
        <p className="mt-3 mb-2 text-xs font-semibold uppercase tracking-[0.14em] text-[var(--azure-light-ink-soft)]">
          {extraCodeLabel}
        </p>
      )}
      {extraCode && (
        <pre className="bg-[var(--azure-light-surface-high)] rounded-lg p-3 font-mono text-xs overflow-x-auto text-[var(--azure-light-cyan-ink)]">
          {extraCode}
        </pre>
      )}
      {note && (
        <p className="mt-3 text-xs text-[var(--azure-light-ink-muted)] italic">
          {note}
        </p>
      )}
    </div>
  );
}
