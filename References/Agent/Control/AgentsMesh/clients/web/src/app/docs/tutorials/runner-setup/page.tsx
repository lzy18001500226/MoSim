"use client";

import Link from "next/link";
import { useServerUrl } from "@/hooks/useServerUrl";
import { useTranslations } from "next-intl";
import { DocNavigation } from "@/components/docs/DocNavigation";
import { UpdateMethods } from "./_sections/UpdateMethods";
import { BackgroundModes } from "./_sections/BackgroundModes";

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

export default function RunnerSetupTutorialPage() {
  const serverUrl = useServerUrl();
  const t = useTranslations();

  return (
    <div>
      <h1 className="text-4xl font-bold mb-2">
        {t("docs.tutorials.runnerSetup.title")}
      </h1>
      <p className="text-sm text-muted-foreground mb-8">
        {t("docs.tutorials.runnerSetup.difficulty")}
      </p>

      <p className="text-muted-foreground leading-relaxed mb-8">
        {t("docs.tutorials.runnerSetup.description")}
      </p>

      {/* Prerequisites */}
      <section className="mb-8">
        <div className="bg-muted/50 border border-border rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">
            {t("docs.tutorials.runnerSetup.prerequisites.title")}
          </h2>
          <p className="text-muted-foreground mb-4">
            {t("docs.tutorials.runnerSetup.prerequisites.description")}
          </p>
          <ul className="list-disc list-inside text-muted-foreground space-y-2">
            <li>{t("docs.tutorials.runnerSetup.prerequisites.item1")}</li>
            <li>{t("docs.tutorials.runnerSetup.prerequisites.item2")}</li>
            <li>{t("docs.tutorials.runnerSetup.prerequisites.item3")}</li>
            <li>{t("docs.tutorials.runnerSetup.prerequisites.item4")}</li>
          </ul>
        </div>
      </section>

      {/* Step 1: Install */}
      <section className="mb-8">
        <div className="border border-border rounded-lg p-6">
          <StepHeader
            step={1}
            titleKey="docs.tutorials.runnerSetup.step1.title"
            t={t}
          />
          <p className="text-muted-foreground mb-4">
            {t("docs.tutorials.runnerSetup.step1.description")}
          </p>
          <div className="bg-muted rounded-lg p-4 font-mono text-sm overflow-x-auto mb-4">
            <p className="text-muted-foreground font-sans text-xs mb-2">
              {t("docs.tutorials.runnerSetup.step1.oneLine")}
            </p>
            <pre className="text-green-500 dark:text-green-400">{`curl -fsSL ${serverUrl}/install.sh | sh`}</pre>
          </div>
          <div className="bg-muted/50 border border-border rounded-lg p-4 text-sm text-muted-foreground">
            {t("docs.tutorials.runnerSetup.step1.tip")}
          </div>
        </div>
      </section>

      {/* Step 2: Register */}
      <section className="mb-8">
        <div className="border border-border rounded-lg p-6">
          <StepHeader
            step={2}
            titleKey="docs.tutorials.runnerSetup.step2.title"
            t={t}
          />
          <p className="text-muted-foreground mb-4">
            {t("docs.tutorials.runnerSetup.step2.description")}
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div className="bg-muted rounded-lg p-4">
              <h4 className="font-medium mb-2">
                {t("docs.tutorials.runnerSetup.step2.methodToken")}
              </h4>
              <p className="text-sm text-muted-foreground mb-2">
                {t("docs.tutorials.runnerSetup.step2.methodTokenDesc")}
              </p>
              <div className="font-mono text-sm overflow-x-auto">
                <pre className="text-green-500 dark:text-green-400">{`agentsmesh-runner register \\
  --server ${serverUrl} \\
  --token <YOUR_TOKEN>`}</pre>
              </div>
            </div>
            <div className="bg-muted rounded-lg p-4">
              <h4 className="font-medium mb-2">
                {t("docs.tutorials.runnerSetup.step2.methodLogin")}
              </h4>
              <p className="text-sm text-muted-foreground mb-2">
                {t("docs.tutorials.runnerSetup.step2.methodLoginDesc")}
              </p>
              <div className="font-mono text-sm overflow-x-auto">
                <pre className="text-green-500 dark:text-green-400">{`agentsmesh-runner login`}</pre>
              </div>
            </div>
          </div>
          <div className="bg-muted/50 border border-border rounded-lg p-4 text-sm text-muted-foreground">
            {t("docs.tutorials.runnerSetup.step2.tip")}
          </div>
        </div>
      </section>

      {/* Step 3: Start */}
      <section className="mb-8">
        <div className="border border-border rounded-lg p-6">
          <StepHeader
            step={3}
            titleKey="docs.tutorials.runnerSetup.step3.title"
            t={t}
          />
          <p className="text-muted-foreground mb-4">
            {t("docs.tutorials.runnerSetup.step3.description")}
          </p>
          <div className="bg-muted rounded-lg p-4 font-mono text-sm overflow-x-auto mb-4">
            <pre className="text-green-500 dark:text-green-400">{`agentsmesh-runner run`}</pre>
          </div>
          <ul className="list-disc list-inside text-muted-foreground space-y-2 mb-4">
            <li>{t("docs.tutorials.runnerSetup.step3.item1")}</li>
            <li>{t("docs.tutorials.runnerSetup.step3.item2")}</li>
            <li>{t("docs.tutorials.runnerSetup.step3.item3")}</li>
          </ul>
          <div className="bg-muted/50 border border-border rounded-lg p-4 text-sm text-muted-foreground">
            {t("docs.tutorials.runnerSetup.step3.tip")}
          </div>
          <BackgroundModes />
        </div>
      </section>

      {/* Step 4: Install AI Agent CLIs */}
      <section className="mb-8">
        <div className="border border-border rounded-lg p-6">
          <StepHeader
            step={4}
            titleKey="docs.tutorials.runnerSetup.step4.title"
            t={t}
          />
          <p className="text-muted-foreground mb-4">
            {t("docs.tutorials.runnerSetup.step4.description")}
          </p>
          <ul className="list-disc list-inside text-muted-foreground space-y-2 mb-4">
            <li>{t("docs.tutorials.runnerSetup.step4.item1")}</li>
            <li>{t("docs.tutorials.runnerSetup.step4.item2")}</li>
            <li>{t("docs.tutorials.runnerSetup.step4.item3")}</li>
          </ul>
          <div className="bg-muted/50 border border-border rounded-lg p-4 text-sm text-muted-foreground">
            {t("docs.tutorials.runnerSetup.step4.tip")}
          </div>
        </div>
      </section>

      {/* Step 5: Verify */}
      <section className="mb-8">
        <div className="border border-border rounded-lg p-6">
          <StepHeader
            step={5}
            titleKey="docs.tutorials.runnerSetup.step5.title"
            t={t}
          />
          <p className="text-muted-foreground mb-4">
            {t("docs.tutorials.runnerSetup.step5.description")}
          </p>
          <ol className="list-decimal list-inside text-muted-foreground space-y-2">
            <li>{t("docs.tutorials.runnerSetup.step5.item1")}</li>
            <li>{t("docs.tutorials.runnerSetup.step5.item2")}</li>
            <li>{t("docs.tutorials.runnerSetup.step5.item3")}</li>
            <li>{t("docs.tutorials.runnerSetup.step5.item4")}</li>
          </ol>
        </div>
      </section>

      {/* Step 6: Keep Up to Date */}
      <section className="mb-8">
        <div className="mb-6">
          <StepHeader
            step={6}
            titleKey="docs.tutorials.runnerSetup.updating.title"
            t={t}
          />
          <p className="text-muted-foreground mb-4">
            {t("docs.tutorials.runnerSetup.updating.description")}
          </p>
        </div>
        <UpdateMethods />
      </section>

      {/* Troubleshooting */}
      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">
          {t("docs.tutorials.runnerSetup.troubleshooting.title")}
        </h2>
        <div className="space-y-3">
          <div className="border border-border rounded-lg p-4">
            <p className="text-sm text-muted-foreground">
              {t("docs.tutorials.runnerSetup.troubleshooting.item1")}
            </p>
          </div>
          <div className="border border-border rounded-lg p-4">
            <p className="text-sm text-muted-foreground">
              {t("docs.tutorials.runnerSetup.troubleshooting.item2")}
            </p>
          </div>
          <div className="border border-border rounded-lg p-4">
            <p className="text-sm text-muted-foreground">
              {t("docs.tutorials.runnerSetup.troubleshooting.item3")}
            </p>
          </div>
        </div>
      </section>

      {/* Next Steps */}
      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">
          {t("docs.tutorials.runnerSetup.nextSteps.title")}
        </h2>
        <p className="text-muted-foreground mb-4">
          {t("docs.tutorials.runnerSetup.nextSteps.description")}
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Link
            href="/docs/tutorials/git-setup"
            className="border border-border rounded-lg p-4 hover:border-primary transition-colors"
          >
            <p className="text-sm text-muted-foreground">
              {t("docs.tutorials.runnerSetup.nextSteps.item1")}
            </p>
          </Link>
          <Link
            href="/docs/tutorials/first-pod"
            className="border border-border rounded-lg p-4 hover:border-primary transition-colors"
          >
            <p className="text-sm text-muted-foreground">
              {t("docs.tutorials.runnerSetup.nextSteps.item2")}
            </p>
          </Link>
        </div>
      </section>

      <DocNavigation />
    </div>
  );
}
