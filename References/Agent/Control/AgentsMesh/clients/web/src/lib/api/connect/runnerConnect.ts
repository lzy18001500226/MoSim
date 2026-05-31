// Connect-RPC adapter for proto.runner_api.v1.RunnerService.
//
// Encodes requests via @bufbuild/protobuf .toBinary(), passes the Uint8Array
// to the wasm bridge (which forwards binary in / binary out — conventions
// §2.5), and decodes responses via .fromBinary(). No JSON intermediate.
//
// Returns the existing snake_case web shapes (RunnerData,
// GRPCRegistrationToken, RelayConnectionInfo, etc.) so call sites don't have
// to switch wire-camelCase off the proto generated types. This is the same
// pattern used by skillRegistry.ts during the dual-track migration window.

import {
  CreateRunnerTokenRequestSchema,
  DeleteRunnerRequestSchema,
  DeleteRunnerResponseSchema,
  DeleteRunnerTokenRequestSchema,
  DeleteRunnerTokenResponseSchema,
  GetRunnerRequestSchema,
  GetRunnerResponseSchema,
  ListAvailableRunnersRequestSchema,
  ListAvailableRunnersResponseSchema,
  ListRunnerLogsRequestSchema,
  ListRunnerLogsResponseSchema,
  ListRunnerTokensRequestSchema,
  ListRunnerTokensResponseSchema,
  ListRunnersRequestSchema,
  ListRunnersResponseSchema,
  QuerySandboxesRequestSchema,
  QuerySandboxesResponseSchema,
  RequestLogUploadRequestSchema,
  RequestLogUploadResponseSchema,
  RunnerSchema,
  RunnerTokenSchema,
  UpdateRunnerRequestSchema,
  UpgradeRunnerRequestSchema,
  UpgradeRunnerResponseSchema,
  type RelayConnectionInfo as ProtoRelayConn,
  type Runner as ProtoRunner,
  type RunnerLog as ProtoRunnerLog,
  type RunnerToken as ProtoRunnerToken,
  type SandboxStatus as ProtoSandboxStatus,
} from "@proto/runner_api/v1/runner_pb";
import { create, toBinary, fromBinary } from "@bufbuild/protobuf";
import { getRunnerService } from "@/lib/wasm-core";
import type {
  GRPCRegistrationToken,
  RelayConnectionInfo,
  RunnerData,
  RunnerLogData,
  SandboxStatus,
} from "@/lib/viewModels/runner";

type RunnerStatus = "online" | "offline" | "maintenance" | "busy";

interface HostInfo {
  os?: string;
  arch?: string;
  memory?: number;
  cpu_cores?: number;
  hostname?: string;
}

function parseHostInfo(json: string): HostInfo | undefined {
  if (!json) return undefined;
  try {
    return JSON.parse(json) as HostInfo;
  } catch {
    return undefined;
  }
}

function fromProtoRunner(r: ProtoRunner): RunnerData {
  // Status comes from the server as a string; cast back to the union the UI uses.
  // Unknown values (server-side schema drift) still satisfy the type at runtime.
  return {
    id: Number(r.id),
    node_id: r.nodeId,
    description: r.description || undefined,
    status: r.status as RunnerStatus,
    last_heartbeat: r.lastHeartbeat,
    current_pods: r.currentPods,
    max_concurrent_pods: r.maxConcurrentPods,
    runner_version: r.runnerVersion,
    is_enabled: r.isEnabled,
    visibility: r.visibility as RunnerData["visibility"],
    registered_by_user_id:
      r.registeredByUserId === undefined ? undefined : Number(r.registeredByUserId),
    host_info: parseHostInfo(r.hostInfoJson),
    available_agents: r.availableAgents?.length ? r.availableAgents : undefined,
    tags: r.tags?.length ? r.tags : undefined,
    created_at: r.createdAt,
    updated_at: r.updatedAt,
  };
}

function fromProtoRelayConn(c: ProtoRelayConn): RelayConnectionInfo {
  return {
    pod_key: c.podKey,
    relay_url: c.relayUrl,
    connected: c.connected,
    // Wire format: int64 milliseconds. Web UI takes ISO; convert here.
    connected_at: c.connectedAt > 0
      ? new Date(Number(c.connectedAt)).toISOString()
      : "",
  };
}

function fromProtoToken(t: ProtoRunnerToken): GRPCRegistrationToken {
  return {
    id: Number(t.id),
    name: t.name,
    max_uses: t.maxUses,
    used_count: t.usedCount,
    expires_at: t.expiresAt,
    created_at: t.createdAt,
  };
}

