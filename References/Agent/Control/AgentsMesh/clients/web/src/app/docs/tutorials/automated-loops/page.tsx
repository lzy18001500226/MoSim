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

export default function AutomatedLoopsTutorialPage() {
  const t = useTranslations();

  return (
    <div>
      <h1 className="text-4xl font-bold mb-2">
        {t("docs.tutorials.loops.title")}
      </h1>
      <p className="text-sm text-muted-foreground mb-8">
        {t("docs.tutorials.loops.difficulty")}
      </p>

      <p className="text-muted-foreground leading-relaxed mb-8">
        {t("docs.tutorials.loops.description")}
      </p>

      {/* What Are Loops? */}
      <section className="mb-8">
        <div className="bg-muted/50 border border-border rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">
            {t("docs.tutorials.loops.whatAreLoops.title")}
          </h2>
          <p className="text-muted-foreground mb-4">
            {t("docs.tutorials.loops.whatAreLoops.description")}
          </p>
          <ul className="list-disc list-inside text-muted-foreground space-y-2">
            <li>{t("docs.tutorials.loops.whatAreLoops.item1")}</li>
            <li>{t("docs.tutorials.loops.whatAreLoops.item2")}</li>
            <li>{t("docs.tutorials.loops.whatAreLoops.item3")}</li>
            <li>{t("docs.tutorials.loops.whatAreLoops.item4")}</li>
          </ul>
        </div>
      </section>

      {/* Step 1 */}
      <section className="mb-8">
        <div className="border border-border rounded-lg p-6">
          <StepHeader
            step={1}
            titleKey="docs.tutorials.loops.step1.title"
            t={t}
          />
          <p className="text-muted-foreground">
            {t("docs.tutorials.loops.step1.description")}
          </p>
        </div>
      </section>

      {/* Step 2 */}
      <section className="mb-8">
        <div className="border border-border rounded-lg p-6">
          <StepHeader
            step={2}
            titleKey="docs.tutorials.loops.step2.title"
            t={t}
          />
          <p className="text-muted-foreground mb-4">
            {t("docs.tutorials.loops.step2.description")}
          </p>
          <p className="font-medium mb-3">
            {t("docs.tutorials.loops.step2.fields")}
          </p>
          <ol className="list-decimal list-inside text-muted-foreground space-y-2">
            <li>{t("docs.tutorials.loops.step2.field1")}</li>
            <li>{t("docs.tutorials.loops.step2.field2")}</li>
            <li>{t("docs.tutorials.loops.step2.field3")}</li>
            <li>{t("docs.tutorials.loops.step2.field4")}</li>
            <li>{t("docs.tutorials.loops.step2.field5")}</li>
            <li>{t("docs.tutorials.loops.step2.field6")}</li>
            <li>{t("docs.tutorials.loops.step2.field7")}</li>
          </ol>
        </div>
      </section>

      {/* Step 3 */}
      <section className="mb-8">
        <div className="border border-border rounded-lg p-6">
          <StepHeader
            step={3}
            titleKey="docs.tutorials.loops.step3.title"
            t={t}
          />
          <p className="text-muted-foreground mb-4">
            {t("docs.tutorials.loops.step3.description")}
          </p>
          <div className="bg-muted rounded-lg p-4 font-mono text-sm overflow-x-auto mb-4">
            <div className="space-y-2 text-green-500 dark:text-green-400">
              <p>{t("docs.tutorials.loops.step3.pattern1")}</p>
              <p>{t("docs.tutorials.loops.step3.pattern2")}</p>
              <p>{t("docs.tutorials.loops.step3.pattern3")}</p>
              <p>{t("docs.tutorials.loops.step3.pattern4")}</p>
            </div>
          </div>
          <div className="bg-muted/50 border border-border rounded-lg p-4 text-sm text-muted-foreground">
            {t("docs.tutorials.loops.step3.tip")}
          </div>
        </div>
      </section>

      {/* Step 4 */}
      <section className="mb-8">
        <div className="border border-border rounded-lg p-6">
          <StepHeader
            step={4}
            titleKey="docs.tutorials.loops.step4.title"
            t={t}
          />
          <p className="text-muted-foreground mb-4">
            {t("docs.tutorials.loops.step4.description")}
          </p>
          <ul className="list-disc list-inside text-muted-foreground space-y-2">
            <li>{t("docs.tutorials.loops.step4.item1")}</li>
            <li>{t("docs.tutorials.loops.step4.item2")}</li>
            <li>{t("docs.tutorials.loops.step4.item3")}</li>
            <li>{t("docs.tutorials.loops.step4.item4")}</li>
          </ul>
        </div>
      </section>

      {/* Step 5 */}
      <section className="mb-8">
        <div className="border border-border rounded-lg p-6">
          <StepHeader
            step={5}
            titleKey="docs.tutorials.loops.step5.title"
            t={t}
          />
          <p className="text-muted-foreground mb-4">
            {t("docs.tutorials.loops.step5.description")}
          </p>
          <ul className="list-disc list-inside text-muted-foreground space-y-2">
            <li>{t("docs.tutorials.loops.step5.item1")}</li>
            <li>{t("docs.tutorials.loops.step5.item2")}</li>
            <li>{t("docs.tutorials.loops.step5.item3")}</li>
            <li>{t("docs.tutorials.loops.step5.item4")}</li>
            <li>{t("docs.tutorials.loops.step5.item5")}</li>
          </ul>
        </div>
      </section>

      {/* Common Patterns */}
      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">
          {t("docs.tutorials.loops.commonPatterns.title")}
        </h2>
        <div className="space-y-4">
          <div className="border border-border rounded-lg p-4">
            <h3 className="font-medium mb-2">
              {t("docs.tutorials.loops.commonPatterns.pattern1.title")}
            </h3>
            <p className="text-sm text-muted-foreground">
              {t("docs.tutorials.loops.commonPatterns.pattern1.description")}
            </p>
          </div>
          <div className="border border-border rounded-lg p-4">
            <h3 className="font-medium mb-2">
              {t("docs.tutorials.loops.commonPatterns.pattern2.title")}
            </h3>
            <p className="text-sm text-muted-foreground">
              {t("docs.tutorials.loops.commonPatterns.pattern2.description")}
            </p>
          </div>
          <div className="border border-border rounded-lg p-4">
            <h3 className="font-medium mb-2">
              {t("docs.tutorials.loops.commonPatterns.pattern3.title")}
            </h3>
            <p className="text-sm text-muted-foreground">
              {t("docs.tutorials.loops.commonPatterns.pattern3.description")}
            </p>
          </div>
        </div>
      </section>

      {/* Next Steps */}
      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">
          {t("docs.tutorials.loops.nextSteps.title")}
        </h2>
        <p className="text-muted-foreground mb-4">
          {t("docs.tutorials.loops.nextSteps.description")}
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Link
            href="/docs/tutorials/multi-agent-collaboration"
            className="border border-border rounded-lg p-4 hover:border-primary transition-colors"
          >
            <p className="text-sm text-muted-foreground">
              {t("docs.tutorials.loops.nextSteps.item1")}
            </p>
          </Link>
          <Link
            href="/docs/tutorials/ticket-workflow"
            className="border border-border rounded-lg p-4 hover:border-primary transition-colors"
          >
            <p className="text-sm text-muted-foreground">
              {t("docs.tutorials.loops.nextSteps.item2")}
            </p>
          </Link>
        </div>
      </section>

      <DocNavigation />
    </div>
  );
}
