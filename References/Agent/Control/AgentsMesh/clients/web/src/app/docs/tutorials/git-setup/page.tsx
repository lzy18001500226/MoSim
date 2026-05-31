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

export default function GitSetupTutorialPage() {
  const t = useTranslations();

  return (
    <div>
      <h1 className="text-4xl font-bold mb-2">
        {t("docs.tutorials.gitSetup.title")}
      </h1>
      <p className="text-sm text-muted-foreground mb-8">
        {t("docs.tutorials.gitSetup.difficulty")}
      </p>

      <p className="text-muted-foreground leading-relaxed mb-8">
        {t("docs.tutorials.gitSetup.description")}
      </p>

      {/* Prerequisites */}
      <section className="mb-8">
        <div className="bg-muted/50 border border-border rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">
            {t("docs.tutorials.gitSetup.prerequisites.title")}
          </h2>
          <p className="text-muted-foreground mb-4">
            {t("docs.tutorials.gitSetup.prerequisites.description")}
          </p>
          <ul className="list-disc list-inside text-muted-foreground space-y-2">
            <li>{t("docs.tutorials.gitSetup.prerequisites.item1")}</li>
            <li>{t("docs.tutorials.gitSetup.prerequisites.item2")}</li>
          </ul>
        </div>
      </section>

      {/* Step 1: Open Git Settings */}
      <section className="mb-8">
        <div className="border border-border rounded-lg p-6">
          <StepHeader
            step={1}
            titleKey="docs.tutorials.gitSetup.step1.title"
            t={t}
          />
          <p className="text-muted-foreground">
            {t("docs.tutorials.gitSetup.step1.description")}
          </p>
        </div>
      </section>

      {/* Step 2: Connect GitHub */}
      <section className="mb-8">
        <div className="border border-border rounded-lg p-6">
          <StepHeader
            step={2}
            titleKey="docs.tutorials.gitSetup.step2.title"
            t={t}
          />
          <p className="text-muted-foreground mb-4">
            {t("docs.tutorials.gitSetup.step2.description")}
          </p>
          <ol className="list-decimal list-inside text-muted-foreground space-y-2 mb-4">
            <li>{t("docs.tutorials.gitSetup.step2.item1")}</li>
            <li>{t("docs.tutorials.gitSetup.step2.item2")}</li>
            <li>{t("docs.tutorials.gitSetup.step2.item3")}</li>
            <li>{t("docs.tutorials.gitSetup.step2.item4")}</li>
          </ol>
          <div className="bg-muted/50 border border-border rounded-lg p-4 text-sm text-muted-foreground">
            {t("docs.tutorials.gitSetup.step2.tip")}
          </div>
        </div>
      </section>

      {/* Step 3: Connect GitLab */}
      <section className="mb-8">
        <div className="border border-border rounded-lg p-6">
          <StepHeader
            step={3}
            titleKey="docs.tutorials.gitSetup.step3.title"
            t={t}
          />
          <p className="text-muted-foreground mb-4">
            {t("docs.tutorials.gitSetup.step3.description")}
          </p>
          <ol className="list-decimal list-inside text-muted-foreground space-y-2 mb-4">
            <li>{t("docs.tutorials.gitSetup.step3.item1")}</li>
            <li>{t("docs.tutorials.gitSetup.step3.item2")}</li>
            <li>{t("docs.tutorials.gitSetup.step3.item3")}</li>
            <li>{t("docs.tutorials.gitSetup.step3.item4")}</li>
          </ol>
          <div className="bg-muted/50 border border-border rounded-lg p-4 text-sm text-muted-foreground">
            {t("docs.tutorials.gitSetup.step3.tip")}
          </div>
        </div>
      </section>

      {/* Step 4: Connect Gitee */}
      <section className="mb-8">
        <div className="border border-border rounded-lg p-6">
          <StepHeader
            step={4}
            titleKey="docs.tutorials.gitSetup.step4.title"
            t={t}
          />
          <p className="text-muted-foreground mb-4">
            {t("docs.tutorials.gitSetup.step4.description")}
          </p>
          <ol className="list-decimal list-inside text-muted-foreground space-y-2">
            <li>{t("docs.tutorials.gitSetup.step4.item1")}</li>
            <li>{t("docs.tutorials.gitSetup.step4.item2")}</li>
            <li>{t("docs.tutorials.gitSetup.step4.item3")}</li>
          </ol>
        </div>
      </section>

      {/* Step 5: Import Repositories */}
      <section className="mb-8">
        <div className="border border-border rounded-lg p-6">
          <StepHeader
            step={5}
            titleKey="docs.tutorials.gitSetup.step5.title"
            t={t}
          />
          <p className="text-muted-foreground mb-4">
            {t("docs.tutorials.gitSetup.step5.description")}
          </p>
          <ol className="list-decimal list-inside text-muted-foreground space-y-2">
            <li>{t("docs.tutorials.gitSetup.step5.item1")}</li>
            <li>{t("docs.tutorials.gitSetup.step5.item2")}</li>
            <li>{t("docs.tutorials.gitSetup.step5.item3")}</li>
            <li>{t("docs.tutorials.gitSetup.step5.item4")}</li>
          </ol>
        </div>
      </section>

      {/* Step 6: SSH Keys */}
      <section className="mb-8">
        <div className="border border-border rounded-lg p-6">
          <StepHeader
            step={6}
            titleKey="docs.tutorials.gitSetup.step6.title"
            t={t}
          />
          <p className="text-muted-foreground mb-4">
            {t("docs.tutorials.gitSetup.step6.description")}
          </p>
          <ol className="list-decimal list-inside text-muted-foreground space-y-2 mb-4">
            <li>{t("docs.tutorials.gitSetup.step6.item1")}</li>
            <li>{t("docs.tutorials.gitSetup.step6.item2")}</li>
            <li>{t("docs.tutorials.gitSetup.step6.item3")}</li>
          </ol>
          <div className="bg-muted/50 border border-border rounded-lg p-4 text-sm text-muted-foreground">
            {t("docs.tutorials.gitSetup.step6.tip")}
          </div>
        </div>
      </section>

      {/* Step 7: Verify */}
      <section className="mb-8">
        <div className="border border-border rounded-lg p-6">
          <StepHeader
            step={7}
            titleKey="docs.tutorials.gitSetup.step7.title"
            t={t}
          />
          <p className="text-muted-foreground mb-4">
            {t("docs.tutorials.gitSetup.step7.description")}
          </p>
          <ol className="list-decimal list-inside text-muted-foreground space-y-2 mb-4">
            <li>{t("docs.tutorials.gitSetup.step7.item1")}</li>
            <li>{t("docs.tutorials.gitSetup.step7.item2")}</li>
            <li>{t("docs.tutorials.gitSetup.step7.item3")}</li>
            <li>{t("docs.tutorials.gitSetup.step7.item4")}</li>
          </ol>
          <div className="bg-muted/50 border border-border rounded-lg p-4 text-sm text-muted-foreground">
            {t("docs.tutorials.gitSetup.step7.tip")}
          </div>
        </div>
      </section>

      {/* Next Steps */}
      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">
          {t("docs.tutorials.gitSetup.nextSteps.title")}
        </h2>
        <p className="text-muted-foreground mb-4">
          {t("docs.tutorials.gitSetup.nextSteps.description")}
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Link
            href="/docs/tutorials/first-pod"
            className="border border-border rounded-lg p-4 hover:border-primary transition-colors"
          >
            <p className="text-sm text-muted-foreground">
              {t("docs.tutorials.gitSetup.nextSteps.item1")}
            </p>
          </Link>
          <Link
            href="/docs/tutorials/ticket-workflow"
            className="border border-border rounded-lg p-4 hover:border-primary transition-colors"
          >
            <p className="text-sm text-muted-foreground">
              {t("docs.tutorials.gitSetup.nextSteps.item2")}
            </p>
          </Link>
        </div>
      </section>

      <DocNavigation />
    </div>
  );
}