function fromProtoLog(l: ProtoRunnerLog): RunnerLogData {
  return {
    id: Number(l.id),
    request_id: l.requestId,
    status: l.status,
    storage_key: l.storageKey,
    size_bytes: Number(l.sizeBytes),
    error_message: l.errorMessage,
    requested_by_id: Number(l.requestedById),
    download_url: l.downloadUrl,
    created_at: l.createdAt,
    completed_at: l.completedAt,
  };
}

function fromProtoSandbox(s: ProtoSandboxStatus): SandboxStatus {
  return {
    pod_key: s.podKey,
    exists: s.exists,
    can_resume: s.canResume,
    sandbox_path: s.sandboxPath,
    repository_url: s.repositoryUrl,
    branch_name: s.branchName,
    current_commit: s.currentCommit,
    size_bytes: s.sizeBytes === undefined ? undefined : Number(s.sizeBytes),
    last_modified: s.lastModified === undefined ? undefined : Number(s.lastModified),
    has_uncommitted_changes: s.hasUncommittedChanges,
    error: s.error,
  };
}

// ============== Runner CRUD ==============

export async function listRunners(
  orgSlug: string,
  opts: { status?: string; offset?: number; limit?: number } = {},
): Promise<{
  items: RunnerData[];
  total: number;
  limit: number;
  offset: number;
  latest_runner_version?: string;
}> {
  const req = create(ListRunnersRequestSchema, {
    orgSlug,
    status: opts.status,
    offset: opts.offset,
    limit: opts.limit,
  });
  const bytes = toBinary(ListRunnersRequestSchema, req);
  const respBytes = await getRunnerService().listRunnersConnect(bytes);
  const resp = fromBinary(ListRunnersResponseSchema, new Uint8Array(respBytes));
  return {
    items: resp.items.map(fromProtoRunner),
    total: Number(resp.total),
    limit: resp.limit,
    offset: resp.offset,
    latest_runner_version: resp.latestRunnerVersion,
  };
}

export async function listAvailableRunners(
  orgSlug: string,
): Promise<{ items: RunnerData[]; total: number }> {
  const req = create(ListAvailableRunnersRequestSchema, { orgSlug });
  const bytes = toBinary(ListAvailableRunnersRequestSchema, req);
  const respBytes = await getRunnerService().listAvailableRunnersConnect(bytes);
  const resp = fromBinary(ListAvailableRunnersResponseSchema, new Uint8Array(respBytes));
  return { items: resp.items.map(fromProtoRunner), total: Number(resp.total) };
}

export async function getRunner(
  orgSlug: string,
  id: number,
): Promise<{
  runner: RunnerData | null;
  relay_connections: RelayConnectionInfo[];
  latest_runner_version?: string;
}> {
  const req = create(GetRunnerRequestSchema, { orgSlug, id: BigInt(id) });
  const bytes = toBinary(GetRunnerRequestSchema, req);
  const respBytes = await getRunnerService().getRunnerConnect(bytes);
  const resp = fromBinary(GetRunnerResponseSchema, new Uint8Array(respBytes));
  return {
    runner: resp.runner ? fromProtoRunner(resp.runner) : null,
    relay_connections: resp.relayConnections.map(fromProtoRelayConn),
    latest_runner_version: resp.latestRunnerVersion,
  };
}

export interface UpdateRunnerInput {
  description?: string;
  max_concurrent_pods?: number;
  is_enabled?: boolean;
  visibility?: string;
  // tags: undefined = no change, [] = clear, [...] = set.
  tags?: string[];
}

export async function updateRunner(
  orgSlug: string,
  id: number,
  input: UpdateRunnerInput,
): Promise<RunnerData> {
  const req = create(UpdateRunnerRequestSchema, {
    orgSlug,
    id: BigInt(id),
    description: input.description,
    maxConcurrentPods: input.max_concurrent_pods,
    isEnabled: input.is_enabled,
    visibility: input.visibility,
    tags: input.tags === undefined ? undefined : { values: input.tags },
  });
  const bytes = toBinary(UpdateRunnerRequestSchema, req);
  const respBytes = await getRunnerService().updateRunnerConnect(bytes);
  return fromProtoRunner(fromBinary(RunnerSchema, new Uint8Array(respBytes)));
}

export async function deleteRunner(orgSlug: string, id: number): Promise<void> {
  const req = create(DeleteRunnerRequestSchema, { orgSlug, id: BigInt(id) });
  const bytes = toBinary(DeleteRunnerRequestSchema, req);
  const respBytes = await getRunnerService().deleteRunnerConnect(bytes);
  fromBinary(DeleteRunnerResponseSchema, new Uint8Array(respBytes));
}

