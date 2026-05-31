// Connect-RPC adapter for proto.blockstore.v1.BlockstoreService.
//
// Encodes requests via @bufbuild/protobuf .toBinary(), passes the Uint8Array
// to the wasm bridge (binary in / binary out — conventions §2.5), and
// decodes responses via .fromBinary(). No JSON intermediate.
//
// Returns the existing web Block / BlockRef / BlockOp / Workspace shapes
// (snake_case + opaque JSON-as-object data/meta) so existing call sites in
// blockstoreApi.ts don't have to change shape. The proto types carry data
// / meta as JSON strings; the adapter parses them back into JSONMap.
//
// Until every call site is on Connect, the legacy blockstoreApi.ts (REST
// path via wasm JSON bridge) keeps working unchanged.

import {
  ApplyOpsRequestSchema,
  ApplyOpsResponseSchema,
  ListWorkspacesRequestSchema,
  ListWorkspacesResponseSchema,
  EnsureDefaultWorkspaceRequestSchema,
  CreateWorkspaceRequestSchema,
  DeleteWorkspaceRequestSchema,
  DeleteWorkspaceResponseSchema,
  GetBlockRequestSchema,
  ListChildrenRequestSchema,
  ChildrenResultSchema,
  ListBacklinksRequestSchema,
  ListBacklinksResponseSchema,
  GetSubtreeRequestSchema,
  StreamOpsRequestSchema,
  StreamOpsResponseSchema,
  ExportWorkspaceRequestSchema,
  ExportWorkspaceResponseSchema,
  ListTypeDefsRequestSchema,
  ListTypeDefsResponseSchema,
  GetBlockAtRequestSchema,
  BlockSchema,
  WorkspaceSchema,
  SemanticSearchRequestSchema,
  SemanticSearchResponseSchema,
  MemoryRetrieveRequestSchema,
  MemoryRetrieveResponseSchema,
  type Block as ProtoBlock,
  type BlockRef as ProtoBlockRef,
  type BlockOp as ProtoBlockOp,
  type Workspace as ProtoWorkspace,
  type SearchHit as ProtoSearchHit,
  type OpEnvelope as ProtoOpEnvelope,
} from "@proto/blockstore/v1/blockstore_pb";
import { create, toBinary, fromBinary } from "@bufbuild/protobuf";
import { getBlockstoreService } from "@/lib/wasm-core";
import type {
  ApplyOpsRequest,
  ApplyOpsResult,
  Block,
  BlockOp,
  BlockRef,
  ChildrenResult,
  JSONMap,
  OpEnvelope,
  SearchHit,
  Workspace,
} from "@/lib/viewModels/blockstore";

// ---------------- JSON helpers ----------------
//
// The proto wire ships JSONB payloads as opaque strings (see proto file
// header). Adapter re-hydrates them into JSONMap so call-sites keep the
// legacy `block.data["title"]` ergonomics.

function parseJsonMap(s: string): JSONMap {
  if (!s) return {};
  try {
    return JSON.parse(s) as JSONMap;
  } catch {
    return {};
  }
}

function stringifyJsonMap(m: JSONMap | undefined): string {
  if (!m) return "";
  return JSON.stringify(m);
}

// ---------------- Field mappers ----------------

export function blockFromProto(b: ProtoBlock): Block {
  return {
    id: b.id,
    workspace_id: b.workspaceId,
    type: b.type,
    data: parseJsonMap(b.dataJson),
    text: b.text,
    meta: parseJsonMap(b.metaJson),
    created_by: Number(b.createdBy),
    created_at: b.createdAt,
    updated_at: b.updatedAt,
    deleted_at: b.deletedAt,
  };
}

export function refFromProto(r: ProtoBlockRef): BlockRef {
  return {
    id: Number(r.id),
    workspace_id: r.workspaceId,
    from_id: r.fromId,
    to_id: r.toId,
    rel: r.rel,
    order_key: r.orderKey,
    anchor: r.anchor,
    meta: parseJsonMap(r.metaJson),
    created_by: Number(r.createdBy),
    created_at: r.createdAt,
    updated_at: r.updatedAt,
  };
}

export function opFromProto(o: ProtoBlockOp): BlockOp {
  return {
    id: Number(o.id),
    workspace_id: o.workspaceId,
    idempotency_key: o.idempotencyKey,
    actor_type: o.actorType as BlockOp["actor_type"],
    actor_id: Number(o.actorId),
    op: o.op as BlockOp["op"],
    target_block: o.targetBlock,
    target_ref: o.targetRef !== undefined ? Number(o.targetRef) : undefined,
    payload: parseJsonMap(o.payloadJson),
    forward: parseJsonMap(o.forwardJson),
    inverse: parseJsonMap(o.inverseJson),
    parent_op_id: o.parentOpId !== undefined ? Number(o.parentOpId) : undefined,
    applied_at: o.appliedAt,
  };
}

