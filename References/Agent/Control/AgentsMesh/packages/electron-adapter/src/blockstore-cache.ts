import { invoke } from "./invoke";
import { rebuildNestAndBacklinks, safeArray, safeJsonMap, type CacheState } from "./blockstore-apply";

// Bulk JSON-blob mutators driven by the renderer after each Connect fetch
// (getSubtree / listWorkspaces / listTypeDefs). They keep CacheState in sync
// with what just landed on the wire so the synchronous zustand selectors see
// the new data without a round-trip back to the main process.

export interface WorkspacesRef { value: string }

export function upsertBlocks(cache: CacheState, blockCache: Map<string, string>, jsonArray: string): void {
  const blocks = safeArray<Record<string, unknown>>(jsonArray);
  if (blocks.length === 0) return;
  const map = safeJsonMap(cache.blocksJson);
  for (const b of blocks) {
    const id = b?.id;
    if (typeof id === "string") {
      map[id] = b;
      blockCache.set(id, JSON.stringify(b));
    }
  }
  cache.blocksJson = JSON.stringify(map);
}

export function upsertRefs(cache: CacheState, jsonArray: string): void {
  const refs = safeArray<Record<string, unknown>>(jsonArray);
  if (refs.length === 0) return;
  const map = safeJsonMap(cache.refsJson);
  for (const r of refs) {
    const id = r?.id;
    if (typeof id === "number" || typeof id === "string") {
      map[String(id)] = r;
    }
  }
  cache.refsJson = JSON.stringify(map);
  rebuildNestAndBacklinks(cache);
}

export function upsertWorkspace(ref: WorkspacesRef, json: string): void {
  let ws: Record<string, unknown>;
  try { ws = JSON.parse(json) as Record<string, unknown>; }
  catch { return; }
  const id = ws?.id;
  if (typeof id !== "string") return;
  const map = safeJsonMap(ref.value);
  map[id] = ws;
  ref.value = JSON.stringify(map);
}

export function replaceWorkspaces(ref: WorkspacesRef, jsonArray: string): void {
  const items = safeArray<Record<string, unknown>>(jsonArray);
  const map: Record<string, unknown> = {};
  for (const ws of items) {
    const id = ws?.id;
    if (typeof id === "string") map[id] = ws;
  }
  ref.value = JSON.stringify(map);
}

// Subtree hydration: walks the tree depth-first starting at `rootId`,
// populating the per-id JSON caches used by sync getters. Runs once after
// `blockstoreLoadSubtree` lands in main.
export async function hydrateSubtree(
  rootId: string,
  blockCache: Map<string, string>,
  childrenCache: Map<string, string>,
): Promise<void> {
  const seen = new Set<string>();
  await hydrateNode(rootId, seen, blockCache, childrenCache);
}

async function hydrateNode(
  id: string,
  seen: Set<string>,
  blockCache: Map<string, string>,
  childrenCache: Map<string, string>,
): Promise<void> {
  if (seen.has(id)) return;
  seen.add(id);
  const [blockJson, childrenJson] = await Promise.all([
    invoke<string | null>("blockstoreGetBlockJson", id),
    invoke<string>("blockstoreListChildrenJson", id),
  ]);
  if (blockJson) blockCache.set(id, blockJson);
  childrenCache.set(id, childrenJson);
  try {
    const { blocks } = JSON.parse(childrenJson) as { blocks?: Array<{ id: string }> };
    if (!blocks?.length) return;
    for (const b of blocks) blockCache.set(b.id, JSON.stringify(b));
    await Promise.all(blocks.map((b) => hydrateNode(b.id, seen, blockCache, childrenCache)));
  } catch {
    // malformed payload — leave node cached with what we already have
  }
}
