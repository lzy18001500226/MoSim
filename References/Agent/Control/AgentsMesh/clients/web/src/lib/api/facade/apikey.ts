// Connect-RPC adapter for proto.apikey.v1.ApiKeyService.
//
// Wire layer is proto-SSOT: returns and consumes `@proto/apikey/v1`
// types directly. No adapter DTO layer — hooks/components consume proto
// types (camelCase, bigint id) as-is.
//
// PR #345 lineage: `createApiKey` returns `{ apiKey, rawKey }` (multi-field
// per conventions §9 exception). The wire carries both tag 1 and tag 2;
// the secret cannot be silently dropped on the wasm hop.
import {
  ApiKeySchema,
  CreateApiKeyRequestSchema,
  CreateApiKeyResponseSchema,
  DeleteApiKeyRequestSchema,
  DeleteApiKeyResponseSchema,
  GetApiKeyRequestSchema,
  ListApiKeysRequestSchema,
  ListApiKeysResponseSchema,
  RevokeApiKeyRequestSchema,
  RevokeApiKeyResponseSchema,
  UpdateApiKeyRequestSchema,
  type ApiKey,
} from "@proto/apikey/v1/api_key_pb";
import { create, toBinary, fromBinary } from "@bufbuild/protobuf";
import { getApiKeyService } from "@/lib/wasm-core";

export type { ApiKey } from "@proto/apikey/v1/api_key_pb";

export async function listApiKeys(
  orgSlug: string,
  opts: { offset?: number; limit?: number } = {},
): Promise<{ items: ApiKey[]; total: number; limit: number; offset: number }> {
  const req = create(ListApiKeysRequestSchema, {
    orgSlug,
    offset: opts.offset,
    limit: opts.limit,
  });
  const bytes = toBinary(ListApiKeysRequestSchema, req);
  const respBytes = await getApiKeyService().listApiKeysConnect(bytes);
  const resp = fromBinary(ListApiKeysResponseSchema, new Uint8Array(respBytes));
  return {
    items: resp.items,
    total: Number(resp.total),
    limit: resp.limit,
    offset: resp.offset,
  };
}

export async function getApiKey(orgSlug: string, id: bigint): Promise<ApiKey> {
  const req = create(GetApiKeyRequestSchema, { orgSlug, id });
  const bytes = toBinary(GetApiKeyRequestSchema, req);
  const respBytes = await getApiKeyService().getApiKeyConnect(bytes);
  return fromBinary(ApiKeySchema, new Uint8Array(respBytes));
}

export interface CreateApiKeyResult {
  apiKey: ApiKey;
  rawKey: string;
}

export async function createApiKey(
  orgSlug: string,
  input: {
    name?: string;
    description?: string;
    scopes?: string[];
    expiresIn?: bigint;
  },
): Promise<CreateApiKeyResult> {
  const req = create(CreateApiKeyRequestSchema, {
    orgSlug,
    name: input.name,
    description: input.description,
    scopes: input.scopes ?? [],
    expiresIn: input.expiresIn,
  });
  const bytes = toBinary(CreateApiKeyRequestSchema, req);
  const respBytes = await getApiKeyService().createApiKeyConnect(bytes);
  const resp = fromBinary(CreateApiKeyResponseSchema, new Uint8Array(respBytes));
  if (!resp.apiKey) {
    throw new Error("createApiKey response missing api_key (proto tag 1)");
  }
  return { apiKey: resp.apiKey, rawKey: resp.rawKey };
}

export async function updateApiKey(
  orgSlug: string,
  id: bigint,
  input: {
    name?: string;
    description?: string;
    scopes?: string[];
    isEnabled?: boolean;
  },
): Promise<ApiKey> {
  const req = create(UpdateApiKeyRequestSchema, {
    orgSlug,
    id,
    name: input.name,
    description: input.description,
    scopes: input.scopes ?? [],
    isEnabled: input.isEnabled,
  });
  const bytes = toBinary(UpdateApiKeyRequestSchema, req);
  const respBytes = await getApiKeyService().updateApiKeyConnect(bytes);
  return fromBinary(ApiKeySchema, new Uint8Array(respBytes));
}

export async function revokeApiKey(orgSlug: string, id: bigint): Promise<void> {
  const req = create(RevokeApiKeyRequestSchema, { orgSlug, id });
  const bytes = toBinary(RevokeApiKeyRequestSchema, req);
  const respBytes = await getApiKeyService().revokeApiKeyConnect(bytes);
  fromBinary(RevokeApiKeyResponseSchema, new Uint8Array(respBytes));
}

export async function deleteApiKey(orgSlug: string, id: bigint): Promise<void> {
  const req = create(DeleteApiKeyRequestSchema, { orgSlug, id });
  const bytes = toBinary(DeleteApiKeyRequestSchema, req);
  const respBytes = await getApiKeyService().deleteApiKeyConnect(bytes);
  fromBinary(DeleteApiKeyResponseSchema, new Uint8Array(respBytes));
}
