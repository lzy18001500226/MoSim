// Connect-RPC adapter for proto.env_bundle.v1.EnvBundleService.
//
// Wire layer is proto-SSOT: returns and consumes `@proto/env_bundle/v1`
// types directly. No adapter DTO layer — hooks/components consume proto
// types (camelCase, bigint id) as-is.

import {
  CreateEnvBundleRequestSchema,
  DeleteEnvBundleRequestSchema,
  DeleteEnvBundleResponseSchema,
  EnvBundleSchema,
  GetEnvBundleRequestSchema,
  ListEnvBundlesRequestSchema,
  ListEnvBundlesResponseSchema,
  SetPrimaryEnvBundleRequestSchema,
  SetPrimaryEnvBundleResponseSchema,
  UpdateEnvBundleRequestSchema,
  type EnvBundle,
} from "@proto/env_bundle/v1/env_bundle_pb";
import { create, toBinary, fromBinary, type MessageInitShape } from "@bufbuild/protobuf";
import { getEnvBundleService } from "@/lib/wasm-core";

export type { EnvBundle } from "@proto/env_bundle/v1/env_bundle_pb";

export async function listEnvBundles(
  opts?: { kind?: string; agentSlug?: string },
): Promise<{ items: EnvBundle[]; total: number }> {
  const req = create(ListEnvBundlesRequestSchema, {
    kind: opts?.kind,
    agentSlug: opts?.agentSlug,
  });
  const bytes = toBinary(ListEnvBundlesRequestSchema, req);
  const respBytes = await getEnvBundleService().listEnvBundlesConnect(bytes);
  const resp = fromBinary(ListEnvBundlesResponseSchema, new Uint8Array(respBytes));
  return { items: resp.items, total: Number(resp.total) };
}

export async function getEnvBundle(id: bigint): Promise<EnvBundle> {
  const req = create(GetEnvBundleRequestSchema, { id });
  const bytes = toBinary(GetEnvBundleRequestSchema, req);
  const respBytes = await getEnvBundleService().getEnvBundleConnect(bytes);
  return fromBinary(EnvBundleSchema, new Uint8Array(respBytes));
}

export async function createEnvBundle(
  input: MessageInitShape<typeof CreateEnvBundleRequestSchema>,
): Promise<EnvBundle> {
  const req = create(CreateEnvBundleRequestSchema, input);
  const bytes = toBinary(CreateEnvBundleRequestSchema, req);
  const respBytes = await getEnvBundleService().createEnvBundleConnect(bytes);
  return fromBinary(EnvBundleSchema, new Uint8Array(respBytes));
}

export type UpdateEnvBundleInput = Omit<
  MessageInitShape<typeof UpdateEnvBundleRequestSchema>,
  "id" | "$typeName"
>;

export async function updateEnvBundle(
  id: bigint,
  input: UpdateEnvBundleInput,
): Promise<EnvBundle> {
  const req = create(UpdateEnvBundleRequestSchema, { ...input, id });
  const bytes = toBinary(UpdateEnvBundleRequestSchema, req);
  const respBytes = await getEnvBundleService().updateEnvBundleConnect(bytes);
  return fromBinary(EnvBundleSchema, new Uint8Array(respBytes));
}

export async function deleteEnvBundle(id: bigint): Promise<void> {
  const req = create(DeleteEnvBundleRequestSchema, { id });
  const bytes = toBinary(DeleteEnvBundleRequestSchema, req);
  const respBytes = await getEnvBundleService().deleteEnvBundleConnect(bytes);
  fromBinary(DeleteEnvBundleResponseSchema, new Uint8Array(respBytes));
}

export async function setPrimaryEnvBundle(id: bigint): Promise<void> {
  const req = create(SetPrimaryEnvBundleRequestSchema, { id });
  const bytes = toBinary(SetPrimaryEnvBundleRequestSchema, req);
  const respBytes = await getEnvBundleService().setPrimaryEnvBundleConnect(bytes);
  fromBinary(SetPrimaryEnvBundleResponseSchema, new Uint8Array(respBytes));
}
