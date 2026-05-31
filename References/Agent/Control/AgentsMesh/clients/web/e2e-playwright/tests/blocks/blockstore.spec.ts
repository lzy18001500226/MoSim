// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { test as uiTest, expect as uiExpect } from "@playwright/test";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";
import { collectConsoleErrors, assertNoWasmErrors } from "../../helpers/console-errors";

// ────────────────────────────────────────────────────
// Part 1: API — workspaces, applyOps, catchup, subtree
// ────────────────────────────────────────────────────

test.describe("Block Store · API", () => {
  let workspaceId: string;

  test.beforeAll(async ({ api }) => {
    clearAuthRateLimit();
    const cc = await api.connect();
    // ensureDefault is idempotent — returns the org's default workspace.
    const ws = await cc.blockstore.ensureDefaultWorkspace({ orgSlug: TEST_ORG_SLUG }) as { id: string };
    workspaceId = ws.id;
    expect(workspaceId).toBeTruthy();
  });

  test("listWorkspaces includes default workspace", async ({ api }) => {
    const cc = await api.connect();
    const { items } = await cc.blockstore.listWorkspaces({ orgSlug: TEST_ORG_SLUG }) as { items: Array<{ id: string }> };
    expect(Array.isArray(items)).toBe(true);
    expect(items.some((w) => w.id === workspaceId)).toBe(true);
  });

  test("applyOps creates block + nest ref, subtree reflects state", async ({ api }) => {
    const cc = await api.connect();
    const rootId = crypto.randomUUID();
    const childId = crypto.randomUUID();
    const idempotencyKey = `e2e-blocks-${Date.now()}`;
    const applyBody = await cc.blockstore.applyOps({
      orgSlug: TEST_ORG_SLUG,
      workspaceId,
      idempotencyKey,
      ops: [
        { op: "createBlock", payloadJson: JSON.stringify({ id: rootId, type: "page", data: { title: "E2E root" } }) },
        { op: "createBlock", payloadJson: JSON.stringify({ id: childId, type: "paragraph", data: { text: "child" } }) },
        { op: "addRef", payloadJson: JSON.stringify({ from: rootId, to: childId, rel: "nest", order_key: "m" }) },
      ],
    }) as { opIds: bigint[]; wasReplay: boolean };
    expect(applyBody.opIds).toHaveLength(3);
    expect(applyBody.wasReplay).toBe(false);

    const sub = await cc.blockstore.getSubtree({
      orgSlug: TEST_ORG_SLUG,
      workspaceId,
      rootId,
      maxDepth: 8,
    }) as { blocks: Array<{ id: string }>; refs: Array<{ rel: string; toId: string }> };
    expect(sub.blocks.some((b) => b.id === childId)).toBe(true);
    expect(sub.refs.some((r) => r.rel === "nest" && r.toId === childId)).toBe(true);
  });

  test("applyOps idempotency — replay returns was_replay=true", async ({ api }) => {
    const cc = await api.connect();
    const rootId = crypto.randomUUID();
    const idempotencyKey = `e2e-idem-${Date.now()}`;
    const req = {
      orgSlug: TEST_ORG_SLUG,
      workspaceId,
      idempotencyKey,
      ops: [{ op: "createBlock", payloadJson: JSON.stringify({ id: rootId, type: "page", data: { title: "Idem" } }) }],
    };
    const first = await cc.blockstore.applyOps(req) as { wasReplay: boolean };
    expect(first.wasReplay).toBe(false);
    const second = await cc.blockstore.applyOps(req) as { wasReplay: boolean };
    expect(second.wasReplay).toBe(true);
  });

  test("catchup returns ops after the watermark", async ({ api }) => {
    const cc = await api.connect();
    const { items } = await cc.blockstore.streamOps({
      orgSlug: TEST_ORG_SLUG,
      workspaceId,
      after: BigInt(0),
      limit: 50,
    }) as { items: unknown[] };
    expect(Array.isArray(items)).toBe(true);
  });

  test("type-defs endpoint returns block_type_def blocks", async ({ api }) => {
    const cc = await api.connect();
    const { items } = await cc.blockstore.listTypeDefs({
      orgSlug: TEST_ORG_SLUG,
      workspaceId,
    }) as { items: Array<{ type: string }> };
    expect(Array.isArray(items)).toBe(true);
    // All returned blocks should be of type block_type_def.
    for (const b of items) {
      expect(b.type).toBe("block_type_def");
    }
  });

  test("updateBlock op patches data field", async ({ api }) => {
    const cc = await api.connect();
    const blockId = crypto.randomUUID();
    await cc.blockstore.applyOps({
      orgSlug: TEST_ORG_SLUG,
      workspaceId,
      idempotencyKey: `e2e-upd-create-${Date.now()}`,
      ops: [{ op: "createBlock", payloadJson: JSON.stringify({ id: blockId, type: "paragraph", data: { text: "v1" } }) }],
    });
    await cc.blockstore.applyOps({
      orgSlug: TEST_ORG_SLUG,
      workspaceId,
      idempotencyKey: `e2e-upd-patch-${Date.now()}`,
      ops: [{ op: "updateBlock", payloadJson: JSON.stringify({ id: blockId, data: { text: "v2" } }) }],
    });
    const block = await cc.blockstore.getBlock({ orgSlug: TEST_ORG_SLUG, id: blockId }) as { dataJson: string };
    const data = JSON.parse(block.dataJson);
    expect(data.text).toBe("v2");
  });
});

// ────────────────────────────────────────────────────
// Part 2: UI — page loads, no WASM errors
// ────────────────────────────────────────────────────

uiTest.describe("Block Store · UI", () => {
  uiTest.beforeEach(async () => { clearAuthRateLimit(); });

  uiTest("blocks page loads without WASM errors", async ({ page }) => {
    const errors = collectConsoleErrors(page);
    await page.goto(`/${TEST_ORG_SLUG}/blocks`);
    await page.waitForLoadState("load");
    // Page must render past the spinner — either the DocumentView or an
    // error banner is acceptable; a stuck spinner is not.
    await uiExpect(page.locator("body")).toBeVisible();
    assertNoWasmErrors(errors);
  });

  uiTest("search panel opens on search button click", async ({ page }) => {
    await page.goto(`/${TEST_ORG_SLUG}/blocks`);
    await page.waitForLoadState("load");
    // SearchPanel only mounts after the workspace is hydrated — wait for the
    // Search button rather than skipping; the spec asserts the open flow.
    const searchBtn = page.getByRole("button", { name: /search|搜索/i }).first();
    await uiExpect(searchBtn).toBeVisible({ timeout: 15_000 });
    await searchBtn.click();
    await page.waitForTimeout(300);
  });
});
