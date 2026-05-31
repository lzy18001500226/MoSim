"use client";

import { useTranslations } from "next-intl";
import { DocNavigation } from "@/components/docs/DocNavigation";

export default function RepositoriesGitPage() {
  const t = useTranslations();

  return (
    <div>
      <h1 className="text-4xl font-bold mb-8">
        {t("docs.concepts.repositoriesGit.title")}
      </h1>

      <p className="text-muted-foreground leading-relaxed mb-8">
        {t("docs.concepts.repositoriesGit.description")}
      </p>

      {/* Overview */}
      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4">
          {t("docs.concepts.repositoriesGit.overview.title")}
        </h2>
        <p className="text-muted-foreground leading-relaxed">
          {t("docs.concepts.repositoriesGit.overview.description")}
        </p>
      </section>

      {/* Supported Git Providers */}
      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4">
          {t("docs.concepts.repositoriesGit.providers.title")}
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="border border-border rounded-lg p-4">
            <h3 className="font-medium mb-2">
              {t("docs.concepts.repositoriesGit.providers.github")}
            </h3>
            <p className="text-sm text-muted-foreground">
              {t("docs.concepts.repositoriesGit.providers.githubDesc")}
            </p>
          </div>
          <div className="border border-border rounded-lg p-4">
            <h3 className="font-medium mb-2">
              {t("docs.concepts.repositoriesGit.providers.gitlab")}
            </h3>
            <p className="text-sm text-muted-foreground">
              {t("docs.concepts.repositoriesGit.providers.gitlabDesc")}
            </p>
          </div>
          <div className="border border-border rounded-lg p-4">
            <h3 className="font-medium mb-2">
              {t("docs.concepts.repositoriesGit.providers.gitee")}
            </h3>
            <p className="text-sm text-muted-foreground">
              {t("docs.concepts.repositoriesGit.providers.giteeDesc")}
            </p>
          </div>
        </div>
      </section>

      {/* Connecting GitHub */}
      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4">
          {t("docs.concepts.repositoriesGit.github.title")}
        </h2>
        <p className="text-muted-foreground leading-relaxed mb-4">
          {t("docs.concepts.repositoriesGit.github.description")}
        </p>
        <div className="space-y-4">
          <div className="border border-border rounded-lg p-6">
            <h3 className="font-medium mb-2">
              {t("docs.concepts.repositoriesGit.github.patTitle")}
            </h3>
            <p className="text-sm text-muted-foreground mb-3">
              {t("docs.concepts.repositoriesGit.github.patDesc")}
            </p>
            <ol className="list-decimal list-inside text-muted-foreground space-y-3">
              <li>{t("docs.concepts.repositoriesGit.github.step1")}</li>
              <li>{t("docs.concepts.repositoriesGit.github.step2")}</li>
              <li>{t("docs.concepts.repositoriesGit.github.step3")}</li>
              <li>{t("docs.concepts.repositoriesGit.github.step4")}</li>
              <li>{t("docs.concepts.repositoriesGit.github.step5")}</li>
            </ol>
          </div>
          <div className="border border-border rounded-lg p-6">
            <h3 className="font-medium mb-2">
              {t("docs.concepts.repositoriesGit.github.oauthTitle")}
            </h3>
            <p className="text-sm text-muted-foreground mb-3">
              {t("docs.concepts.repositoriesGit.github.oauthDesc")}
            </p>
            <ol className="list-decimal list-inside text-muted-foreground space-y-3">
              <li>{t("docs.concepts.repositoriesGit.github.oauthStep1")}</li>
              <li>{t("docs.concepts.repositoriesGit.github.oauthStep2")}</li>
              <li>{t("docs.concepts.repositoriesGit.github.oauthStep3")}</li>
            </ol>
            <div className="bg-muted/50 border border-border rounded-lg p-4 mt-4 text-sm text-muted-foreground">
              {t("docs.concepts.repositoriesGit.github.oauthNote")}
            </div>
          </div>
        </div>
      </section>

      {/* Connecting GitLab */}
      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4">
          {t("docs.concepts.repositoriesGit.gitlab.title")}
        </h2>
        <p className="text-muted-foreground leading-relaxed mb-4">
          {t("docs.concepts.repositoriesGit.gitlab.description")}
        </p>
        <div className="border border-border rounded-lg p-6">
          <ol className="list-decimal list-inside text-muted-foreground space-y-3">
            <li>{t("docs.concepts.repositoriesGit.gitlab.step1")}</li>
            <li>{t("docs.concepts.repositoriesGit.gitlab.step2")}</li>
            <li>{t("docs.concepts.repositoriesGit.gitlab.step3")}</li>
            <li>{t("docs.concepts.repositoriesGit.gitlab.step4")}</li>
            <li>{t("docs.concepts.repositoriesGit.gitlab.step5")}</li>
          </ol>
          <div className="bg-muted rounded-lg p-4 mt-4">
            <p className="text-sm text-muted-foreground">
              {t("docs.concepts.repositoriesGit.gitlab.selfHosted")}
            </p>
          </div>
        </div>
      </section>

      {/* Connecting Gitee */}
      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4">
          {t("docs.concepts.repositoriesGit.gitee.title")}
        </h2>
        <p className="text-muted-foreground leading-relaxed mb-4">
          {t("docs.concepts.repositoriesGit.gitee.description")}
        </p>
        <div className="border border-border rounded-lg p-6">
          <ol className="list-decimal list-inside text-muted-foreground space-y-3">
            <li>{t("docs.concepts.repositoriesGit.gitee.step1")}</li>
            <li>{t("docs.concepts.repositoriesGit.gitee.step2")}</li>
            <li>{t("docs.concepts.repositoriesGit.gitee.step3")}</li>
            <li>{t("docs.concepts.repositoriesGit.gitee.step4")}</li>
          </ol>
        </div>
      </section>

      {/* SSH Keys */}
      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4">
          {t("docs.concepts.repositoriesGit.sshKeys.title")}
        </h2>
        <p className="text-muted-foreground leading-relaxed mb-4">
          {t("docs.concepts.repositoriesGit.sshKeys.description")}
        </p>
        <div className="border border-border rounded-lg p-6">
          <ol className="list-decimal list-inside text-muted-foreground space-y-3">
            <li>{t("docs.concepts.repositoriesGit.sshKeys.step1")}</li>
            <li>{t("docs.concepts.repositoriesGit.sshKeys.step2")}</li>
            <li>{t("docs.concepts.repositoriesGit.sshKeys.step3")}</li>
          </ol>
          <div className="bg-muted rounded-lg p-4 mt-4">
            <p className="text-sm text-muted-foreground">
              {t("docs.concepts.repositoriesGit.sshKeys.dockerNote")}
            </p>
          </div>
        </div>
      </section>

      {/* Using Repositories in Pods */}
      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4">
          {t("docs.concepts.repositoriesGit.podUsage.title")}
        </h2>
        <p className="text-muted-foreground leading-relaxed mb-4">
          {t("docs.concepts.repositoriesGit.podUsage.description")}
        </p>
        <div className="border border-border rounded-lg p-6">
          <ol className="list-decimal list-inside text-muted-foreground space-y-3">
            <li>{t("docs.concepts.repositoriesGit.podUsage.step1")}</li>
            <li>{t("docs.concepts.repositoriesGit.podUsage.step2")}</li>
            <li>{t("docs.concepts.repositoriesGit.podUsage.step3")}</li>
            <li>{t("docs.concepts.repositoriesGit.podUsage.step4")}</li>
          </ol>
        </div>
      </section>

      {/* Git Worktree Isolation */}
      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4">
          {t("docs.concepts.repositoriesGit.worktree.title")}
        </h2>
        <p className="text-muted-foreground leading-relaxed">
          {t("docs.concepts.repositoriesGit.worktree.description")}
        </p>
      </section>

      {/* Managing Repositories */}
      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4">
          {t("docs.concepts.repositoriesGit.management.title")}
        </h2>
        <div className="space-y-4">
          <div className="border border-border rounded-lg p-4">
            <h3 className="font-medium mb-2">
              {t("docs.concepts.repositoriesGit.management.addRepo")}
            </h3>
            <p className="text-sm text-muted-foreground">
              {t("docs.concepts.repositoriesGit.management.addRepoSteps")}
            </p>
          </div>
          <div className="border border-border rounded-lg p-4">
            <h3 className="font-medium mb-2">
              {t("docs.concepts.repositoriesGit.management.removeRepo")}
            </h3>
            <p className="text-sm text-muted-foreground">
              {t("docs.concepts.repositoriesGit.management.removeRepoSteps")}
            </p>
          </div>
        </div>
      </section>

      <DocNavigation />
    </div>
  );
}
