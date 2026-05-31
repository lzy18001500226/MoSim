// Connect-RPC adapter for proto.invitation.v1 (InvitationService +
// UserInvitationService + PublicInvitationService).
//
// Wire layer is proto-SSOT: returns and consumes `@proto/invitation/v1`
// types directly. No adapter DTO layer.

import {
  AcceptInvitationRequestSchema,
  AcceptInvitationResponseSchema,
  CreateInvitationRequestSchema,
  GetInvitationByTokenRequestSchema,
  InvitationInfoSchema,
  InvitationSchema,
  ListInvitationsRequestSchema,
  ListInvitationsResponseSchema,
  ListPendingInvitationsRequestSchema,
  ListPendingInvitationsResponseSchema,
  ResendInvitationRequestSchema,
  ResendInvitationResponseSchema,
  RevokeInvitationRequestSchema,
  RevokeInvitationResponseSchema,
  type AcceptedOrgInfo,
  type Invitation,
  type InvitationInfo,
  type PendingInvitation,
} from "@proto/invitation/v1/invitation_pb";
import { create, toBinary, fromBinary } from "@bufbuild/protobuf";
import { getInvitationService } from "@/lib/wasm-core";

export type {
  Invitation,
  InvitationInfo,
  PendingInvitation,
  AcceptedOrgInfo,
} from "@proto/invitation/v1/invitation_pb";

export async function listInvitations(
  orgSlug: string,
  opts: { offset?: number; limit?: number } = {},
): Promise<{ items: Invitation[]; total: number; limit: number; offset: number }> {
  const req = create(ListInvitationsRequestSchema, {
    orgSlug,
    offset: opts.offset,
    limit: opts.limit,
  });
  const bytes = toBinary(ListInvitationsRequestSchema, req);
  const respBytes = await getInvitationService().listInvitationsConnect(bytes);
  const resp = fromBinary(ListInvitationsResponseSchema, new Uint8Array(respBytes));
  return {
    items: resp.items,
    total: Number(resp.total),
    limit: resp.limit,
    offset: resp.offset,
  };
}

export async function createInvitation(
  orgSlug: string,
  email: string,
  role: string,
): Promise<Invitation> {
  const req = create(CreateInvitationRequestSchema, { orgSlug, email, role });
  const bytes = toBinary(CreateInvitationRequestSchema, req);
  const respBytes = await getInvitationService().createInvitationConnect(bytes);
  return fromBinary(InvitationSchema, new Uint8Array(respBytes));
}

export async function revokeInvitation(orgSlug: string, id: number): Promise<void> {
  const req = create(RevokeInvitationRequestSchema, { orgSlug, id: BigInt(id) });
  const bytes = toBinary(RevokeInvitationRequestSchema, req);
  const respBytes = await getInvitationService().revokeInvitationConnect(bytes);
  fromBinary(RevokeInvitationResponseSchema, new Uint8Array(respBytes));
}

export async function resendInvitation(orgSlug: string, id: number): Promise<void> {
  const req = create(ResendInvitationRequestSchema, { orgSlug, id: BigInt(id) });
  const bytes = toBinary(ResendInvitationRequestSchema, req);
  const respBytes = await getInvitationService().resendInvitationConnect(bytes);
  fromBinary(ResendInvitationResponseSchema, new Uint8Array(respBytes));
}

export async function acceptInvitation(
  token: string,
): Promise<{ message: string; organization?: AcceptedOrgInfo }> {
  const req = create(AcceptInvitationRequestSchema, { token });
  const bytes = toBinary(AcceptInvitationRequestSchema, req);
  const respBytes = await getInvitationService().acceptInvitationConnect(bytes);
  const resp = fromBinary(AcceptInvitationResponseSchema, new Uint8Array(respBytes));
  return {
    message: resp.message,
    organization: resp.organization,
  };
}

export async function listPendingInvitations(): Promise<{
  items: PendingInvitation[];
  total: number;
  limit: number;
  offset: number;
}> {
  const req = create(ListPendingInvitationsRequestSchema, {});
  const bytes = toBinary(ListPendingInvitationsRequestSchema, req);
  const respBytes = await getInvitationService().listPendingInvitationsConnect(bytes);
  const resp = fromBinary(ListPendingInvitationsResponseSchema, new Uint8Array(respBytes));
  return {
    items: resp.items,
    total: Number(resp.total),
    limit: resp.limit,
    offset: resp.offset,
  };
}

export async function getInvitationByToken(token: string): Promise<InvitationInfo> {
  const req = create(GetInvitationByTokenRequestSchema, { token });
  const bytes = toBinary(GetInvitationByTokenRequestSchema, req);
  const respBytes = await getInvitationService().getInvitationByTokenConnect(bytes);
  return fromBinary(InvitationInfoSchema, new Uint8Array(respBytes));
}
