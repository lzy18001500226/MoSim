import { useState, useEffect, useMemo } from "react";
import { useCurrentUser, useCurrentOrg, useAuthStore } from "@/stores/auth";
import { usePods } from "@/stores/pod";
import { organizationApi } from "@/lib/api/facade/organization";
import type { OrganizationMember } from "@/lib/api/facade/org";
import { useChannelPods } from "@/hooks/useChannelPods";
import { getPodDisplayName, getMentionSafeName, getShortPodKey } from "@/lib/pod-display-name";

export interface MentionItem {
  id: string;
  type: "user" | "pod";
  mentionText: string;
  displayName: string;
  description?: string;
  avatarUrl?: string;
}

interface ChannelPodRaw {
  pod_key: string;
  alias?: string;
  status: string;
}

interface UseMentionCandidatesOptions {
  channelId: number | null;
  enabled?: boolean;
}

export function useMentionCandidates({
  channelId,
  enabled = true,
}: UseMentionCandidatesOptions) {
  const currentOrg = useCurrentOrg();
  const user = useCurrentUser();
  const allPods = usePods();
  const [members, setMembers] = useState<MentionItem[]>([]);
  const [loading, setLoading] = useState(false);

  const { pods: sharedChannelPods, loading: podsLoading } = useChannelPods(
    enabled ? channelId : null,
  );
  const rawChannelPods = useMemo<ChannelPodRaw[]>(
    () =>
      sharedChannelPods
        .filter((p) => p.status === "running" || p.status === "initializing")
        .map((p) => ({ pod_key: p.pod_key, alias: p.alias, status: p.status })),
    [sharedChannelPods],
  );

  const orgSlug = currentOrg?.slug;
  useEffect(() => {
    if (!enabled || !orgSlug) return;

    let cancelled = false;

    async function fetchMembers() {
      try {
        const response = await organizationApi.listMembers(orgSlug!);
        if (cancelled) return;

        const memberItems: MentionItem[] = (response.members || [])
          .filter(
            (m): m is OrganizationMember & {
              user: NonNullable<OrganizationMember["user"]>;
            } => !!m.user && Number(m.user.id) !== user?.id,
          )
          .map((m) => ({
            id: `user:${Number(m.user.id)}`,
            type: "user" as const,
            mentionText: m.user.username,
            displayName: m.user.name || m.user.username,
            description: m.user.email,
            avatarUrl: m.user.avatarUrl,
          }));

        setMembers(memberItems);
      } catch (error) {
        console.error("Failed to fetch members for mentions:", error);
      }
    }

    fetchMembers();

    return () => {
      cancelled = true;
    };
  }, [orgSlug, enabled, user?.id]);

  const pods: MentionItem[] = useMemo(
    () =>
      rawChannelPods.map((p) => {
        const storePod = allPods.find((sp) => sp.pod_key === p.pod_key);
        const displayName = storePod
          ? getPodDisplayName(storePod)
          : p.alias || getShortPodKey(p.pod_key);
        const mentionText = storePod
          ? getMentionSafeName(storePod)
          : (p.alias?.replace(/\s+/g, "_") || getShortPodKey(p.pod_key));
        return {
          id: `pod:${p.pod_key}`,
          type: "pod" as const,
          mentionText,
          displayName,
          description: `Pod ${p.status}`,
        };
      }),
    [rawChannelPods, allPods]
  );

  const candidates = useMemo(
    () => [...members, ...pods],
    [members, pods]
  );

  return { candidates, members, pods, loading: loading || podsLoading };
}
