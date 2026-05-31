// Connect-RPC adapter for proto.extension.v1.SkillRegistryAdminService.
//
// Migrated from REST `/api/v1/admin/skill-registries/*`. Keeps the
// existing TS return shapes (snake_case + number) so the page + table
// don't need to change. Proto types are camelCase + bigint; the
// adapter bridges the gap inline (no separate convert file — the
// surface is small enough to keep the converter colocated under the
// 200-line cap).
import {
  AdminSkillRegistrySchema,
  CreateAdminSkillRegistryRequestSchema,
  DeleteAdminSkillRegistryRequestSchema,
  DeleteAdminSkillRegistryResponseSchema,
  ListAdminSkillRegistriesRequestSchema,
  ListAdminSkillRegistriesResponseSchema,
  SkillRegistryAdminService,
  SyncAdminSkillRegistryRequestSchema,
  SyncAdminSkillRegistryResponseSchema,
  type AdminSkillRegistry as ProtoAdminSkillRegistry,
} from "@proto/extension/v1/skill_registry_admin_pb";

import { callConnect } from "@/lib/connect/transport";
import type { CreateSkillRegistryRequest, SkillRegistry } from "./adminTypesExtended";

const SERVICE = "proto.extension.v1.SkillRegistryAdminService";
void SkillRegistryAdminService;

function fromProto(r: ProtoAdminSkillRegistry): SkillRegistry {
  return {
    id: Number(r.id),
    // Admin surface is platform-level only — REST always emitted null.
    organization_id: null,
    repository_url: r.repositoryUrl,
    branch: r.branch,
    source_type: r.sourceType,
    sync_status: r.syncStatus,
    sync_error: r.syncError ?? "",
    skill_count: r.skillCount,
    last_synced_at: r.lastSyncedAt ?? null,
    is_active: r.isActive,
    created_at: r.createdAt,
    updated_at: r.updatedAt,
  };
}

export async function listSkillRegistries(): Promise<{ items: SkillRegistry[]; total: number }> {
  const resp = await callConnect(
    SERVICE,
    "ListSkillRegistries",
    ListAdminSkillRegistriesRequestSchema,
    ListAdminSkillRegistriesResponseSchema,
    {},
  );
  return { items: resp.items.map(fromProto), total: Number(resp.total) };
}

export async function createSkillRegistry(data: CreateSkillRegistryRequest): Promise<SkillRegistry> {
  const resp = await callConnect(
    SERVICE,
    "CreateSkillRegistry",
    CreateAdminSkillRegistryRequestSchema,
    AdminSkillRegistrySchema,
    { repositoryUrl: data.repository_url, branch: data.branch },
  );
  return fromProto(resp);
}

export async function syncSkillRegistry(
  id: number,
): Promise<{ message: string; registry: SkillRegistry }> {
  const resp = await callConnect(
    SERVICE,
    "SyncSkillRegistry",
    SyncAdminSkillRegistryRequestSchema,
    SyncAdminSkillRegistryResponseSchema,
    { id: BigInt(id) },
  );
  // Backend always returns the reloaded registry — fall back to a stub
  // only on the unreachable path where Sync's post-sync re-read failed
  // AND somehow returned no message (defensive; never observed in REST).
  if (!resp.registry) {
    throw new Error("sync response missing registry");
  }
  return { message: resp.message, registry: fromProto(resp.registry) };
}

export async function deleteSkillRegistry(id: number): Promise<void> {
  await callConnect(
    SERVICE,
    "DeleteSkillRegistry",
    DeleteAdminSkillRegistryRequestSchema,
    DeleteAdminSkillRegistryResponseSchema,
    { id: BigInt(id) },
  );
}
