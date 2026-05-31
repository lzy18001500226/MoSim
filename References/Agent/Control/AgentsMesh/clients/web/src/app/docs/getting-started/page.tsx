"use client";

import Link from "next/link";
import { useServerUrl } from "@/hooks/useServerUrl";
import { useTranslations } from "next-intl";
import { DocNavigation } from "@/components/docs/DocNavigation";

function StepHeader({ step, titleKey, t }: { step: number; titleKey: string; t: ReturnType<typeof useTranslations> }) {
  return (
    <div className="flex items-center gap-3 mb-4">
      <div className="w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-sm font-bold">
        {step}
      </div>
      <h2 className="text-xl font-semibold">{t(titleKey)}</h2>
    </div>
  );
}

function LinkInText({ raw, linkHref, linkLabel }: { raw: string; linkHref: string; linkLabel: string }) {
  const parts = raw.split("{link}");
  if (parts.length < 2) return <>{raw}</>;
  return (
    <>
      {parts[0]}
      <Link href={linkHref} className="text-primary hover:underline">
        {linkLabel}
      </Link>
      {parts[1]}
    </>
  );
}

export default function GettingStartedPage() {
  const serverUrl = useServerUrl();
  const t = useTranslations();

  return (
    <div>
      <h1 className="text-4xl font-bold mb-8">
        {t("docs.gettingStarted.title")}
      </h1>

      <p className="text-muted-foreground leading-relaxed mb-8">
        {t("docs.gettingStarted.description")}
      </p>

      {/* Step 1: Create an Account */}
      <section className="mb-8">
        <div className="border border-border rounded-lg p-6">
          <StepHeader step={1} titleKey="docs.gettingStarted.step1.title" t={t} />
          <p className="text-muted-foreground mb-4">
            {t("docs.gettingStarted.step1.description")}
          </p>
          <div className="bg-muted rounded-lg p-4 text-sm">
            <p className="font-medium mb-2">
              {t("docs.gettingStarted.step1.whatYouGet")}
            </p>
            <ul className="list-disc list-inside text-muted-foreground space-y-1">
              <li>{t("docs.gettingStarted.step1.item1")}</li>
              <li>{t("docs.gettingStarted.step1.item2")}</li>
            </ul>
          </div>
        </div>
      </section>

      {/* Step 2: Setup a Runner */}
      <section className="mb-8">
        <div className="border border-border rounded-lg p-6">
          <StepHeader step={2} titleKey="docs.gettingStarted.step2.title" t={t} />
          <p className="text-muted-foreground mb-4">
            {t("docs.gettingStarted.step2.description")}
          </p>
          <div className="bg-muted rounded-lg p-4 font-mono text-sm overflow-x-auto mb-4">
            <pre className="text-green-500 dark:text-green-400">{`# Download and install the runner
curl -fsSL ${serverUrl}/install.sh | sh`}</pre>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div className="bg-muted rounded-lg p-4">
              <h4 className="font-medium mb-2">
                {t("docs.gettingStarted.step2.methodToken")}
              </h4>
              <div className="font-mono text-sm overflow-x-auto">
                <pre className="text-green-500 dark:text-green-400">{`agentsmesh-runner register \\
  --server ${serverUrl} \\
  --token <YOUR_TOKEN>
agentsmesh-runner run`}</pre>
              </div>
            </div>
            <div className="bg-muted rounded-lg p-4">
              <h4 className="font-medium mb-2">
                {t("docs.gettingStarted.step2.methodLogin")}
              </h4>
              <div className="font-mono text-sm overflow-x-auto">
                <pre className="text-green-500 dark:text-green-400">{`agentsmesh-runner login
agentsmesh-runner run`}</pre>
              </div>
            </div>
          </div>

          <p className="text-sm text-muted-foreground">
            <LinkInText
              raw={t.raw("docs.gettingStarted.step2.seeSetup")}
              linkHref="/docs/runners/setup"
              linkLabel={t("docs.nav.runnerSetup")}
            />
          </p>
        </div>
      </section>

      {/* Step 3: Install AI Agent CLIs */}
      <section className="mb-8">
        <div className="border border-border rounded-lg p-6">
          <StepHeader step={3} titleKey="docs.gettingStarted.step3.title" t={t} />
          <p className="text-muted-foreground mb-4">
            {t("docs.gettingStarted.step3.description")}
          </p>

          <div className="space-y-4">
            {/* Claude Code */}
            <div className="bg-muted rounded-lg p-4">
              <h4 className="font-medium mb-2">
                {t("docs.gettingStarted.step3.claudeCode")}
              </h4>
              <div className="font-mono text-sm overflow-x-auto space-y-1">
                <pre className="text-green-500 dark:text-green-400">{t("docs.gettingStarted.step3.claudeCodeInstall")}</pre>
                <pre className="text-green-500 dark:text-green-400">{t("docs.gettingStarted.step3.claudeCodeEnv")}</pre>
              </div>
              <p className="text-sm text-muted-foreground mt-2">
                {t("docs.gettingStarted.step3.claudeCodeHint")}{" "}
                <a
                  href="https://console.anthropic.com"
                  className="text-primary hover:underline"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  console.anthropic.com
                </a>
              </p>
            </div>

            {/* Codex CLI */}
            <div className="bg-muted rounded-lg p-4">
              <h4 className="font-medium mb-2">
                {t("docs.gettingStarted.step3.codexCli")}
              </h4>
              <div className="font-mono text-sm overflow-x-auto space-y-1">
                <pre className="text-green-500 dark:text-green-400">{t("docs.gettingStarted.step3.codexCliInstall")}</pre>
                <pre className="text-green-500 dark:text-green-400">{t("docs.gettingStarted.step3.codexCliEnv")}</pre>
              </div>
              <p className="text-sm text-muted-foreground mt-2">
                {t("docs.gettingStarted.step3.codexCliHint")}{" "}
                <a
                  href="https://platform.openai.com"
                  className="text-primary hover:underline"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  platform.openai.com
                </a>
              </p>
            </div>

            {/* Gemini CLI */}
            <div className="bg-muted rounded-lg p-4">
              <h4 className="font-medium mb-2">
                {t("docs.gettingStarted.step3.geminiCli")}
              </h4>
              <div className="font-mono text-sm overflow-x-auto space-y-1">
                <pre className="text-green-500 dark:text-green-400">{t("docs.gettingStarted.step3.geminiCliInstall")}</pre>
                <pre className="text-green-500 dark:text-green-400">{t("docs.gettingStarted.step3.geminiCliEnv")}</pre>
              </div>
              <p className="text-sm text-muted-foreground mt-2">
                {t("docs.gettingStarted.step3.geminiCliHint")}{" "}
                <a
                  href="https://aistudio.google.com"
                  className="text-primary hover:underline"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  aistudio.google.com
                </a>
              </p>
            </div>
          </div>

          <div className="bg-muted/50 border border-border rounded-lg p-4 mt-4 text-sm text-muted-foreground">
            {t("docs.gettingStarted.step3.tip")}
          </div>

          <p className="text-sm text-muted-foreground mt-4">
            <LinkInText
              raw={t.raw("docs.gettingStarted.step3.seeSetup")}
              linkHref="/docs/tutorials/mcp-and-skills"
              linkLabel={t("docs.nav.tutorialMcpSkills")}
            />
          </p>
        </div>
      </section>

      {/* Step 4: Connect a Git Provider */}
      <section className="mb-8">
        <div className="border border-border rounded-lg p-6">
          <StepHeader step={4} titleKey="docs.gettingStarted.step4.title" t={t} />
          <p className="text-muted-foreground mb-4">
            {t("docs.gettingStarted.step4.description")}
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div className="bg-muted rounded-lg p-4">
              <h4 className="font-medium mb-2">
                {t("docs.gettingStarted.step4.github")}
              </h4>
              <p className="text-sm text-muted-foreground">
                {t("docs.gettingStarted.step4.githubDesc")}{" "}
                <a
                  href="https://github.com/settings/tokens"
                  className="text-primary hover:underline"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {t("docs.gettingStarted.step4.githubTokenUrl")}
                </a>
              </p>
            </div>
            <div className="bg-muted rounded-lg p-4">
              <h4 className="font-medium mb-2">
                {t("docs.gettingStarted.step4.gitlab")}
              </h4>
              <p className="text-sm text-muted-foreground">
                {t("docs.gettingStarted.step4.gitlabDesc")}
              </p>
            </div>
          </div>
          <p className="text-sm text-muted-foreground">
            <LinkInText
              raw={t.raw("docs.gettingStarted.step4.seeGuide")}
              linkHref="/docs/tutorials/git-setup"
              linkLabel={t("docs.nav.tutorialGitSetup")}
            />
          </p>
        </div>
      </section>

      {/* Step 5: Start a Pod */}
      <section className="mb-8">
        <div className="border border-border rounded-lg p-6">
          <StepHeader step={5} titleKey="docs.gettingStarted.step5.title" t={t} />
          <p className="text-muted-foreground mb-4">
            {t("docs.gettingStarted.step5.description")}
          </p>
          <ol className="list-decimal list-inside text-muted-foreground space-y-2">
            <li>{t("docs.gettingStarted.step5.item1")}</li>
            <li>{t("docs.gettingStarted.step5.item2")}</li>
            <li>{t("docs.gettingStarted.step5.item3")}</li>
            <li>{t("docs.gettingStarted.step5.item4")}</li>
            <li>{t("docs.gettingStarted.step5.item5")}</li>
            <li>{t("docs.gettingStarted.step5.item6")}</li>
            <li>{t("docs.gettingStarted.step5.item7")}</li>
            <li>{t("docs.gettingStarted.step5.item8")}</li>
          </ol>

          <p className="text-sm text-muted-foreground mt-4">
            <LinkInText
              raw={t.raw("docs.gettingStarted.step5.seeSetup")}
              linkHref="/docs/tutorials/first-pod"
              linkLabel={t("docs.nav.tutorialFirstPod")}
            />
          </p>
        </div>
      </section>

      {/* Step 6: Interact with Your Agent */}
      <section className="mb-8">
        <div className="border border-border rounded-lg p-6">
          <StepHeader step={6} titleKey="docs.gettingStarted.step6.title" t={t} />
          <p className="text-muted-foreground mb-4">
            {t("docs.gettingStarted.step6.description")}
          </p>
          <ul className="list-disc list-inside text-muted-foreground space-y-2">
            <li>{t("docs.gettingStarted.step6.item1")}</li>
            <li>{t("docs.gettingStarted.step6.item2")}</li>
            <li>{t("docs.gettingStarted.step6.item3")}</li>
            <li>{t("docs.gettingStarted.step6.item4")}</li>
          </ul>
        </div>
      </section>

      {/* Try It */}
      <section className="mb-8">
        <div className="bg-primary/5 border border-primary/20 rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">
            {t("docs.gettingStarted.tryIt.title")}
          </h2>
          <p className="text-muted-foreground mb-4">
            {t("docs.gettingStarted.tryIt.description")}
          </p>
          <ol className="list-decimal list-inside text-muted-foreground space-y-2 mb-4">
            <li>{t("docs.gettingStarted.tryIt.item1")}</li>
            <li>{t("docs.gettingStarted.tryIt.item2")}</li>
            <li>{t("docs.gettingStarted.tryIt.item3")}</li>
            <li>{t("docs.gettingStarted.tryIt.item4")}</li>
            <li>{t("docs.gettingStarted.tryIt.item5")}</li>
          </ol>
          <div className="bg-muted/50 border border-border rounded-lg p-4 text-sm text-muted-foreground">
            {t("docs.gettingStarted.tryIt.tip")}
          </div>
        </div>
      </section>

      {/* Next Steps */}
      <section className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">
          {t("docs.gettingStarted.nextSteps.title")}
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Link
            href="/docs/features/agentpod"
            className="border border-border rounded-lg p-4 hover:border-primary transition-colors"
          >
            <h3 className="font-medium mb-1">
              {t("docs.gettingStarted.nextSteps.agentpod")}
            </h3>
            <p className="text-sm text-muted-foreground">
              {t("docs.gettingStarted.nextSteps.agentpodDesc")}
            </p>
          </Link>
          <Link
            href="/docs/features/mesh"
            className="border border-border rounded-lg p-4 hover:border-primary transition-colors"
          >
            <h3 className="font-medium mb-1">
              {t("docs.gettingStarted.nextSteps.mesh")}
            </h3>
            <p className="text-sm text-muted-foreground">
              {t("docs.gettingStarted.nextSteps.meshDesc")}
            </p>
          </Link>
          <Link
            href="/docs/features/tickets"
            className="border border-border rounded-lg p-4 hover:border-primary transition-colors"
          >
            <h3 className="font-medium mb-1">
              {t("docs.gettingStarted.nextSteps.tickets")}
            </h3>
            <p className="text-sm text-muted-foreground">
              {t("docs.gettingStarted.nextSteps.ticketsDesc")}
            </p>
          </Link>
          <Link
            href="/docs/guides/multi-agent-workflows"
            className="border border-border rounded-lg p-4 hover:border-primary transition-colors"
          >
            <h3 className="font-medium mb-1">
              {t("docs.gettingStarted.nextSteps.multiAgent")}
            </h3>
            <p className="text-sm text-muted-foreground">
              {t("docs.gettingStarted.nextSteps.multiAgentDesc")}
            </p>
          </Link>
        </div>
      </section>

      <DocNavigation />
    </div>
  );
}
