// Connect-RPC adapter for proto.binding.v1.BindingService.
//
// Encodes requests via @bufbuild/protobuf .toBinary(), passes the Uint8Array
// to the wasm bridge (binary in / binary out — conventions §2.5), decodes
// responses via .fromBinary().
//
// The renderer-side `Binding` shape (lib/api/bindingTypes — not yet
// extracted; the legacy serde DTO at clients/core/crates/types/src/binding.rs
// has source_pod/target_pod rather than initiator_pod/target_pod, but no
// UI call site reads those fields today). This adapter exports the proto
// camelCase shape directly — callers receive a typed PodBinding with
// camelCase getters.

import {
  AcceptBindingRequestSchema,
  ApproveScopesRequestSchema,
  CheckBindingRequestSchema,
  CheckBindingResponseSchema,
  GetBoundPodsRequestSchema,
  GetBoundPodsResponseSchema,
  GetPendingBindingsRequestSchema,
  ListBindingsRequestSchema,
  ListBindingsResponseSchema,
  PodBindingSchema,
  RejectBindingRequestSchema,
  RequestBindingRequestSchema,
  RequestScopesRequestSchema,
  UnbindRequestSchema,
  UnbindResponseSchema,
  type PodBinding,
} from "@proto/binding/v1/binding_pb";
import { create, fromBinary, toBinary } from "@bufbuild/protobuf";
import { getBindingService } from "@/lib/wasm-core";

export type { PodBinding } from "@proto/binding/v1/binding_pb";

export async function requestBindingConnect(
  orgSlug: string,
  initiatorPod: string,
  targetPod: string,
  scopes: string[],
  policy?: string,
): Promise<PodBinding> {
  const req = create(RequestBindingRequestSchema, {
    orgSlug,
    initiatorPod,
    targetPod,
    scopes,
    policy,
  });
  const bytes = toBinary(RequestBindingRequestSchema, req);
  const respBytes = await getBindingService().requestBindingConnect(bytes);
  return fromBinary(PodBindingSchema, new Uint8Array(respBytes));
}

export async function acceptBindingConnect(
  orgSlug: string,
  initiatorPod: string,
  bindingId: bigint,
): Promise<PodBinding> {
  const req = create(AcceptBindingRequestSchema, { orgSlug, initiatorPod, bindingId });
  const bytes = toBinary(AcceptBindingRequestSchema, req);
  const respBytes = await getBindingService().acceptBindingConnect(bytes);
  return fromBinary(PodBindingSchema, new Uint8Array(respBytes));
}

export async function rejectBindingConnect(
  orgSlug: string,
  initiatorPod: string,
  bindingId: bigint,
  reason?: string,
): Promise<PodBinding> {
  const req = create(RejectBindingRequestSchema, {
    orgSlug,
    initiatorPod,
    bindingId,
    reason,
  });
  const bytes = toBinary(RejectBindingRequestSchema, req);
  const respBytes = await getBindingService().rejectBindingConnect(bytes);
  return fromBinary(PodBindingSchema, new Uint8Array(respBytes));
}

export async function unbindConnect(
  orgSlug: string,
  initiatorPod: string,
  targetPod: string,
): Promise<boolean> {
  const req = create(UnbindRequestSchema, { orgSlug, initiatorPod, targetPod });
  const bytes = toBinary(UnbindRequestSchema, req);
  const respBytes = await getBindingService().unbindConnect(bytes);
  const resp = fromBinary(UnbindResponseSchema, new Uint8Array(respBytes));
  return resp.removed;
}

export async function requestScopesConnect(
  orgSlug: string,
  initiatorPod: string,
  bindingId: bigint,
  scopes: string[],
): Promise<PodBinding> {
  const req = create(RequestScopesRequestSchema, {
    orgSlug,
    initiatorPod,
    bindingId,
    scopes,
  });
  const bytes = toBinary(RequestScopesRequestSchema, req);
  const respBytes = await getBindingService().requestScopesConnect(bytes);
  return fromBinary(PodBindingSchema, new Uint8Array(respBytes));
}

export async function approveScopesConnect(
  orgSlug: string,
  initiatorPod: string,
  bindingId: bigint,
  scopes: string[],
): Promise<PodBinding> {
  const req = create(ApproveScopesRequestSchema, {
    orgSlug,
    initiatorPod,
    bindingId,
    scopes,
  });
  const bytes = toBinary(ApproveScopesRequestSchema, req);
  const respBytes = await getBindingService().approveScopesConnect(bytes);
  return fromBinary(PodBindingSchema, new Uint8Array(respBytes));
}

export async function listBindingsConnect(
  orgSlug: string,
  initiatorPod: string,
  status?: string,
): Promise<PodBinding[]> {
  const req = create(ListBindingsRequestSchema, { orgSlug, initiatorPod, status });
  const bytes = toBinary(ListBindingsRequestSchema, req);
  const respBytes = await getBindingService().listBindingsConnect(bytes);
  const resp = fromBinary(ListBindingsResponseSchema, new Uint8Array(respBytes));
  return resp.items;
}

export async function getPendingBindingsConnect(
  orgSlug: string,
  initiatorPod: string,
): Promise<PodBinding[]> {
  const req = create(GetPendingBindingsRequestSchema, { orgSlug, initiatorPod });
  const bytes = toBinary(GetPendingBindingsRequestSchema, req);
  const respBytes = await getBindingService().getPendingBindingsConnect(bytes);
  const resp = fromBinary(ListBindingsResponseSchema, new Uint8Array(respBytes));
  return resp.items;
}

export async function getBoundPodsConnect(
  orgSlug: string,
  initiatorPod: string,
): Promise<string[]> {
  const req = create(GetBoundPodsRequestSchema, { orgSlug, initiatorPod });
  const bytes = toBinary(GetBoundPodsRequestSchema, req);
  const respBytes = await getBindingService().getBoundPodsConnect(bytes);
  const resp = fromBinary(GetBoundPodsResponseSchema, new Uint8Array(respBytes));
  return resp.pods;
}

export async function checkBindingConnect(
  orgSlug: string,
  initiatorPod: string,
  targetPod: string,
): Promise<{ isBound: boolean; binding?: PodBinding }> {
  const req = create(CheckBindingRequestSchema, { orgSlug, initiatorPod, targetPod });
  const bytes = toBinary(CheckBindingRequestSchema, req);
  const respBytes = await getBindingService().checkBindingConnect(bytes);
  const resp = fromBinary(CheckBindingResponseSchema, new Uint8Array(respBytes));
  return { isBound: resp.isBound, binding: resp.binding };
}
