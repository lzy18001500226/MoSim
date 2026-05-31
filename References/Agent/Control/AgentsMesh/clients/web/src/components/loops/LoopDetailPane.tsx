"use client";

import { useEffect, useCallback, useState } from "react";
import { useRouter } from "next/navigation";
import { useLoopStore, useCurrentLoop, useLoopRuns } from "@/stores/loop";
import { CenteredSpinner } from "@/components/ui/spinner";
import { LoopCreateDialog } from "@/components/loops/LoopCreateDialog";
import { Button } from "@/components/ui/button";
import { useConfirmDialog, ConfirmDialog } from "@/components/ui/confirm-dialog";
import { AlertCircle, RefreshCw, Loader2 } from "lucide-react";
import { useTranslations } from "next-intl";
import { toast } from "sonner";
import { LoopStatsOverview } from "@/components/loops/LoopStatsOverview";
import { LoopPromptPreview } from "@/components/loops/LoopPromptPreview";
import { LoopRunCard } from "@/components/loops/LoopRunCard";
import {
  LoopHeader,
  LoopConfigSection,
} from "@/app/(dashboard)/[org]/loops/[slug]/components";
import { LoopDetailTabs } from "@/app/(dashboard)/[org]/loops/[slug]/components/LoopDetailTabs";

interface LoopDetailPaneProps {
  slug: string;
  orgSlug: string;
  embedded?: boolean;
}

type TabId = "runs" | "prompt" | "autopilot";

