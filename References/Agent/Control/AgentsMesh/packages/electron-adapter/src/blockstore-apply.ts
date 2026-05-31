// Mirrors clients/core/crates/state/src/blockstore_apply.rs in TypeScript so the
// renderer-side cache (which is the Electron SSOT after the R6 wasm-Connect
// flip) stays converged without round-tripping through the Rust main-process
// service for every op.

export function safeArray<T>(json: string): T[] {
  try {
    const parsed = JSON.parse(json);
    return Array.isArray(parsed) ? (parsed as T[]) : [];
  } catch { return []; }
}

export function safeJsonMap(json: string): Record<string, unknown> {
  try {
    const parsed = JSON.parse(json);
    return parsed && typeof parsed === "object" && !Array.isArray(parsed)
      ? (parsed as Record<string, unknown>)
      : {};
  } catch { return {}; }
}

export interface CacheState {
  blocksJson: string;
  refsJson: string;
  nestChildrenJson: string;
  backlinksJsonFlat: string;
  lastOpIdsJson: string;
}

interface BlockLike { id: string; workspace_id?: string; type?: string; data?: unknown; text?: string | null; meta?: unknown; updated_at?: string }
interface RefLike { id: number; workspace_id?: string; from_id: string; to_id: string; rel: string; order_key?: string | null; anchor?: string | null; meta?: unknown; updated_at?: string }
interface OpLike { id: number; workspace_id: string; op: string; forward: Record<string, unknown>; applied_at: string; actor_id?: number }

export function applyOpToCache(state: CacheState, op: OpLike): void {
  switch (op.op) {
    case "createBlock": applyCreateBlock(state, op); break;
    case "updateBlock": applyUpdateBlock(state, op); break;
    case "deleteBlock": applyDeleteBlock(state, op); break;
    case "addRef":      applyAddRef(state, op); break;
    case "removeRef":   applyRemoveRef(state, op); break;
    case "updateRef":   applyUpdateRef(state, op); break;
  }
  bumpLastOpId(state, op.workspace_id, op.id);
}

function applyCreateBlock(state: CacheState, op: OpLike): void {
  const fwd = op.forward ?? {};
  const id = typeof fwd.id === "string" ? fwd.id : undefined;
  const ty = typeof fwd.type === "string" ? fwd.type : undefined;
  if (!id || !ty) return;
  const block: BlockLike = {
    id, workspace_id: op.workspace_id, type: ty,
    data: fwd.data ?? {}, text: typeof fwd.text === "string" ? fwd.text : null,
    meta: fwd.meta ?? {}, updated_at: op.applied_at,
  };
  const map = safeJsonMap(state.blocksJson);
  map[id] = { ...(map[id] as object ?? {}), ...block, created_at: (map[id] as BlockLike)?.updated_at ?? op.applied_at };
  state.blocksJson = JSON.stringify(map);
}

function applyUpdateBlock(state: CacheState, op: OpLike): void {
  const fwd = op.forward ?? {};
  const id = typeof fwd.id === "string" ? fwd.id : undefined;
  if (!id) return;
  const map = safeJsonMap(state.blocksJson);
  const existing = (map[id] as Record<string, unknown>) ?? { id };
  map[id] = { ...existing, ...fwd, updated_at: op.applied_at };
  state.blocksJson = JSON.stringify(map);
}

function applyDeleteBlock(state: CacheState, op: OpLike): void {
  const id = typeof op.forward?.id === "string" ? (op.forward.id as string) : undefined;
  if (!id) return;
  const blocks = safeJsonMap(state.blocksJson);
  delete blocks[id];
  state.blocksJson = JSON.stringify(blocks);
  // Remove refs touching id and reindex.
  const refs = safeJsonMap(state.refsJson);
  for (const [rid, r] of Object.entries(refs)) {
    const ref = r as RefLike;
    if (ref?.from_id === id || ref?.to_id === id) delete refs[rid];
  }
  state.refsJson = JSON.stringify(refs);
  rebuildIndexes(state);
}

