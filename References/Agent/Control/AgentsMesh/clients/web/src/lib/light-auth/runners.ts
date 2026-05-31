// Runner CRUD over Connect-RPC JSON. GetRunnerAuthStatus is public (no JWT
// — the auth key IS the auth); AuthorizeRunner / CreateRunnerToken /
// ListRunners require the user's bearer token.

import { lightConnect } from "./api-fetch";
import type { RunnerAuthStatus, RunnerData } from "@/lib/viewModels/runner";

interface ConnectRunnerAuthStatus {
  status: string;
  nodeId?: string;
  expiresAt?: string;
}

export async function lightGetRunnerAuthStatus(authKey: string): Promise<RunnerAuthStatus> {
  const resp = await lightConnect<{ authKey: string }, ConnectRunnerAuthStatus>(
    "proto.runner_api.v1.RunnerPublicService",
    "GetRunnerAuthStatus",
    { authKey },
  );
  return {
    status: resp.status as RunnerAuthStatus["status"],
    node_id: resp.nodeId,
    expires_at: resp.expiresAt,
  };
}

export interface LightAuthorizeRunnerInput {
  organizationSlug: string;
  authKey: string;
  nodeId?: string;
}

interface ConnectAuthorizeRunnerResponse {
  runnerId?: number | string;
  nodeId?: string;
  message?: string;
}

export async function lightAuthorizeRunner(
  input: LightAuthorizeRunnerInput,
): Promise<{ runner_id?: number; node_id?: string; message?: string }> {
  const resp = await lightConnect<
    { orgSlug: string; authKey: string; nodeId: string },
    ConnectAuthorizeRunnerResponse
  >(
    "proto.runner_api.v1.RunnerService",
    "AuthorizeRunner",
    {
      orgSlug: input.organizationSlug,
      authKey: input.authKey,
      nodeId: input.nodeId ?? "",
    },
    { authenticated: true },
  );
  return {
    runner_id: resp.runnerId !== undefined ? Number(resp.runnerId) : undefined,
    node_id: resp.nodeId,
    message: resp.message,
  };
}

// Used by the onboarding "Setup local runner" step. Creates a single-use
// registration token bound to the current organization so the user can
// paste it into the `runner register` CLI command.
interface ConnectCreateRunnerTokenResponse {
  token?: string;
}

export async function lightCreateRunnerToken(orgSlug: string): Promise<string | null> {
  const resp = await lightConnect<{ orgSlug: string; labels: string[] }, ConnectCreateRunnerTokenResponse>(
    "proto.runner_api.v1.RunnerService",
    "CreateRunnerToken",
    { orgSlug, labels: [] },
    { authenticated: true },
  );
  return resp?.token ?? null;
}

interface ConnectListRunnersResponse {
  items?: Array<{
    id: number | string;
    nodeId?: string;
    [key: string]: unknown;
  }>;
}

export async function lightListRunners(orgSlug: string): Promise<RunnerData[]> {
  const resp = await lightConnect<{ orgSlug: string }, ConnectListRunnersResponse>(
    "proto.runner_api.v1.RunnerService",
    "ListRunners",
    { orgSlug },
    { authenticated: true },
  );
  // The runners/authorize page only needs id + node_id + a few status
  // fields, so a shallow remap is enough — full RunnerData hydration
  // happens in wasm-land once the user reaches the dashboard.
  return (resp?.items ?? []).map((r) => ({
    id: Number(r.id),
    node_id: r.nodeId ?? "",
    status: (r as { status?: string }).status as RunnerData["status"],
    current_pods: Number((r as { currentPods?: number }).currentPods ?? 0),
    max_concurrent_pods: Number((r as { maxConcurrentPods?: number }).maxConcurrentPods ?? 0),
    is_enabled: Boolean((r as { isEnabled?: boolean }).isEnabled),
  } as RunnerData));
}
