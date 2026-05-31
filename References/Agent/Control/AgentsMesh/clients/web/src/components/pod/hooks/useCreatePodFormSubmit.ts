import type { PodData } from "@/lib/api";
import { createPod } from "@/lib/api/facade/podConnect";
import { readCurrentOrg } from "@/stores/auth";

export interface CreatePodResult {
  pod: PodData;
  warning?: string;
}

export async function submitCreatePod(params: {
  selectedAgent: string;
  alias: string;
  perpetual?: boolean;
  selectedRunnerId: number | null | undefined;
  agentfileLayer?: string;
  options?: { ticketSlug?: string; cols?: number; rows?: number };
}): Promise<CreatePodResult | null> {
  const { selectedAgent, alias, perpetual, selectedRunnerId, agentfileLayer, options } = params;

  const result = await createPod(readCurrentOrg()?.slug ?? "", {
    agent_slug: selectedAgent,
    runner_id: selectedRunnerId || undefined,
    alias: alias.trim() || undefined,
    ticket_slug: options?.ticketSlug,
    cols: options?.cols,
    rows: options?.rows,
    agentfile_layer: agentfileLayer || undefined,
    perpetual: perpetual || undefined,
  });

  if (!result?.pod) return null;
  return { pod: result.pod, warning: result.warning };
}
