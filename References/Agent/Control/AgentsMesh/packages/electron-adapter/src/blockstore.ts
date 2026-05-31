import { invoke } from "./invoke";
import { applyOpToCache, safeJsonMap, type CacheState } from "./blockstore-apply";
import {
  hydrateSubtree, upsertBlocks, upsertRefs, upsertWorkspace, replaceWorkspaces,
  type WorkspacesRef,
} from "./blockstore-cache";

/**
 * Desktop facade for the wasm-shaped BlockstoreService. The renderer cache is
 * the SSOT after the R6 Connect flip — main-process Rust state is kept warm
 * for legacy IPC consumers only. Synchronous mutators apply to `this.cache`
 * first so zustand selectors converge in the same React commit; IPC fires
 * fire-and-forget to mirror state in main.
 */
export class ElectronBlockstoreService {
  private blockCache = new Map<string, string>();
  private childrenCache = new Map<string, string>();
  private typeDefsCache = new Map<string, string>();
  private backlinksCache = new Map<string, string>();

  private cache: CacheState = {
    blocksJson: "{}", refsJson: "{}", nestChildrenJson: "{}",
    backlinksJsonFlat: "{}", lastOpIdsJson: "{}",
  };
  private workspaces: WorkspacesRef = { value: "{}" };

  private async refreshFlatCaches(): Promise<void> {
    const [blocks, refs, nestChildren, backlinks, lastOpIds, workspaces] = await Promise.all([
      invoke<string>("blockstoreBlocksJson"),
      invoke<string>("blockstoreRefsJson"),
      invoke<string>("blockstoreNestChildrenJson"),
      invoke<string>("blockstoreBacklinksJson"),
      invoke<string>("blockstoreLastOpIdsJson"),
      invoke<string>("blockstoreWorkspacesJson"),
    ]);
    this.cache.blocksJson = blocks || "{}";
    this.cache.refsJson = refs || "{}";
    this.cache.nestChildrenJson = nestChildren || "{}";
    this.cache.backlinksJsonFlat = backlinks || "{}";
    this.cache.lastOpIdsJson = lastOpIds || "{}";
    this.workspaces.value = workspaces || "{}";
  }

  async apply_ops(reqJson: string): Promise<string> {
    const result = await invoke<string>("blockstoreApplyOps", reqJson);
    await this.refreshFlatCaches();
    return result;
  }

  async list_workspaces(): Promise<string> {
    const result = await invoke<string>("blockstoreListWorkspaces");
    await this.refreshFlatCaches();
    return result;
  }

  async ensure_default_workspace(): Promise<string> {
    const result = await invoke<string>("blockstoreEnsureDefaultWorkspace");
    await this.refreshFlatCaches();
    return result;
  }

  async load_subtree(workspaceId: string, rootId: string): Promise<void> {
    await invoke("blockstoreLoadSubtree", workspaceId, rootId);
    await hydrateSubtree(rootId, this.blockCache, this.childrenCache);
    await this.refreshFlatCaches();
  }

  async load_type_defs(workspaceId: string): Promise<void> {
    await invoke("blockstoreLoadTypeDefs", workspaceId);
    const json = await invoke<string>("blockstoreTypeDefsJson", workspaceId);
    this.typeDefsCache.set(workspaceId, json);
  }

  async catchup(workspaceId: string): Promise<void> {
    await invoke("blockstoreCatchup", workspaceId);
  }

  async semantic_search(workspaceId: string, reqJson: string): Promise<string> {
    return invoke<string>("blockstoreSemanticSearch", workspaceId, reqJson);
  }

  apply_remote_op(opJson: string): void {
    let normalized = opJson;
    let parsed: Record<string, unknown> | null = null;
    try {
      parsed = JSON.parse(opJson) as Record<string, unknown>;
      // Backend WS pushes applied_at as Unix ms; Rust BlockOp expects ISO string.
      if (typeof parsed.applied_at === "number") {
        parsed.applied_at = new Date(parsed.applied_at).toISOString();
        normalized = JSON.stringify(parsed);
      }
    } catch { /* fall through with original payload */ }
    if (parsed) {
      try { applyOpToCache(this.cache, parsed as unknown as Parameters<typeof applyOpToCache>[1]); }
      catch { /* tolerate malformed ops */ }
    }
    // Fire IPC to keep main-process mirror warm for legacy consumers, but
    // DO NOT refresh from main afterwards — main is racing the catchup loop
    // and an in-flight refresh would overwrite the renderer cache with a
    // stale snapshot before later ops in the same loop apply.
    void invoke("blockstoreApplyRemoteOp", normalized);
  }