// ============== Upgrade / Logs / Sandboxes ==============

export async function upgradeRunner(
  orgSlug: string,
  id: number,
  targetVersion = "",
): Promise<{ request_id: string; message: string }> {
  const req = create(UpgradeRunnerRequestSchema, {
    orgSlug,
    id: BigInt(id),
    targetVersion,
  });
  const bytes = toBinary(UpgradeRunnerRequestSchema, req);
  const respBytes = await getRunnerService().upgradeRunnerConnect(bytes);
  const resp = fromBinary(UpgradeRunnerResponseSchema, new Uint8Array(respBytes));
  return { request_id: resp.requestId, message: resp.message };
}

export async function requestLogUpload(
  orgSlug: string,
  id: number,
): Promise<{ request_id: string; message: string }> {
  const req = create(RequestLogUploadRequestSchema, { orgSlug, id: BigInt(id) });
  const bytes = toBinary(RequestLogUploadRequestSchema, req);
  const respBytes = await getRunnerService().requestLogUploadConnect(bytes);
  const resp = fromBinary(RequestLogUploadResponseSchema, new Uint8Array(respBytes));
  return { request_id: resp.requestId, message: resp.message };
}

export async function listRunnerLogs(
  orgSlug: string,
  id: number,
  opts: { offset?: number; limit?: number } = {},
): Promise<{ items: RunnerLogData[]; total: number; limit: number; offset: number }> {
  const req = create(ListRunnerLogsRequestSchema, {
    orgSlug,
    id: BigInt(id),
    offset: opts.offset,
    limit: opts.limit,
  });
  const bytes = toBinary(ListRunnerLogsRequestSchema, req);
  const respBytes = await getRunnerService().listRunnerLogsConnect(bytes);
  const resp = fromBinary(ListRunnerLogsResponseSchema, new Uint8Array(respBytes));
  return {
    items: resp.items.map(fromProtoLog),
    total: Number(resp.total),
    limit: resp.limit,
    offset: resp.offset,
  };
}

export async function querySandboxes(
  orgSlug: string,
  id: number,
  podKeys: string[],
): Promise<{ sandboxes: SandboxStatus[]; error: string }> {
  const req = create(QuerySandboxesRequestSchema, {
    orgSlug,
    id: BigInt(id),
    podKeys,
  });
  const bytes = toBinary(QuerySandboxesRequestSchema, req);
  const respBytes = await getRunnerService().querySandboxesConnect(bytes);
  const resp = fromBinary(QuerySandboxesResponseSchema, new Uint8Array(respBytes));
  return {
    sandboxes: resp.sandboxes.map(fromProtoSandbox),
    error: resp.error,
  };
}

// ============== Tokens ==============

export async function createRunnerToken(
  orgSlug: string,
  data: { name?: string; labels?: string[]; max_uses?: number; expires_in_days?: number } = {},
): Promise<GRPCRegistrationToken & { token?: string }> {
  const req = create(CreateRunnerTokenRequestSchema, {
    orgSlug,
    name: data.name,
    labels: data.labels ?? [],
    maxUses: data.max_uses,
    expiresInDays: data.expires_in_days === undefined ? undefined : BigInt(data.expires_in_days),
  });
  const bytes = toBinary(CreateRunnerTokenRequestSchema, req);
  const respBytes = await getRunnerService().createRunnerTokenConnect(bytes);
  const t = fromBinary(RunnerTokenSchema, new Uint8Array(respBytes));
  return {
    ...fromProtoToken(t),
    token: t.token,
  };
}

export async function listRunnerTokens(
  orgSlug: string,
): Promise<{ items: GRPCRegistrationToken[]; total: number }> {
  const req = create(ListRunnerTokensRequestSchema, { orgSlug });
  const bytes = toBinary(ListRunnerTokensRequestSchema, req);
  const respBytes = await getRunnerService().listRunnerTokensConnect(bytes);
  const resp = fromBinary(ListRunnerTokensResponseSchema, new Uint8Array(respBytes));
  return { items: resp.items.map(fromProtoToken), total: Number(resp.total) };
}

export async function deleteRunnerToken(orgSlug: string, id: number): Promise<void> {
  const req = create(DeleteRunnerTokenRequestSchema, { orgSlug, id: BigInt(id) });
  const bytes = toBinary(DeleteRunnerTokenRequestSchema, req);
  const respBytes = await getRunnerService().deleteRunnerTokenConnect(bytes);
  fromBinary(DeleteRunnerTokenResponseSchema, new Uint8Array(respBytes));
}