function applyAddRef(state: CacheState, op: OpLike): void {
  const fwd = op.forward ?? {};
  const id = typeof fwd.id === "number" ? fwd.id : undefined;
  const from = typeof fwd.from === "string" ? fwd.from : undefined;
  const to = typeof fwd.to === "string" ? fwd.to : undefined;
  const rel = typeof fwd.rel === "string" ? fwd.rel : undefined;
  if (id === undefined || !from || !to || !rel) return;
  const refs = safeJsonMap(state.refsJson);
  refs[String(id)] = {
    id, workspace_id: op.workspace_id, from_id: from, to_id: to, rel,
    order_key: typeof fwd.order_key === "string" ? fwd.order_key : null,
    anchor: typeof fwd.anchor === "string" ? fwd.anchor : null,
    meta: fwd.meta ?? {}, updated_at: op.applied_at, created_at: op.applied_at,
  };
  state.refsJson = JSON.stringify(refs);
  rebuildIndexes(state);
}

function applyRemoveRef(state: CacheState, op: OpLike): void {
  const fwd = op.forward ?? {};
  const rid = typeof fwd.ref_id === "number" ? fwd.ref_id : undefined;
  if (rid === undefined) return;
  const refs = safeJsonMap(state.refsJson);
  delete refs[String(rid)];
  state.refsJson = JSON.stringify(refs);
  rebuildIndexes(state);
}

function applyUpdateRef(state: CacheState, op: OpLike): void {
  const fwd = op.forward ?? {};
  const rid = typeof fwd.ref_id === "number" ? fwd.ref_id : undefined;
  if (rid === undefined) return;
  const refs = safeJsonMap(state.refsJson);
  const existing = (refs[String(rid)] as Record<string, unknown>) ?? {};
  const patch: Record<string, unknown> = { updated_at: op.applied_at };
  if (typeof fwd.from === "string") patch.from_id = fwd.from;
  for (const k of ["order_key", "anchor", "meta"] as const) {
    if (k in fwd) patch[k] = fwd[k];
  }
  refs[String(rid)] = { ...existing, ...patch };
  state.refsJson = JSON.stringify(refs);
  rebuildIndexes(state);
}

function rebuildIndexes(state: CacheState): void {
  rebuildNestAndBacklinks(state);
}

export function rebuildNestAndBacklinks(state: CacheState): void {
  const refs = safeJsonMap(state.refsJson);
  const nest: Record<string, number[]> = {};
  const backlinks: Record<string, number[]> = {};
  const list = Object.values(refs) as RefLike[];
  list.sort((a, b) => {
    const ak = a.order_key ?? "";
    const bk = b.order_key ?? "";
    if (ak === bk) return (a.id ?? 0) - (b.id ?? 0);
    if (ak && bk) return ak < bk ? -1 : 1;
    if (!ak && !bk) return (a.id ?? 0) - (b.id ?? 0);
    return ak ? -1 : 1;
  });
  for (const r of list) {
    if (!r || typeof r.id !== "number") continue;
    if (r.rel === "nest") {
      (nest[r.from_id] ??= []).push(r.id);
    } else {
      (backlinks[r.to_id] ??= []).push(r.id);
    }
  }
  state.nestChildrenJson = JSON.stringify(nest);
  state.backlinksJsonFlat = JSON.stringify(backlinks);
}

function bumpLastOpId(state: CacheState, wsId: string, opId: number): void {
  const map = safeJsonMap(state.lastOpIdsJson);
  const cur = map[wsId];
  const curNum = typeof cur === "number" ? cur : (typeof cur === "string" ? Number(cur) : 0);
  if (opId > curNum) {
    map[wsId] = opId;
    state.lastOpIdsJson = JSON.stringify(map);
  }
}