  // Mirrors services::blockstore::apply_local_ops — skips ref ops (server
  // assigns ref_id) and projects the rest using the server-returned op_ids.
  project_local_ops(reqJson: string, resJson: string): void {
    let req: { workspace_id?: string; ops?: Array<{ op: string; payload: Record<string, unknown> }> };
    let res: { op_ids?: number[]; was_replay?: boolean };
    try { req = JSON.parse(reqJson); res = JSON.parse(resJson); } catch { return; }
    if (res.was_replay) return;
    const wsId = req.workspace_id ?? "";
    const ops = req.ops ?? [];
    const opIds = res.op_ids ?? [];
    for (let i = 0; i < ops.length; i++) {
      const env = ops[i];
      const opId = opIds[i];
      if (opId === undefined) continue;
      if (env.op === "addRef" || env.op === "removeRef" || env.op === "updateRef") continue;
      applyOpToCache(this.cache, {
        id: opId, workspace_id: wsId, op: env.op,
        forward: env.payload, applied_at: "",
      });
    }
  }

  workspaces_json(): string { return this.workspaces.value; }
  blocks_json(): string { return this.cache.blocksJson; }
  refs_json(): string { return this.cache.refsJson; }
  nest_children_json(): string { return this.cache.nestChildrenJson; }
  backlinks_json(): string { return this.cache.backlinksJsonFlat; }
  last_op_ids_json(): string { return this.cache.lastOpIdsJson; }

  get_block_json(id: string): string | null { return this.blockCache.get(id) ?? null; }
  list_children_json(parentId: string): string {
    return this.childrenCache.get(parentId) ?? '{"blocks":[],"refs":[]}';
  }
  list_backlinks_json(targetId: string): string {
    return this.backlinksCache.get(targetId) ?? '{"refs":[]}';
  }
  type_defs_json(workspaceId: string): string {
    return this.typeDefsCache.get(workspaceId) ?? '{"blocks":[]}';
  }

  upsert_blocks_json(jsonArray: string): void { upsertBlocks(this.cache, this.blockCache, jsonArray); }
  upsert_refs_json(jsonArray: string): void { upsertRefs(this.cache, jsonArray); }
  upsert_workspace_json(json: string): void { upsertWorkspace(this.workspaces, json); }
  replace_workspaces_json(jsonArray: string): void { replaceWorkspaces(this.workspaces, jsonArray); }

  // Sync override: stores call set_last_op_id fire-and-forget. Cache the
  // value immediately so the next sync read sees it; IPC mirrors in background.
  set_last_op_id_sync(workspaceId: string, id: bigint): void {
    void invoke("blockstoreSetLastOpId", workspaceId, Number(id));
    const map = safeJsonMap(this.cache.lastOpIdsJson);
    map[workspaceId] = id.toString();
    this.cache.lastOpIdsJson = JSON.stringify(map);
  }

  // wasm exposes last_op_id as synchronous bigint; downstream stores read
  // without await. Resolve from the renderer cache to keep that contract.
  last_op_id(workspaceId: string): bigint {
    try {
      const map = safeJsonMap(this.cache.lastOpIdsJson);
      const v = map[workspaceId];
      if (typeof v === "number") return BigInt(v);
      if (typeof v === "string" && v) return BigInt(v);
    } catch { /* fall through */ }
    return 0n;
  }

  async set_last_op_id(workspaceId: string, id: bigint | number): Promise<void> {
    // napi-rs's i64 binding refuses incoming BigInt — widen at the IPC
    // boundary; op_id is a counter that fits in Number.
    const idNum = typeof id === "bigint" ? Number(id) : id;
    const map = safeJsonMap(this.cache.lastOpIdsJson);
    map[workspaceId] = idNum;
    this.cache.lastOpIdsJson = JSON.stringify(map);
    await invoke("blockstoreSetLastOpId", workspaceId, idNum);
  }
}
