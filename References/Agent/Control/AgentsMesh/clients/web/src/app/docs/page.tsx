"use client";

import Link from "next/link";
import { useTranslations } from "next-intl";
import ArchitectureDiagram from "@/components/docs/ArchitectureDiagram";

const AGENTS = [
  "Claude Code (Anthropic)",
  "Codex CLI (OpenAI)",
  "Gemini CLI (Google)",
  "Aider",
  "OpenCode",
];

const CAPABILITIES = [
  "orchestrate",
  "remoteWorkstation",
  "taskDriven",
  "selfHosted",
] as const;

export default function DocsPage() {
  const t = useTranslations();

  return (
    <div>
      <div className="mb-10 sm:mb-14">
        <span className="inline-flex items-center gap-2 rounded-full azure-light-chip px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.14em]">
          <span className="h-1.5 w-1.5 rounded-full bg-[var(--azure-light-cyan-ink)]" />
          {t("docs.title")}
        </span>
        <h1 className="mt-4 text-3xl sm:text-4xl md:text-5xl font-semibold leading-tight tracking-tight text-[var(--azure-light-ink)]">
          {t("docs.intro.title")}
        </h1>
        <p className="mt-4 max-w-2xl text-base sm:text-lg leading-relaxed text-[var(--azure-light-ink-muted)]">
          {t("docs.intro.description")}
        </p>
      </div>

      <section className="mb-12 sm:mb-16">
        <div className="azure-light-card rounded-2xl p-5 sm:p-7">
          <p className="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--azure-light-cyan-ink)]">
            {t("docs.intro.supportedAgents")}
          </p>
          <ul className="mt-4 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
            {AGENTS.map((agent) => (
              <li
                key={agent}
                className="flex items-center gap-2 text-sm text-[var(--azure-light-ink)]"
              >
                <span className="h-1.5 w-1.5 rounded-full bg-[var(--azure-light-mint)]" />
                {agent}
              </li>
            ))}
            <li className="flex items-center gap-2 text-sm text-[var(--azure-light-ink-muted)]">
              <span className="h-1.5 w-1.5 rounded-full bg-[var(--azure-light-mint)]" />
              {t("docs.intro.customAgents")}
            </li>
          </ul>
        </div>
      </section>

      <section className="mb-12 sm:mb-16">
        <div className="mb-5 sm:mb-6">
          <h2 className="text-2xl sm:text-3xl font-semibold tracking-tight text-[var(--azure-light-ink)]">
            {t("docs.whatYouCanDo.title")}
          </h2>
          <p className="mt-2 text-[var(--azure-light-ink-muted)] leading-relaxed max-w-2xl">
            {t("docs.whatYouCanDo.description")}
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {CAPABILITIES.map((key) => (
            <div
              key={key}
              className="azure-light-card azure-light-card-hover rounded-xl p-5 sm:p-6"
            >
              <h3 className="text-base font-semibold text-[var(--azure-light-ink)]">
                {t(`docs.whatYouCanDo.${key}.title`)}
              </h3>
              <p className="mt-2 text-sm leading-relaxed text-[var(--azure-light-ink-muted)]">
                {t(`docs.whatYouCanDo.${key}.description`)}
              </p>
            </div>
          ))}
        </div>
      </section>

      <section className="mb-12 sm:mb-16">
        <div className="mb-2">
          <h2 className="text-2xl sm:text-3xl font-semibold tracking-tight text-[var(--azure-light-ink)]">
            {t("docs.architecture.title")}
          </h2>
          <p className="mt-2 text-[var(--azure-light-ink-muted)] leading-relaxed max-w-2xl">
            {t("docs.architecture.description")}
          </p>
        </div>
        <ArchitectureDiagram />
      </section>

      <section className="mb-12">
        <h2 className="text-2xl sm:text-3xl font-semibold mb-5 sm:mb-6 tracking-tight text-[var(--azure-light-ink)]">
          {t("docs.quickLinks.title")}
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <QuickLinkCard
            href="/docs/getting-started"
            title={`${t("docs.quickLinks.quickStart")} →`}
            description={t("docs.quickLinks.quickStartDesc")}
          />
          <QuickLinkCard
            href="/docs/features/agentpod"
            title="AgentPod →"
            description={t("docs.quickLinks.agentpodDesc")}
          />
          <QuickLinkCard
            href="/docs/features/channels"
            title="AgentsMesh →"
            description={t("docs.quickLinks.agentsmeshDesc")}
          />
          <QuickLinkCard
            href="/docs/runners/mcp-tools"
            title={`${t("docs.quickLinks.mcpTools")} →`}
            description={t("docs.quickLinks.mcpToolsDesc")}
          />
        </div>
      </section>
    </div>
  );
}

function QuickLinkCard({
  href,
  title,
  description,
}: {
  href: string;
  title: string;
  description: string;
}) {
  return (
    <Link
      href={href}
      className="azure-light-card azure-light-card-hover rounded-xl p-5 sm:p-6 block group"
    >
      <h3 className="text-base font-semibold text-[var(--azure-light-ink)] group-hover:text-[var(--azure-light-cyan-ink)] transition-colors">
        {title}
      </h3>
      <p className="mt-2 text-sm leading-relaxed text-[var(--azure-light-ink-muted)]">
        {description}
      </p>
    </Link>
  );
}
