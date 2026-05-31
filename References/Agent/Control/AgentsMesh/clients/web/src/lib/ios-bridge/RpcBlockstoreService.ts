/**
 * iOS embed-mode `BlockstoreService`. Mirrors `WasmBlockstoreService`'s
 * Connect-RPC binary surface (`applyOpsConnect(bytes): Promise<Uint8Array>`
 * etc.) so web's `blockstoreConnect` adapter is unaware of the swap —
 * `registerServiceProvider` is the only difference.
 *
 *   1. Binary `_connect` methods → base64-encode request bytes, post
 *      through `webkit.messageHandlers.amBridge`, base64-decode the
 *      response bytes returned by Swift's `BlockstoreRpcRoute`.
 *   2. State-cache mutators / readers still go through JSON because the
 *      in-process Rust SSOT (view-types) lives behind `apply_remote_op`,
 *      `replace_workspaces_json`, etc.
 *   3. Sync flat-map getters mirror what `refreshFlatCaches` pulled in
 *      so the next zustand selector tick reads the freshest state.
 */

let nextId = 1;
const pending = new Map<number, { resolve: (v: unknown) => void; reject: (e: Error) => void }>();

function ensureBridgeWired() {
  const w = window as unknown as {
    __amResolve?: (id: number, payload: { result?: unknown; error?: string }) => void;
  };
  if (w.__amResolve) return;
  w.__amResolve = (id, payload) => {
    const p = pending.get(id);
    pending.delete(id);
    if (!p) return;
    if (payload.error) p.reject(new Error(payload.error));
    else p.resolve(payload.result);
  };
}

interface IosBridge {
  postMessage: (msg: unknown) => void;
}
function bridge(): IosBridge {
  const w = window as unknown as { webkit?: { messageHandlers?: { amBridge?: IosBridge } } };
  const b = w.webkit?.messageHandlers?.amBridge;
  if (!b) throw new Error("iOS amBridge not available — running outside embed mode?");
  return b;
}

export function rpc<T>(method: string, args: Record<string, unknown> = {}): Promise<T> {
  ensureBridgeWired();
  const id = nextId++;
  return new Promise<T>((resolve, reject) => {
    pending.set(id, { resolve: resolve as (v: unknown) => void, reject });
    bridge().postMessage({ id, method, args });
  });
}

function toBase64(bytes: Uint8Array): string {
  let out = "";
  for (let i = 0; i < bytes.length; i++) out += String.fromCharCode(bytes[i]);
  return btoa(out);
}

function fromBase64(s: string): Uint8Array {
  const raw = atob(s);
  const out = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i++) out[i] = raw.charCodeAt(i);
  return out;
}

async function rpcConnect(method: string, bytes: Uint8Array): Promise<Uint8Array> {
  const respB64 = await rpc<string>(method, { bytes: toBase64(bytes) });
  return fromBase64(respB64);
}

/**
 * Sync getters need a value the millisecond a zustand selector fires.
 * Native is async, so we mirror the flat maps here. `refreshFlatCaches`
 * runs after every mutation to keep the mirror tight.
 */
export class RpcBlockstoreService {
  private _workspacesJson = "{}";
  private _blocksJson = "{}";
  private _refsJson = "{}";
  private _nestChildrenJson = "{}";
  private _backlinksJson = "{}";
  private _lastOpIdsJson = "{}";

  private async refreshFlatCaches(): Promise<void> {
    const [w, b, r, nc, bl, lo] = await Promise.all([
      rpc<string>("workspaces_json"),
      rpc<string>("blocks_json"),
      rpc<string>("refs_json"),
      rpc<string>("nest_children_json"),
      rpc<string>("backlinks_json"),
      rpc<string>("last_op_ids_json"),
    ]);
    this._workspacesJson = w || "{}";
    this._blocksJson = b || "{}";
    this._refsJson = r || "{}";
    this._nestChildrenJson = nc || "{}";
    this._backlinksJson = bl || "{}";
    this._lastOpIdsJson = lo || "{}";
  }

  // ── Connect-RPC binary wire (matches WasmBlockstoreService)

