import { getBlockstoreService, parseWasmAny } from "@/lib/wasm-core";
import { readCurrentOrg } from "@/stores/auth";
import {
  applyOps as applyOpsConnect,
  listWorkspaces as listWorkspacesConnect,
  ensureDefaultWorkspace as ensureDefaultWorkspaceConnect,
  getSubtree as getSubtreeConnect,
  streamOps as streamOpsConnect,
  listTypeDefs as listTypeDefsConnect,
  semanticSearch as semanticSearchConnect,
} from "@/lib/api/connect/blockstoreConnect";
import type {
  ApplyOpsRequest,
  ApplyOpsResult,
  Block,
  BlockOp,
  BlockRef,
  ChildrenResult,
  SearchHit,
  Workspace,
} from "@/lib/viewModels/blockstore";

const svc = () => getBlockstoreService();

function orgSlug(): string {
  return readCurrentOrg()?.slug ?? "";
}

export const blockstoreApi = {
  async applyOps(req: ApplyOpsRequest): Promise<ApplyOpsResult> {
    const res = await applyOpsConnect(orgSlug(), req);
    // Project locally so the SSOT cache reflects the optimistic mutation
    // before the WS broadcast / catchup arrives.
    svcProjectOps(req, res);
    return res;
  },

  async listWorkspaces(): Promise<{ workspaces: Workspace[] }> {
    const { workspaces } = await listWorkspacesConnect(orgSlug());
    svc().replace_workspaces_json(JSON.stringify(workspaces));
    return { workspaces };
  },

  async ensureDefaultWorkspace(): Promise<Workspace> {
    const ws = await ensureDefaultWorkspaceConnect(orgSlug());
    svc().upsert_workspace_json(JSON.stringify(ws));
    return ws;
  },

  async getBlock(id: string): Promise<Block> {
    const raw = parseWasmAny<Block>(svc().get_block_json(id));
    if (!raw) throw new Error(`block not found: ${id}`);
    return raw;
  },

  async listChildren(id: string, _rel = "nest"): Promise<ChildrenResult> {
    const raw = svc().list_children_json(id);
    return (JSON.parse(raw) as ChildrenResult) ?? { blocks: [], refs: [] };
  },

  async listBacklinks(id: string): Promise<{ refs: BlockRef[] }> {
    const raw = svc().list_backlinks_json(id);
    return (JSON.parse(raw) as { refs: BlockRef[] }) ?? { refs: [] };
  },

  async getSubtree(wsID: string, rootID: string, maxDepth = 64): Promise<ChildrenResult> {
    const { blocks, refs } = await getSubtreeConnect(orgSlug(), wsID, rootID, maxDepth);
    svc().upsert_blocks_json(JSON.stringify(blocks));
    svc().upsert_refs_json(JSON.stringify(refs));
    if (svc().last_op_id(wsID) === BigInt(0)) {
      // Seed watermark so the WS filter recognises this workspace, mirroring
      // the legacy Rust load_subtree path. `set_last_op_id` is wasm-bindgen
      // i64 → JS BigInt — passing a Number throws "Cannot convert 0 to a
      // BigInt" and wedges DocumentView in the Loading state.
      svc().set_last_op_id(wsID, BigInt(0));
    }
    const result: ChildrenResult = (() => {
      try {
        return JSON.parse(svc().list_children_json(rootID)) as ChildrenResult;
      } catch {
        return { blocks: [], refs: [] };
      }
    })();
    // The root block itself isn't in list_children — splice it in for callers.
    try {
      const rootJson = svc().get_block_json(rootID);
      const root = parseWasmAny<Block>(rootJson);
      if (root && !result.blocks.some((b) => b.id === root.id)) {
        result.blocks = [root, ...result.blocks];
      }
    } catch {
      // Root not present yet — tolerate.
    }
    return result;
  },

  async catchupOps(wsID: string, _after = 0, limit = 500): Promise<{ ops: BlockOp[] }> {
    const after = svc().last_op_id(wsID);
    const { ops } = await streamOpsConnect(orgSlug(), wsID, after, limit);
    // Apply each authoritative op into the SSOT cache so subsequent reads
    // reflect the converged state. apply_remote_op also bumps last_op_id.
    for (const op of ops) {
      svc().apply_remote_op(JSON.stringify(op));
    }
    // Callers historically iterated the returned ops to feed applyRemoteOp;
    // with this adapter the cache is already converged, so return empty.
    return { ops: [] };
  },

  async listTypeDefs(wsID: string): Promise<{ blocks: Block[] }> {
    const { blocks } = await listTypeDefsConnect(orgSlug(), wsID);
    svc().upsert_blocks_json(JSON.stringify(blocks));
    return { blocks };
  },

  async semanticSearch(
    wsID: string,
    query: string,
    opts: { topK?: number; minScore?: number; type?: string } = {},
  ): Promise<{ hits: SearchHit[] }> {
    return await semanticSearchConnect(orgSlug(), wsID, query, opts);
  },
};

function svcProjectOps(req: ApplyOpsRequest, res: ApplyOpsResult): void {
  // Some test mocks omit project_local_ops; tolerate by guarding.
  const s = svc() as unknown as { project_local_ops?: (a: string, b: string) => unknown };
  if (typeof s.project_local_ops === "function") {
    s.project_local_ops(JSON.stringify(req), JSON.stringify(res));
  }
}