export function workspaceFromProto(w: ProtoWorkspace): Workspace {
  return {
    id: w.id,
    organization_id: Number(w.organizationId),
    slug: w.slug,
    name: w.name,
    root_block_id: w.rootBlockId,
    created_at: w.createdAt,
  };
}

export function hitFromProto(h: ProtoSearchHit): SearchHit {
  return {
    block_id: h.blockId,
    type: h.type,
    snippet: h.snippet,
    score: h.score,
  };
}

function envelopeToProto(e: OpEnvelope): ProtoOpEnvelope {
  return {
    $typeName: "proto.blockstore.v1.OpEnvelope",
    op: e.op,
    payloadJson: stringifyJsonMap(e.payload),
  } as ProtoOpEnvelope;
}

// ---------------- Ops ----------------

export async function applyOps(orgSlug: string, req: ApplyOpsRequest): Promise<ApplyOpsResult> {
  const protoReq = create(ApplyOpsRequestSchema, {
    orgSlug,
    workspaceId: req.workspace_id,
    ops: req.ops.map(envelopeToProto),
    idempotencyKey: req.idempotency_key,
    parentOpId: req.parent_op_id !== undefined && req.parent_op_id !== null
      ? BigInt(req.parent_op_id) : undefined,
  });
  const bytes = toBinary(ApplyOpsRequestSchema, protoReq);
  const respBytes = await getBlockstoreService().applyOpsConnect(bytes);
  const resp = fromBinary(ApplyOpsResponseSchema, new Uint8Array(respBytes));
  return {
    op_ids: resp.opIds.map((n) => Number(n)),
    was_replay: resp.wasReplay,
    parent_op_id: resp.parentOpId !== undefined ? Number(resp.parentOpId) : undefined,
  };
}

// ---------------- Workspaces ----------------

export async function listWorkspaces(orgSlug: string): Promise<{ workspaces: Workspace[] }> {
  const req = create(ListWorkspacesRequestSchema, { orgSlug });
  const bytes = toBinary(ListWorkspacesRequestSchema, req);
  const respBytes = await getBlockstoreService().listWorkspacesConnect(bytes);
  const resp = fromBinary(ListWorkspacesResponseSchema, new Uint8Array(respBytes));
  return { workspaces: resp.items.map(workspaceFromProto) };
}

export async function ensureDefaultWorkspace(orgSlug: string): Promise<Workspace> {
  const req = create(EnsureDefaultWorkspaceRequestSchema, { orgSlug });
  const bytes = toBinary(EnsureDefaultWorkspaceRequestSchema, req);
  const respBytes = await getBlockstoreService().ensureDefaultWorkspaceConnect(bytes);
  return workspaceFromProto(fromBinary(WorkspaceSchema, new Uint8Array(respBytes)));
}

export async function createWorkspace(
  orgSlug: string, slug: string, name?: string,
): Promise<Workspace> {
  const req = create(CreateWorkspaceRequestSchema, { orgSlug, slug, name });
  const bytes = toBinary(CreateWorkspaceRequestSchema, req);
  const respBytes = await getBlockstoreService().createWorkspaceConnect(bytes);
  return workspaceFromProto(fromBinary(WorkspaceSchema, new Uint8Array(respBytes)));
}

export async function deleteWorkspace(orgSlug: string, workspaceId: string): Promise<void> {
  const req = create(DeleteWorkspaceRequestSchema, { orgSlug, workspaceId });
  const bytes = toBinary(DeleteWorkspaceRequestSchema, req);
  const respBytes = await getBlockstoreService().deleteWorkspaceConnect(bytes);
  fromBinary(DeleteWorkspaceResponseSchema, new Uint8Array(respBytes));
}

// ---------------- Block reads ----------------

export async function getBlock(orgSlug: string, id: string): Promise<Block> {
  const req = create(GetBlockRequestSchema, { orgSlug, id });
  const bytes = toBinary(GetBlockRequestSchema, req);
  const respBytes = await getBlockstoreService().getBlockConnect(bytes);
  return blockFromProto(fromBinary(BlockSchema, new Uint8Array(respBytes)));
}

export async function listChildren(
  orgSlug: string, id: string, rel = "nest",
): Promise<ChildrenResult> {
  const req = create(ListChildrenRequestSchema, { orgSlug, id, rel });
  const bytes = toBinary(ListChildrenRequestSchema, req);
  const respBytes = await getBlockstoreService().listChildrenConnect(bytes);
  const resp = fromBinary(ChildrenResultSchema, new Uint8Array(respBytes));
  return {
    blocks: resp.blocks.map(blockFromProto),
    refs: resp.refs.map(refFromProto),
  };
}