  async applyOpsConnect(bytes: Uint8Array): Promise<Uint8Array> {
    const resp = await rpcConnect("apply_ops_connect", bytes);
    await this.refreshFlatCaches();
    return resp;
  }
  async listWorkspacesConnect(bytes: Uint8Array): Promise<Uint8Array> {
    const resp = await rpcConnect("list_workspaces_connect", bytes);
    await this.refreshFlatCaches();
    return resp;
  }
  async ensureDefaultWorkspaceConnect(bytes: Uint8Array): Promise<Uint8Array> {
    const resp = await rpcConnect("ensure_default_workspace_connect", bytes);
    await this.refreshFlatCaches();
    return resp;
  }
  async createWorkspaceConnect(bytes: Uint8Array): Promise<Uint8Array> {
    const resp = await rpcConnect("create_workspace_connect", bytes);
    await this.refreshFlatCaches();
    return resp;
  }
  async deleteWorkspaceConnect(bytes: Uint8Array): Promise<Uint8Array> {
    const resp = await rpcConnect("delete_workspace_connect", bytes);
    await this.refreshFlatCaches();
    return resp;
  }
  async getBlockConnect(bytes: Uint8Array): Promise<Uint8Array> {
    return rpcConnect("get_block_connect", bytes);
  }
  async listChildrenConnect(bytes: Uint8Array): Promise<Uint8Array> {
    return rpcConnect("list_children_connect", bytes);
  }
  async listBacklinksConnect(bytes: Uint8Array): Promise<Uint8Array> {
    return rpcConnect("list_backlinks_connect", bytes);
  }
  async getSubtreeConnect(bytes: Uint8Array): Promise<Uint8Array> {
    const resp = await rpcConnect("get_subtree_connect", bytes);
    await this.refreshFlatCaches();
    return resp;
  }
  async streamOpsConnect(bytes: Uint8Array): Promise<Uint8Array> {
    const resp = await rpcConnect("stream_ops_connect", bytes);
    await this.refreshFlatCaches();
    return resp;
  }
  async listTypeDefsConnect(bytes: Uint8Array): Promise<Uint8Array> {
    const resp = await rpcConnect("list_type_defs_connect", bytes);
    await this.refreshFlatCaches();
    return resp;
  }
  async semanticSearchConnect(bytes: Uint8Array): Promise<Uint8Array> {
    return rpcConnect("semantic_search_connect", bytes);
  }

  // ── State-cache mutators (web pushes server bytes into Rust cache via JSON)

  apply_remote_op(opJson: string): void {
    void rpc("apply_remote_op", { op: JSON.parse(opJson) }).then(() => this.refreshFlatCaches());
  }

  set_last_op_id(wsId: string, id: number): void {
    void rpc("set_last_op_id", { wsId, id });
  }

  replace_workspaces_json(json: string): void {
    void rpc("replace_workspaces_json", { json }).then(() => this.refreshFlatCaches());
  }
  upsert_workspace_json(json: string): void {
    void rpc("upsert_workspace_json", { json }).then(() => this.refreshFlatCaches());
  }
  upsert_blocks_json(json: string): void {
    void rpc("upsert_blocks_json", { json }).then(() => this.refreshFlatCaches());
  }
  upsert_refs_json(json: string): void {
    void rpc("upsert_refs_json", { json }).then(() => this.refreshFlatCaches());
  }

  // ── Sync flat-map readers (used by zustand selectors)

  workspaces_json(): string { return this._workspacesJson; }
  blocks_json(): string { return this._blocksJson; }
  refs_json(): string { return this._refsJson; }
  nest_children_json(): string { return this._nestChildrenJson; }
  backlinks_json(): string { return this._backlinksJson; }
  last_op_ids_json(): string { return this._lastOpIdsJson; }

  // ── Sync per-id readers — served from the cached flat maps

  get_block_json(id: string): string | null {
    const map = safeParse<Record<string, unknown>>(this._blocksJson);
    const block = map?.[id];
    return block ? JSON.stringify(block) : null;
  }

  list_children_json(id: string): string {
    const idx = safeParse<Record<string, unknown[]>>(this._nestChildrenJson) ?? {};
    const blocks = safeParse<Record<string, unknown>>(this._blocksJson) ?? {};
    const refs = safeParse<Record<string, unknown>>(this._refsJson) ?? {};
    const childRefIds = (idx[id] as unknown[] | undefined) ?? [];
    const childBlocks: unknown[] = [];
    const childRefs: unknown[] = [];
    for (const rid of childRefIds as Array<string | number>) {
      const ref = refs[String(rid)] as { to_id?: string } | undefined;
      if (!ref) continue;
      childRefs.push(ref);
      const child = ref.to_id ? blocks[ref.to_id] : undefined;
      if (child) childBlocks.push(child);
    }
    return JSON.stringify({ blocks: childBlocks, refs: childRefs });
  }

  list_backlinks_json(id: string): string {
    const idx = safeParse<Record<string, unknown[]>>(this._backlinksJson) ?? {};
    const refs = safeParse<Record<string, unknown>>(this._refsJson) ?? {};
    const refIds = (idx[id] as unknown[] | undefined) ?? [];
    const out: unknown[] = [];
    for (const rid of refIds as Array<string | number>) {
      const ref = refs[String(rid)];
      if (ref) out.push(ref);
    }
    return JSON.stringify({ refs: out });
  }

  type_defs_json(_wsId: string): string {
    const blocks = safeParse<Record<string, { workspace_id?: string; type?: string }>>(this._blocksJson) ?? {};
    const out: unknown[] = [];
    for (const b of Object.values(blocks)) {
      if (b?.workspace_id === _wsId && b?.type === "type-def") out.push(b);
    }
    return JSON.stringify({ blocks: out });
  }

  last_op_id(wsId: string): number {
    const map = safeParse<Record<string, number>>(this._lastOpIdsJson);
    return map?.[wsId] ?? 0;
  }
}

function safeParse<T>(s: string): T | undefined {
  try { return JSON.parse(s) as T; } catch { return undefined; }
}

export async function primeSubtreeCache(_wsId: string, _rootId: string): Promise<void> {
  // No-op stub — primed lazily when the binary getSubtreeConnect lands.
}
