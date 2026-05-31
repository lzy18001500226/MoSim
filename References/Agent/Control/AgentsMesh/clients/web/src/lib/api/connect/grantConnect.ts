// Connect-RPC adapter for proto.grant.v1.GrantService.
//
// Encodes requests via @bufbuild/protobuf .toBinary(), passes the Uint8Array
// to the wasm bridge (binary in / binary out — conventions §2.5), decodes
// responses via .fromBinary(). No JSON intermediate.
//
// Returns snake_case web shapes (ResourceGrant) so the existing call sites
// in ShareDialog don't have to flip off camelCase + BigInt — same
// dual-track pattern as supportTicketConnect.ts during the migration window.

import {
  CreateGrantRequestSchema,
  DeleteGrantRequestSchema,
  ListGrantsRequestSchema,
  ListGrantsResponseSchema,
  ResourceGrantSchema,
  type ResourceGrant as ProtoResourceGrant,
  type ResourceGrantUser as ProtoResourceGrantUser,
} from "@proto/grant/v1/grant_pb";
import { create, toBinary, fromBinary } from "@bufbuild/protobuf";
import { getGrantService } from "@/lib/wasm-core";
import type { ResourceGrant } from "../facade/grant";

// ============== Wire conversion (proto -> snake_case web shape) ==============

function fromProtoUser(
  p: ProtoResourceGrantUser | undefined,
): { id: number; email: string; username: string; name?: string } | undefined {
  if (!p) return undefined;
  const out: { id: number; email: string; username: string; name?: string } = {
    id: Number(p.id),
    email: p.email,
    username: p.username,
  };
  if (p.name !== undefined) out.name = p.name;
  return out;
}

export function fromProtoGrant(p: ProtoResourceGrant): ResourceGrant {
  return {
    id: Number(p.id),
    resource_type: p.resourceType,
    resource_id: p.resourceId,
    user_id: Number(p.userId),
    granted_by: Number(p.grantedBy),
    created_at: p.createdAt,
    user: fromProtoUser(p.user),
    granted_by_user: fromProtoUser(p.grantedByUser),
  };
}

// ============== RPCs ==============

export async function listGrants(
  orgSlug: string,
  resourceType: string,
  resourceId: string,
): Promise<{ grants: ResourceGrant[] }> {
  const req = create(ListGrantsRequestSchema, {
    orgSlug,
    resourceType,
    resourceId,
  });
  const bytes = toBinary(ListGrantsRequestSchema, req);
  const respBytes = await getGrantService().listGrantsConnect(bytes);
  const resp = fromBinary(ListGrantsResponseSchema, new Uint8Array(respBytes));
  return { grants: resp.items.map(fromProtoGrant) };
}

export async function createGrant(
  orgSlug: string,
  resourceType: string,
  resourceId: string,
  userId: number,
): Promise<{ grant: ResourceGrant }> {
  const req = create(CreateGrantRequestSchema, {
    orgSlug,
    resourceType,
    resourceId,
    userId: BigInt(userId),
  });
  const bytes = toBinary(CreateGrantRequestSchema, req);
  const respBytes = await getGrantService().createGrantConnect(bytes);
  const resp = fromBinary(ResourceGrantSchema, new Uint8Array(respBytes));
  return { grant: fromProtoGrant(resp) };
}

export async function deleteGrant(
  orgSlug: string,
  resourceType: string,
  resourceId: string,
  grantId: number,
): Promise<{ message: string }> {
  const req = create(DeleteGrantRequestSchema, {
    orgSlug,
    resourceType,
    resourceId,
    grantId: BigInt(grantId),
  });
  const bytes = toBinary(DeleteGrantRequestSchema, req);
  await getGrantService().deleteGrantConnect(bytes);
  return { message: "ok" };
}
