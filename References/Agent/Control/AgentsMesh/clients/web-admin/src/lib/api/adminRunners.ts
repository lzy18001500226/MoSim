// Connect-RPC adapter for the 5 runner procedures on
// proto.admin.v1.AdminService. Migrated from REST `/api/v1/admin/runners/*`.
//
// Public surface preserved (Runner, RunnerListParams, PaginatedResponse<Runner>)
// so the consumer pages don't need touching. The proto carries host_info as
// a JSON string (host_info_json) for binary safety; the legacy REST shape
// re-hydrates it into an object so existing UI keeps rendering identically.
import {
  AdminRunner as ProtoAdminRunner,
  AdminRunnerSchema,
  DeleteRunnerRequestSchema,
  DeleteRunnerResponseSchema,
  DisableRunnerRequestSchema,
  EnableRunnerRequestSchema,
  GetRunnerRequestSchema,
  ListRunnersRequestSchema,
  ListRunnersResponseSchema,
} from "@proto/admin/v1/admin_pb";

import { callConnect } from "@/lib/connect/transport";
import type { PaginatedResponse } from "./base";
import type { Runner, RunnerListParams } from "./adminTypes";

const SERVICE = "proto.admin.v1.AdminService";

void AdminRunnerSchema;
function runnerFromProto(r: ProtoAdminRunner): Runner {
  let hostInfo: Record<string, unknown> | null = null;
  if (r.hostInfoJson) {
    try {
      hostInfo = JSON.parse(r.hostInfoJson) as Record<string, unknown>;
    } catch {
      hostInfo = null;
    }
  }
  return {
    id: Number(r.id),
    organization_id: Number(r.organizationId),
    node_id: r.nodeId,
    description: r.description ?? null,
    status: r.status,
    is_enabled: r.isEnabled,
    runner_version: r.runnerVersion ?? null,
    current_pods: r.currentPods,
    max_concurrent_pods: r.maxConcurrentPods,
    available_agents: r.availableAgents,
    host_info: hostInfo,
    last_heartbeat: r.lastHeartbeat ?? null,
    created_at: r.createdAt,
    updated_at: r.updatedAt,
    organization: r.organization
      ? {
          id: Number(r.organization.id),
          name: r.organization.name,
          slug: r.organization.slug,
        }
      : undefined,
  };
}

export async function listRunners(
  params?: RunnerListParams,
): Promise<PaginatedResponse<Runner>> {
  const resp = await callConnect(
    SERVICE,
    "ListRunners",
    ListRunnersRequestSchema,
    ListRunnersResponseSchema,
    {
      search: params?.search,
      status: params?.status,
      orgId: params?.org_id !== undefined ? BigInt(params.org_id) : undefined,
      page: params?.page,
      pageSize: params?.page_size,
    },
  );
  return {
    data: resp.items.map(runnerFromProto),
    total: Number(resp.total),
    page: resp.page,
    page_size: resp.pageSize,
    total_pages: resp.totalPages,
  };
}

export async function getRunner(id: number): Promise<Runner> {
  const resp = await callConnect(
    SERVICE,
    "GetRunner",
    GetRunnerRequestSchema,
    AdminRunnerSchema,
    { runnerId: BigInt(id) },
  );
  return runnerFromProto(resp);
}

export async function disableRunner(id: number): Promise<Runner> {
  const resp = await callConnect(
    SERVICE,
    "DisableRunner",
    DisableRunnerRequestSchema,
    AdminRunnerSchema,
    { runnerId: BigInt(id) },
  );
  return runnerFromProto(resp);
}

export async function enableRunner(id: number): Promise<Runner> {
  const resp = await callConnect(
    SERVICE,
    "EnableRunner",
    EnableRunnerRequestSchema,
    AdminRunnerSchema,
    { runnerId: BigInt(id) },
  );
  return runnerFromProto(resp);
}

export async function deleteRunner(id: number): Promise<{ message: string }> {
  const resp = await callConnect(
    SERVICE,
    "DeleteRunner",
    DeleteRunnerRequestSchema,
    DeleteRunnerResponseSchema,
    { runnerId: BigInt(id) },
  );
  return { message: resp.message };
}