export function LoopDetailPane({ slug, orgSlug, embedded }: LoopDetailPaneProps) {
  const t = useTranslations();
  const router = useRouter();

  const currentLoop = useCurrentLoop();
  const runs = useLoopRuns();
  const runsLoading = useLoopStore((s) => s.runsLoading);
  const runsTotalCount = useLoopStore((s) => s.runsTotalCount);
  const loopLoading = useLoopStore((s) => s.loopLoading);
  const error = useLoopStore((s) => s.error);
  const fetchLoop = useLoopStore((s) => s.fetchLoop);
  const fetchRuns = useLoopStore((s) => s.fetchRuns);
  const triggerLoop = useLoopStore((s) => s.triggerLoop);
  const cancelRun = useLoopStore((s) => s.cancelRun);
  const enableLoop = useLoopStore((s) => s.enableLoop);
  const disableLoop = useLoopStore((s) => s.disableLoop);
  const deleteLoop = useLoopStore((s) => s.deleteLoop);
  const loadMoreRuns = useLoopStore((s) => s.loadMoreRuns);
  const clearError = useLoopStore((s) => s.clearError);
  const setCurrentLoop = useLoopStore((s) => s.setCurrentLoop);

  const [editOpen, setEditOpen] = useState(false);
  const [triggering, setTriggering] = useState(false);
  const [activeTab, setActiveTab] = useState<TabId>("runs");

  const deleteDialog = useConfirmDialog({
    title: t("loops.deleteConfirm"),
    confirmText: t("common.delete"),
    variant: "destructive",
  });

  useEffect(() => {
    fetchLoop(slug);
    fetchRuns(slug, { limit: 20, offset: 0 });
    return () => setCurrentLoop(null);
  }, [slug, fetchLoop, fetchRuns, setCurrentLoop]);

  const handleTrigger = useCallback(async () => {
    setTriggering(true);
    try {
      const result = await triggerLoop(slug);
      if (result.skipped) toast.info(t("loops.triggerSkipped"), { description: result.reason });
      else if (result.run) toast.success(t("loops.triggered"), { description: `Run #${result.run.run_number}` });
    } catch {
      toast.error(t("loops.triggerFailed"));
    } finally {
      setTriggering(false);
    }
  }, [slug, triggerLoop, t]);

  const handleLoadMore = useCallback(() => loadMoreRuns(slug), [slug, loadMoreRuns]);

  const handleCancelRun = useCallback(
    async (runId: number) => {
      try {
        await cancelRun(slug, runId);
        toast.success(t("loops.runCancelled"));
      } catch {
        toast.error(t("loops.cancelFailed"));
      }
    },
    [slug, cancelRun, t],
  );

  const handleOpenRun = useCallback(
    (run: { pod_key?: string }) => {
      if (run.pod_key) router.push(`/${orgSlug}/workspace?pod=${run.pod_key}`);
    },
    [router, orgSlug],
  );

  const handleEnable = useCallback(async () => {
    try {
      await enableLoop(slug);
      toast.success(t("loops.enabled"));
    } catch {
      toast.error(t("loops.enableFailed"));
    }
  }, [slug, enableLoop, t]);

  const handleDisable = useCallback(async () => {
    try {
      await disableLoop(slug);
      toast.success(t("loops.disabled"));
    } catch {
      toast.error(t("loops.disableFailed"));
    }
  }, [slug, disableLoop, t]);

  const handleDelete = useCallback(async () => {
    const confirmed = await deleteDialog.confirm();
    if (!confirmed) return;
    try {
      await deleteLoop(slug);
      toast.success(t("loops.deleted"));
      if (!embedded) router.push(`/${orgSlug}/loops`);
    } catch (err) {
      const message = (err as Error).message;
      const isActiveRunsError = message.includes("active runs");
      toast.error(t("loops.deleteFailed"), {
        description: isActiveRunsError ? t("loops.deleteHasActiveRuns") : message,
      });
    }
  }, [slug, deleteLoop, deleteDialog, router, orgSlug, t, embedded]);

  if (loopLoading && !currentLoop) return <CenteredSpinner className="h-full" />;

  if (error && !currentLoop) {
    return (
      <div className="flex h-full flex-col items-center justify-center py-20 text-center">
        <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-md bg-destructive/10">
          <AlertCircle className="h-6 w-6 text-destructive" />
        </div>
        <p className="mb-3 text-sm text-muted-foreground">{error}</p>
        <Button
          variant="outline"
          size="sm"
          className="gap-1.5"
          onClick={() => {
            clearError();
            fetchLoop(slug);
          }}
        >
          <RefreshCw className="h-3.5 w-3.5" />
          {t("loops.retry")}
        </Button>
      </div>
    );
  }

  if (!currentLoop) return null;

  const tabs = [
    { id: "runs", label: t("loops.tabs.runs") },
    { id: "prompt", label: t("loops.tabs.prompt") },
    { id: "autopilot", label: t("loops.tabs.autopilot") },
  ];

  const visibleRuns = runs.slice(0, 6);
  const hasMoreToShow = runs.length > 6 || runs.length < runsTotalCount;

  return (
    <div className="flex h-full flex-col overflow-hidden">
      <div className="px-8 pt-6">
        <LoopHeader
          loop={currentLoop}
          triggering={triggering}
          t={t}
          onTrigger={handleTrigger}
          onEdit={() => setEditOpen(true)}
          onEnable={handleEnable}
          onDisable={handleDisable}
          onDelete={handleDelete}
        />
      </div>

      <div className="px-8">
        <LoopDetailTabs
          active={activeTab}
          onChange={(id) => setActiveTab(id as TabId)}
          tabs={tabs}
        />
      </div>

      <div className="flex-1 overflow-y-auto px-8 py-6">
        {activeTab === "runs" && (
          <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_360px]">
            <section>
              <div className="mb-3 flex items-center justify-between">
                <h2 className="text-sm font-semibold text-foreground">{t("loops.recentRuns")}</h2>
                <span className="text-xs text-muted-foreground">
                  {t("loops.showingLast", { count: visibleRuns.length, total: runsTotalCount })}
                </span>
              </div>

              {runsLoading && runs.length === 0 ? (
                <div className="flex items-center justify-center rounded-md border border-border py-10">
                  <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                </div>
              ) : runs.length === 0 ? (
                <div className="rounded-md border border-border bg-muted/30 p-6 text-center text-sm text-muted-foreground">
                  {t("loops.noRuns")}
                </div>
              ) : (
                <div className="flex flex-col gap-2">
                  {visibleRuns.map((run) => (
                    <LoopRunCard
                      key={run.id}
                      run={run}
                      t={t}
                      onOpen={handleOpenRun}
                      onCancel={handleCancelRun}
                    />
                  ))}
                  {hasMoreToShow && (
                    <button
                      type="button"
                      className="mt-1 self-center text-xs font-medium text-primary hover:underline disabled:opacity-60"
                      disabled={runsLoading}
                      onClick={handleLoadMore}
                    >
                      {runsLoading ? t("loops.loadMore") : t("loops.viewAll")} →
                    </button>
                  )}
                </div>
              )}
            </section>

            <aside className="flex flex-col gap-4">
              <LoopStatsOverview loop={currentLoop} t={t} />
              <LoopPromptPreview loop={currentLoop} t={t} onEdit={() => setEditOpen(true)} />
            </aside>
          </div>
        )}

        {activeTab === "prompt" && (
          <div className="space-y-4">
            <LoopConfigSection loop={currentLoop} orgSlug={orgSlug} t={t} />
          </div>
        )}

        {activeTab === "autopilot" && (
          <div className="rounded-md border border-border bg-muted/30 p-6 text-sm text-muted-foreground">
            {t("loops.tabs.autopilotEmpty")}
          </div>
        )}
      </div>

      <LoopCreateDialog
        open={editOpen}
        onOpenChange={setEditOpen}
        onCreated={() => {
          setEditOpen(false);
          fetchLoop(slug);
        }}
        editLoop={currentLoop}
      />
      <ConfirmDialog {...deleteDialog.dialogProps} />
    </div>
  );
}
