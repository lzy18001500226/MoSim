"use client";

import React, { useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useCurrentUser, useCurrentOrg, useAuthStore } from "@/stores/auth";
import { useChannelMessageStore } from "@/stores/channelMessageStore";
import { ResponsiveShell } from "@/components/layout";
import { RealtimeProvider } from "@/providers/RealtimeProvider";
import { getAuthManager } from "@/lib/wasm-core";
import { useBrowserNotification } from "@/hooks";
import { handleNotificationEvent } from "@/stores/notificationHandler";
import type { RealtimeEvent } from "@/lib/realtime";

// Mounted under <RequireAuth>, so `user` is non-null whenever this
// component renders. Dashboard-specific concerns only: URL-slug →
// switch_org routing helper, browser-notification permission prompt,
// channels-unread refresh on org change, and realtime event dispatch.
export default function DashboardShell({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const user = useCurrentUser();
  const currentOrg = useCurrentOrg();
  const _hasHydrated = useAuthStore((s) => s._hasHydrated);
  const { permission, showNotification, requestPermission } = useBrowserNotification();

  // URL-slug → switch_org: a deep link to /{otherOrg}/... should win over
  // the persisted current_org_slug that bootstrap restored.
  useEffect(() => {
    if (!_hasHydrated) return;
    try {
      const orgs = JSON.parse(getAuthManager().get_organizations_json() || "[]");
      if (orgs.length === 0) return;
      const urlSlug = window.location.pathname.split("/")[1];
      const matchedOrg = orgs.find((o: { slug: string }) => o.slug === urlSlug);
      if (matchedOrg) {
        getAuthManager().switch_org(matchedOrg.slug);
        useAuthStore.getState().setCurrentOrg(matchedOrg);
      }
    } catch { /* noop */ }
  }, [_hasHydrated]);

  useEffect(() => {
    if (user && permission === "default") {
      const timer = setTimeout(() => { requestPermission(); }, 3000);
      return () => clearTimeout(timer);
    }
  }, [user, permission, requestPermission]);

  // Cross-cutting org-scoped state (e.g. ActivityBar's channels-unread
  // badge sits outside the org layout's gate) — refresh on org change.
  useEffect(() => {
    if (!currentOrg) return;
    void useChannelMessageStore.getState().fetchUnreadCounts();
  }, [currentOrg]);

  const handleEvent = useCallback(
    (event: RealtimeEvent) => {
      handleNotificationEvent(event, {
        router,
        showBrowserNotification: (data) => {
          showNotification({
            title: data.title,
            body: data.body,
            tag: `notif-${data.link || data.title}`,
            onClick: () => {
              if (data.link && currentOrg?.slug) {
                router.push(`/${currentOrg.slug}${data.link}`);
              }
            },
          });
        },
      });
    },
    [showNotification, router, currentOrg]
  );

  return (
    <RealtimeProvider onEvent={handleEvent}>
      <ResponsiveShell>{children}</ResponsiveShell>
    </RealtimeProvider>
  );
}
