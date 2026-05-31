"use client";

import Link from "next/link";
import { useTranslations } from "next-intl";
import { DocNavigation } from "@/components/docs/DocNavigation";

function StepHeader({
  step,
  titleKey,
  t,
}: {
  step: number;
  titleKey: string;
  t: ReturnType<typeof useTranslations>;
}) {
  return (
    <div className="flex items-center gap-3 mb-4">
      <div className="w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-sm font-bold">
        {step}
      </div>
      <h2 className="text-xl font-semibold">{t(titleKey)}</h2>
    </div>
  );
}

export default function McpAndSkillsTutorialPage() {
  const t = useTranslations();

  return (
    <div>
      <h1 className="text-4xl font-bold mb-2">
        {t("docs.tutorials.mcpSkills.title")}
      </h1>
      <p className="text-sm text-muted-foreground mb-8">
        {t("docs.tutorials.mcpSkills.difficulty")}
      </p>

      <p className="text-muted-foreground leading-relaxed mb-8">
        {t("docs.tutorials.mcpSkills.description")}
      </p>

      {/* What Are MCP Tools? */}
      <section className="mb-8">
        <div className="bg-muted/50 border border-border rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">
            {t("docs.tutorials.mcpSkills.whatIsMcp.title")}
          </h2>
          <p className="text-muted-foreground mb-4">
            {t("docs.tutorials.mcpSkills.whatIsMcp.description")}
          </p>
          <ul className="list-disc list-inside text-muted-foreground space-y-2 mb-4">
            <li>{t("docs.tutorials.mcpSkills.whatIsMcp.item1")}</li>
            <li>{t("docs.tutorials.mcpSkills.whatIsMcp.item2")}</li>
            <li>{t("docs.tutorials.mcpSkills.whatIsMcp.item3")}</li>
            <li>{t("docs.tutorials.mcpSkills.whatIsMcp.item4")}</li>
            <li>{t("docs.tutorials.mcpSkills.whatIsMcp.item5")}</li>
            <li>{t("docs.tutorials.mcpSkills.whatIsMcp.item6")}</li>
            <li>{t("docs.tutorials.mcpSkills.whatIsMcp.item7")}</li>
          </ul>
          <div className="bg-muted border border-border rounded-lg p-4 text-sm text-muted-foreground">
            {t("docs.tutorials.mcpSkills.whatIsMcp.autoNote")}
          </div>
        </div>
      </section>

      {/* Step 1: Built-in vs Custom */}
      <section className="mb-8">
        <div className="border border-border rounded-lg p-6">
          <StepHeader
            step={1}
            titleKey="docs.tutorials.mcpSkills.step1.title"
            t={t}
          />
          <p className="text-muted-foreground mb-4">
            {t("docs.tutorials.mcpSkills.step1.description")}
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-muted rounded-lg p-4">
              <h4 className="font-medium mb-2">
                {t("docs.tutorials.mcpSkills.step1.builtinTitle")}
              </h4>
              <p className="text-sm text-muted-foreground">
                {t("docs.tutorials.mcpSkills.step1.builtinDesc")}
              </p>
            </div>
            <div className="bg-muted rounded-lg p-4">
              <h4 className="font-medium mb-2">
                {t("docs.tutorials.mcpSkills.step1.customTitle")}
              </h4>
              <p className="text-sm text-muted-foreground">
                {t("docs.tutorials.mcpSkills.step1.customDesc")}
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Step 2: Install Custom MCP Server */}
      <section className="mb-8">
        <div className="border border-border rounded-lg p-6">
          <StepHeader
            step={2}
            titleKey="docs.tutorials.mcpSkills.step2.title"
            t={t}
          />
          <p className="text-muted-foreground mb-4">
            {t("docs.tutorials.mcpSkills.step2.description")}
          </p>
          <ol className="list-decimal list-inside text-muted-foreground space-y-2 mb-4">
            <li>{t("docs.tutorials.mcpSkills.step2.item1")}</li>
            <li>{t("docs.tutorials.mcpSkills.step2.item2")}</li>
            <li>{t("docs.tutorials.mcpSkills.step2.item3")}</li>
            <li>{t("docs.tutorials.mcpSkills.step2.item4")}</li>
            <li>{t("docs.tutorials.mcpSkills.step2.item5")}</li>
            <li>{t("docs.tutorials.mcpSkills.step2.item6")}</li>
            <li>{t("docs.tutorials.mcpSkills.step2.item7")}</li>
          </ol>
          <div className="bg-muted/50 border border-border rounded-lg p-4 text-sm text-muted-foreground">
            {t("docs.tutorials.mcpSkills.step2.tip")}
          </div>
        </div>
      </section>

      {/* Step 3: Verify */}
      <section className="mb-8">
        <div className="border border-border rounded-lg p-6">
          <StepHeader
            step={3}
            titleKey="docs.tutorials.mcpSkills.step3.title"
            t={t}
          />
          <p className="text-muted-foreground mb-4">
            {t("docs.tutorials.mcpSkills.step3.description")}
          </p>
          <ol className="list-decimal list-inside text-muted-foreground space-y-2">
            <li>{t("docs.tutorials.mcpSkills.step3.item1")}</li>
            <li>{t("docs.tutorials.mcpSkills.step3.item2")}</li>
            <li>{t("docs.tutorials.mcpSkills.step3.item3")}</li>
            <li>{t("docs.tutorials.mcpSkills.step3.item4")}</li>
          </ol>
        </div>
      </section>

      {/* What Are Skills? */}
      <section className="mb-8">
        <div className="bg-muted/50 border border-border rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">
            {t("docs.tutorials.mcpSkills.whatAreSkills.title")}
          </h2>
          <p className="text-muted-foreground mb-4">
            {t("docs.tutorials.mcpSkills.whatAreSkills.description")}
          </p>
          <ul className="list-disc list-inside text-muted-foreground space-y-2">
            <li>{t("docs.tutorials.mcpSkills.whatAreSkills.item1")}</li>
            <li>{t("docs.tutorials.mcpSkills.whatAreSkills.item2")}</li>
          </ul>
        </div>
      </section>

      {/* Step 4: Built-in Skills */}
      <section className="mb-8">
        <div className="border border-border rounded-lg p-6">
          <StepHeader
            step={4}
            titleKey="docs.tutorials.mcpSkills.step4.title"
            t={t}
          />
          <p className="text-muted-foreground mb-4">
            {t("docs.tutorials.mcpSkills.step4.description")}
          </p>
          <div className="space-y-4">
            <div className="border border-border rounded-lg p-4">
              <h3 className="font-medium mb-2">
                {t("docs.tutorials.mcpSkills.step4.channelTitle")}
              </h3>
              <p className="text-sm text-muted-foreground">
                {t("docs.tutorials.mcpSkills.step4.channelDesc")}
              </p>
            </div>
            <div className="border border-border rounded-lg p-4">
              <h3 className="font-medium mb-2">
                {t("docs.tutorials.mcpSkills.step4.delegateTitle")}
              </h3>
              <p className="text-sm text-muted-foreground">
                {t("docs.tutorials.mcpSkills.step4.delegateDesc")}
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Step 5: Install Custom Skills */}
      <section className="mb-8">
        <div className="border border-border rounded-lg p-6">
          <StepHeader
            step={5}
            titleKey="docs.tutorials.mcpSkills.step5.title"
            t={t}
          />
          <p className="text-muted-foreground mb-4">
            {t("docs.tutorials.mcpSkills.step5.description")}
          </p>
          <ol className="list-decimal list-inside text-muted-foreground space-y-2 mb-4">
            <li>{t("docs.tutorials.mcpSkills.step5.item1")}</li>
            <li>{t("docs.tutorials.mcpSkills.step5.item2")}</li>
            <li>{t("docs.tutorials.mcpSkills.step5.item3")}</li>
            <li>{t("docs.tutorials.mcpSkills.step5.item4")}</li>
          </ol>
          <div className="bg-muted/50 border border-border rounded-lg p-4 text-sm text-muted-foreground">
            {t("docs.tutorials.mcpSkills.step5.tip")}
          </div>
        </div>
      </section>

      {/* Step 6: Per-Repository Config */}
      <section className="mb-8">
        <div className="border border-border rounded-lg p-6">
          <StepHeader
            step={6}
            titleKey="docs.tutorials.mcpSkills.step6.title"
            t={t}
          />
          <p className="text-muted-foreground mb-4">
            {t("docs.tutorials.mcpSkills.step6.description")}
          </p>
          <ul className="list-disc list-inside text-muted-foreground space-y-2 mb-4">
            <li>{t("docs.tutorials.mcpSkills.step6.item1")}</li>
            <li>{t("docs.tutorials.mcpSkills.step6.item2")}</li>
            <li>{t("docs.tutorials.mcpSkills.step6.item3")}</li>
          </ul>
          <div className="bg-muted/50 border border-border rounded-lg p-4 text-sm text-muted-foreground">
            {t("docs.tutorials.mcpSkills.step6.tip")}
          </div>
        </div>
      </section>

      {/* Next Steps */}
      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">
          {t("docs.tutorials.mcpSkills.nextSteps.title")}
        </h2>
        <p className="text-muted-foreground mb-4">
          {t("docs.tutorials.mcpSkills.nextSteps.description")}
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Link
            href="/docs/tutorials/first-pod"
            className="border border-border rounded-lg p-4 hover:border-primary transition-colors"
          >
            <p className="text-sm text-muted-foreground">
              {t("docs.tutorials.mcpSkills.nextSteps.item1")}
            </p>
          </Link>
          <Link
            href="/docs/tutorials/multi-agent-collaboration"
            className="border border-border rounded-lg p-4 hover:border-primary transition-colors"
          >
            <p className="text-sm text-muted-foreground">
              {t("docs.tutorials.mcpSkills.nextSteps.item2")}
            </p>
          </Link>
        </div>
      </section>

      <DocNavigation />
    </div>
  );
}
