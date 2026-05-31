// Connect-RPC adapter for proto.mesh.v1.MeshService.
//
// Encodes requests via @bufbuild/protobuf .toBinary(), passes the
// Uint8Array to the wasm bridge (binary in / binary out — conventions
// §2.5), decodes responses via .fromBinary().
//
// Field-shape note: the wire types use proto camelCase (e.g. `podKey`,
// `runnerId`) while the renderer's `MeshNode` interface (stores/mesh.ts)
// uses snake_case (`pod_key`, `runner_id`). The adapter remaps the
// projection inside `toRendererNode` so call sites keep reading the same
// shape they get from the legacy fetch_topology() path — diverging the
// renderer surface across all 26 services in one PR is out of scope.

import {
  BatchGetTicketPodsRequestSchema,
  BatchGetTicketPodsResponseSchema,
  CreatePodForTicketRequestSchema,
  GetMeshTopologyRequestSchema,
  GetTicketPodsRequestSchema,
  GetTicketPodsResponseSchema,
  MeshNodeSchema,
  MeshTopologySchema,
  type MeshNode as ProtoMeshNode,
  type MeshTopology as ProtoMeshTopology,
} from "@proto/mesh/v1/mesh_pb";
import { create, fromBinary, toBinary } from "@bufbuild/protobuf";
import { getMeshService } from "@/lib/wasm-core";
import type { MeshNode, MeshTopology } from "@/stores/mesh";

function toRendererNode(p: ProtoMeshNode): MeshNode {
  return {
    pod_key: p.podKey,
    status: p.status,
    agent_status: p.agentStatus,
    agent_slug: p.agentSlug,
    model: p.model,
    title: p.title,
    alias: p.alias,
    ticket_id: p.ticketId !== undefined ? Number(p.ticketId) : undefined,
    ticket_slug: p.ticketSlug,
    ticket_title: p.ticketTitle,
    repository_id: p.repositoryId !== undefined ? Number(p.repositoryId) : undefined,
    created_by_id: p.createdById !== undefined ? Number(p.createdById) : undefined,
    runner_id: p.runnerId !== undefined ? Number(p.runnerId) : undefined,
    runner_node_id: p.runnerNodeId || undefined,
    runner_status: p.runnerStatus || undefined,
    started_at: p.startedAt,
  };
}

function toRendererTopology(p: ProtoMeshTopology): MeshTopology {
  return {
    nodes: p.nodes.map(toRendererNode),
    edges: p.edges.map((e) => ({
      id: Number(e.id),
      source: e.source,
      target: e.target,
      granted_scopes: e.grantedScopes,
      pending_scopes: e.pendingScopes,
      status: e.status,
    })),
    channels: p.channels.map((c) => ({
      id: Number(c.id),
      name: c.name,
      description: c.description,
      pod_keys: c.podKeys,
      message_count: c.messageCount,
      is_archived: c.isArchived,
    })),
    runners: p.runners.map((r) => ({
      id: Number(r.id),
      name: r.nodeId,
      status: r.status,
      node_id: r.nodeId,
      max_concurrent_pods: r.maxConcurrentPods,
      current_pods: r.currentPods,
    })),
  };
}

export async function getMeshTopologyConnect(orgSlug: string): Promise<MeshTopology> {
  const req = create(GetMeshTopologyRequestSchema, { orgSlug });
  const bytes = toBinary(GetMeshTopologyRequestSchema, req);
  const respBytes = await getMeshService().getMeshTopologyConnect(bytes);
  const resp = fromBinary(MeshTopologySchema, new Uint8Array(respBytes));
  return toRendererTopology(resp);
}

export async function getTicketPodsConnect(
  orgSlug: string,
  ticketSlug: string,
  activeOnly?: boolean,
): Promise<MeshNode[]> {
  const req = create(GetTicketPodsRequestSchema, {
    orgSlug,
    ticketSlug,
    activeOnly,
  });
  const bytes = toBinary(GetTicketPodsRequestSchema, req);
  const respBytes = await getMeshService().getTicketPodsConnect(bytes);
  const resp = fromBinary(GetTicketPodsResponseSchema, new Uint8Array(respBytes));
  return resp.pods.map(toRendererNode);
}

export async function batchGetTicketPodsConnect(
  orgSlug: string,
  ticketIds: number[] | bigint[],
): Promise<Record<number, MeshNode[]>> {
  const req = create(BatchGetTicketPodsRequestSchema, {
    orgSlug,
    ticketIds: ticketIds.map((id) => BigInt(id)),
  });
  const bytes = toBinary(BatchGetTicketPodsRequestSchema, req);
  const respBytes = await getMeshService().batchGetTicketPodsConnect(bytes);
  const resp = fromBinary(BatchGetTicketPodsResponseSchema, new Uint8Array(respBytes));
  const out: Record<number, MeshNode[]> = {};
  for (const [k, v] of Object.entries(resp.ticketPods)) {
    out[Number(k)] = v.pods.map(toRendererNode);
  }
  return out;
}

export async function createPodForTicketConnect(
  orgSlug: string,
  ticketSlug: string,
  runnerId: bigint,
  prompt?: string,
  model?: string,
  permissionMode?: string,
): Promise<MeshNode> {
  const req = create(CreatePodForTicketRequestSchema, {
    orgSlug,
    ticketSlug,
    runnerId,
    prompt,
    model,
    permissionMode,
  });
  const bytes = toBinary(CreatePodForTicketRequestSchema, req);
  const respBytes = await getMeshService().createPodForTicketConnect(bytes);
  const resp = fromBinary(MeshNodeSchema, new Uint8Array(respBytes));
  return toRendererNode(resp);
}
