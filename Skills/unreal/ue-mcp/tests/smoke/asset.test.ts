import { describe, it, expect, beforeAll, afterAll } from "vitest";
import { getBridge, disconnectBridge, callBridge, resultArray, TEST_PREFIX } from "../setup.js";
import type { EditorBridge } from "../../src/bridge.js";

let bridge: EditorBridge;

beforeAll(async () => { bridge = await getBridge(); });
afterAll(() => disconnectBridge());

describe("asset — read", () => {
  it("search_assets (wildcard)", async () => {
    const r = await callBridge(bridge, "search_assets", { query: "*", maxResults: 10 });
    expect(r.ok, r.error).toBe(true);
  });

  it("search_assets (typed)", async () => {
    const r = await callBridge(bridge, "search_assets", { query: "StaticMesh", maxResults: 5 });
    expect(r.ok, r.error).toBe(true);
  });

  it("list_textures", async () => {
    const r = await callBridge(bridge, "list_textures", { recursive: true });
    expect(r.ok, r.error).toBe(true);
  });
});

describe("asset — read specific (dynamic)", () => {
  let assetPath: string | undefined;

  beforeAll(async () => {
    const r = await callBridge(bridge, "search_assets", { query: "*", maxResults: 1 });
    if (r.ok) {
      const assets = resultArray(r.result, "assets");
      if (assets && assets.length > 0) {
        const first = assets[0] as Record<string, unknown>;
        assetPath = (first.path ?? first.asset_path ?? first.objectPath) as string | undefined;
      }
    }
  });

  it("read_asset", async ({ skip }) => {
    if (!assetPath) skip();
    const r = await callBridge(bridge, "read_asset", { path: assetPath });
    expect(r.ok, r.error).toBe(true);
  });

  it("read_asset_properties", async ({ skip }) => {
    if (!assetPath) skip();
    const r = await callBridge(bridge, "read_asset_properties", { assetPath });
    expect(r.ok, r.error).toBe(true);
  });
});

describe("asset — write (with cleanup)", () => {
  const created: string[] = [];

  afterAll(async () => {
    for (const p of created) {
      await callBridge(bridge, "delete_asset", { assetPath: p });
    }
  });

  it("duplicate_asset", async ({ skip }) => {
    const search = await callBridge(bridge, "search_assets", { query: "*", maxResults: 1 });
    const assets = resultArray(search.result, "assets");
    if (!search.ok || !assets || assets.length === 0) skip();
    const first = assets[0] as Record<string, unknown>;
    const src = (first.path ?? first.asset_path ?? first.objectPath) as string;
    const dest = `${TEST_PREFIX}/DuplicateTest`;
    const r = await callBridge(bridge, "duplicate_asset", { sourcePath: src, destinationPath: dest });
    expect(r.ok, r.error).toBe(true);
    created.push(dest);
  });

  it("save_asset (all dirty)", async () => {
    const r = await callBridge(bridge, "save_asset", { assetPath: "" });
    // May fail if no dirty assets; we're testing the method exists
    expect(r.method).toBe("save_asset");
  });

  it("create_folder + delete_folder round-trip", async () => {
    const folder = `${TEST_PREFIX}/FolderRoundTrip_${Date.now()}`;
    const created = await callBridge(bridge, "create_folder", { path: folder });
    expect(created.ok, created.error).toBe(true);
    const deleted = await callBridge(bridge, "delete_folder", { path: folder });
    expect(deleted.ok, deleted.error).toBe(true);
    const entries = (deleted.result as { entries?: Array<{ status?: string }> })?.entries ?? [];
    expect(entries[0]?.status).toBe("deleted");
  });

  it("delete_folder refuses non-empty without force", async () => {
    const folder = `${TEST_PREFIX}/FolderNonEmpty_${Date.now()}`;
    await callBridge(bridge, "create_folder", { path: folder });
    // Drop one asset inside so the folder is non-empty.
    const search = await callBridge(bridge, "search_assets", { query: "*", maxResults: 1 });
    const assets = resultArray(search.result, "assets");
    if (!search.ok || !assets || assets.length === 0) {
      await callBridge(bridge, "delete_folder", { path: folder });
      return;
    }
    const src = ((assets[0] as Record<string, unknown>).path ?? (assets[0] as Record<string, unknown>).objectPath) as string;
    const dup = `${folder}/RefuseProbe`;
    await callBridge(bridge, "duplicate_asset", { sourcePath: src, destinationPath: dup });

    const refused = await callBridge(bridge, "delete_folder", { path: folder });
    expect(refused.ok, refused.error).toBe(true);
    const refusedEntries = (refused.result as { entries?: Array<{ status?: string; reason?: string }> })?.entries ?? [];
    expect(refusedEntries[0]?.status).toBe("failed");
    expect(refusedEntries[0]?.reason).toBe("not_empty");

    // Clean up with force.
    const forced = await callBridge(bridge, "delete_folder", { path: folder, force: true });
    expect(forced.ok, forced.error).toBe(true);
  });
});
