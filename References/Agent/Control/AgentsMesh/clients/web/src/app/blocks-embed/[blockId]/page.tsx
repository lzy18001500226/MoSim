"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams, useSearchParams } from "next/navigation";
import { DocumentView } from "@/components/blocks/DocumentView";
import { CenteredSpinner } from "@/components/ui/spinner";
import { useBlockstoreStore } from "@/stores/blockstore";
import {
  setupIosBridge, ensurePlatformReady, primeSubtreeCache,
} from "@/lib/ios-bridge/init";

export default function BlocksEmbedPage() {
  const params = useParams<{ blockId: string }>();
  const searchParams = useSearchParams();
  const blockId = params?.blockId;
  const wsId = searchParams.get("wsId") ?? "";

  const [ready, setReady] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        if (!blockId || !wsId) {
          throw new Error("Missing wsId or blockId in embed URL");
        }
        setupIosBridge();
        await ensurePlatformReady();
        useBlockstoreStore.getState().actions.setActiveWorkspaceId(wsId);
        await primeSubtreeCache(wsId, blockId);
        await useBlockstoreStore.getState().actions.loadSubtree(wsId, blockId);
        if (!cancelled) setReady(true);
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : String(e));
      }
    })();
    return () => { cancelled = true; };
  }, [blockId, wsId]);

  const content = useMemo(() => {
    if (error) return <div className="p-4 text-sm text-destructive">{error}</div>;
    if (!ready || !blockId || !wsId) return <CenteredSpinner />;
    return (
      <div className="min-h-0 flex-1 overflow-y-auto">
        <DocumentView workspaceID={wsId} rootBlockID={blockId} />
      </div>
    );
  }, [ready, error, blockId, wsId]);

  return (
    <div
      className="flex h-full min-h-screen w-full flex-col bg-background text-foreground"
      data-am-embed-mode="ios"
    >
      {content}
    </div>
  );
}
