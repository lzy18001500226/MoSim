// Connect-RPC adapter for proto.extension.v1.SkillRegistryService.
//
// Encodes requests via @bufbuild/protobuf .toBinary(), passes the Uint8Array
// to the wasm bridge (which forwards binary in / binary out — conventions
// §2.5), and decodes responses via .fromBinary(). No JSON intermediate.
//
// Returns the existing web SkillRegistry / SkillRegistryOverride shape (the
// snake_case TS interface in lib/api/extensionTypes.ts) so call sites don't
// have to convert. The proto generated types are camelCase + BigInt-typed
// — diverging the public API is a 30-file refactor, out of scope for the
// dual-track migration window.

import {
  CreateSkillRegistryRequestSchema,
  DeleteSkillRegistryRequestSchema,
  DeleteSkillRegistryResponseSchema,
  ListSkillRegistriesRequestSchema,
  ListSkillRegistriesResponseSchema,
  ListSkillRegistryOverridesRequestSchema,
  ListSkillRegistryOverridesResponseSchema,
  SkillRegistrySchema,
  SyncSkillRegistryRequestSchema,
  TogglePlatformRegistryRequestSchema,
  TogglePlatformRegistryResponseSchema,
  type SkillRegistry as ProtoSkillRegistry,
  type SkillRegistryOverride as ProtoSkillRegistryOverride,
} from "@proto/extension/v1/skill_registry_pb";
import { create, toBinary, fromBinary } from "@bufbuild/protobuf";
import { getExtensionService } from "@/lib/wasm-core";
import type {
  SkillRegistry,
  SkillRegistryOverride,
  SkillRegistryAuthType,
} from "@/lib/viewModels/extension";

function fromProto(r: ProtoSkillRegistry): SkillRegistry {
  return {
    id: Number(r.id),
    organization_id:
      r.organizationId === undefined ? null : Number(r.organizationId),
    repository_url: r.repositoryUrl,
    branch: r.branch,
    source_type: r.sourceType,
    detected_type: r.detectedType ?? "",
    compatible_agents: r.compatibleAgents ?? [],
    auth_type: r.authType as SkillRegistryAuthType,
    last_synced_at: r.lastSyncedAt ?? null,
    sync_status: r.syncStatus,
    sync_error: r.syncError ?? "",
    skill_count: r.skillCount,
    is_active: r.isActive,
  };
}

function fromProtoOverride(o: ProtoSkillRegistryOverride): SkillRegistryOverride {
  return {
    id: Number(o.id),
    organization_id: Number(o.organizationId),
    registry_id: Number(o.registryId),
    is_disabled: o.isDisabled,
    created_at: o.createdAt,
    updated_at: o.updatedAt,
  };
}

export async function listSkillRegistries(
  orgSlug: string,
  opts: { offset?: number; limit?: number } = {},
): Promise<{ items: SkillRegistry[]; total: number; limit: number; offset: number }> {
  const req = create(ListSkillRegistriesRequestSchema, {
    orgSlug,
    offset: opts.offset,
    limit: opts.limit,
  });
  const bytes = toBinary(ListSkillRegistriesRequestSchema, req);
  const respBytes = await getExtensionService().listSkillRegistriesConnect(bytes);
  const resp = fromBinary(ListSkillRegistriesResponseSchema, new Uint8Array(respBytes));
  return {
    items: resp.items.map(fromProto),
    total: Number(resp.total),
    limit: resp.limit,
    offset: resp.offset,
  };
}

export async function createSkillRegistry(
  orgSlug: string,
  data: {
    repositoryUrl: string;
    branch?: string;
    sourceType?: string;
    compatibleAgents?: string[];
    authType?: string;
    authCredential?: string;
  },
): Promise<SkillRegistry> {
  const req = create(CreateSkillRegistryRequestSchema, {
    orgSlug,
    repositoryUrl: data.repositoryUrl,
    branch: data.branch,
    sourceType: data.sourceType,
    compatibleAgents: data.compatibleAgents ?? [],
    authType: data.authType,
    authCredential: data.authCredential,
  });
  const bytes = toBinary(CreateSkillRegistryRequestSchema, req);
  const respBytes = await getExtensionService().createSkillRegistryConnect(bytes);
  return fromProto(fromBinary(SkillRegistrySchema, new Uint8Array(respBytes)));
}

export async function syncSkillRegistry(orgSlug: string, id: number): Promise<SkillRegistry> {
  const req = create(SyncSkillRegistryRequestSchema, { orgSlug, id: BigInt(id) });
  const bytes = toBinary(SyncSkillRegistryRequestSchema, req);
  const respBytes = await getExtensionService().syncSkillRegistryConnect(bytes);
  return fromProto(fromBinary(SkillRegistrySchema, new Uint8Array(respBytes)));
}

export async function deleteSkillRegistry(orgSlug: string, id: number): Promise<void> {
  const req = create(DeleteSkillRegistryRequestSchema, { orgSlug, id: BigInt(id) });
  const bytes = toBinary(DeleteSkillRegistryRequestSchema, req);
  const respBytes = await getExtensionService().deleteSkillRegistryConnect(bytes);
  fromBinary(DeleteSkillRegistryResponseSchema, new Uint8Array(respBytes));
}

export async function togglePlatformRegistry(
  orgSlug: string,
  id: number,
  disabled: boolean,
): Promise<{ overrides: SkillRegistryOverride[] }> {
  const req = create(TogglePlatformRegistryRequestSchema, {
    orgSlug,
    id: BigInt(id),
    disabled,
  });
  const bytes = toBinary(TogglePlatformRegistryRequestSchema, req);
  const respBytes = await getExtensionService().togglePlatformRegistryConnect(bytes);
  const resp = fromBinary(TogglePlatformRegistryResponseSchema, new Uint8Array(respBytes));
  return { overrides: resp.overrides.map(fromProtoOverride) };
}

export async function listSkillRegistryOverrides(
  orgSlug: string,
): Promise<{ items: SkillRegistryOverride[] }> {
  const req = create(ListSkillRegistryOverridesRequestSchema, { orgSlug });
  const bytes = toBinary(ListSkillRegistryOverridesRequestSchema, req);
  const respBytes = await getExtensionService().listSkillRegistryOverridesConnect(bytes);
  const resp = fromBinary(ListSkillRegistryOverridesResponseSchema, new Uint8Array(respBytes));
  return { items: resp.items.map(fromProtoOverride) };
}