export async function listBacklinks(orgSlug: string, id: string): Promise<{ refs: BlockRef[] }> {
  const req = create(ListBacklinksRequestSchema, { orgSlug, id });
  const bytes = toBinary(ListBacklinksRequestSchema, req);
  const respBytes = await getBlockstoreService().listBacklinksConnect(bytes);
  const resp = fromBinary(ListBacklinksResponseSchema, new Uint8Array(respBytes));
  return { refs: resp.items.map(refFromProto) };
}

// ---------------- Workspace-scoped queries ----------------

export async function getSubtree(
  orgSlug: string, workspaceId: string, rootId: string, maxDepth = 64,
): Promise<ChildrenResult> {
  const req = create(GetSubtreeRequestSchema, { orgSlug, workspaceId, rootId, maxDepth });
  const bytes = toBinary(GetSubtreeRequestSchema, req);
  const respBytes = await getBlockstoreService().getSubtreeConnect(bytes);
  const resp = fromBinary(ChildrenResultSchema, new Uint8Array(respBytes));
  return {
    blocks: resp.blocks.map(blockFromProto),
    refs: resp.refs.map(refFromProto),
  };
}

export async function streamOps(
  orgSlug: string, workspaceId: string, after = 0, limit = 200,
): Promise<{ ops: BlockOp[] }> {
  const req = create(StreamOpsRequestSchema, {
    orgSlug, workspaceId,
    after: BigInt(after),
    limit,
  });
  const bytes = toBinary(StreamOpsRequestSchema, req);
  const respBytes = await getBlockstoreService().streamOpsConnect(bytes);
  const resp = fromBinary(StreamOpsResponseSchema, new Uint8Array(respBytes));
  return { ops: resp.items.map(opFromProto) };
}

export async function exportWorkspace(orgSlug: string, workspaceId: string): Promise<unknown> {
  const req = create(ExportWorkspaceRequestSchema, { orgSlug, workspaceId });
  const bytes = toBinary(ExportWorkspaceRequestSchema, req);
  const respBytes = await getBlockstoreService().exportWorkspaceConnect(bytes);
  const resp = fromBinary(ExportWorkspaceResponseSchema, new Uint8Array(respBytes));
  return JSON.parse(resp.exportJson);
}

export async function listTypeDefs(
  orgSlug: string, workspaceId: string,
): Promise<{ blocks: Block[] }> {
  const req = create(ListTypeDefsRequestSchema, { orgSlug, workspaceId });
  const bytes = toBinary(ListTypeDefsRequestSchema, req);
  const respBytes = await getBlockstoreService().listTypeDefsConnect(bytes);
  const resp = fromBinary(ListTypeDefsResponseSchema, new Uint8Array(respBytes));
  return { blocks: resp.items.map(blockFromProto) };
}

export async function getBlockAt(
  orgSlug: string, id: string, opId = 0,
): Promise<Block> {
  const req = create(GetBlockAtRequestSchema, { orgSlug, id, opId: BigInt(opId) });
  const bytes = toBinary(GetBlockAtRequestSchema, req);
  const respBytes = await getBlockstoreService().getBlockAtConnect(bytes);
  return blockFromProto(fromBinary(BlockSchema, new Uint8Array(respBytes)));
}

// ---------------- Semantic search ----------------

export async function semanticSearch(
  orgSlug: string,
  workspaceId: string,
  query: string,
  opts: { topK?: number; minScore?: number; type?: string } = {},
): Promise<{ hits: SearchHit[] }> {
  const req = create(SemanticSearchRequestSchema, {
    orgSlug, workspaceId, query,
    topK: opts.topK,
    minScore: opts.minScore,
    type: opts.type,
  });
  const bytes = toBinary(SemanticSearchRequestSchema, req);
  const respBytes = await getBlockstoreService().semanticSearchConnect(bytes);
  const resp = fromBinary(SemanticSearchResponseSchema, new Uint8Array(respBytes));
  return { hits: resp.hits.map(hitFromProto) };
}

export async function memoryRetrieve(
  orgSlug: string,
  workspaceId: string,
  query: string,
  k = 5,
): Promise<{ memories: SearchHit[] }> {
  const req = create(MemoryRetrieveRequestSchema, { orgSlug, workspaceId, query, k });
  const bytes = toBinary(MemoryRetrieveRequestSchema, req);
  const respBytes = await getBlockstoreService().memoryRetrieveConnect(bytes);
  const resp = fromBinary(MemoryRetrieveResponseSchema, new Uint8Array(respBytes));
  return { memories: resp.memories.map(hitFromProto) };
}
