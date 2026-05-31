// Migrated R5+: Connect-RPC only (no REST middle layer).
import { randomUUID } from "crypto";

import { test, expect, orgSlug, installApiProxy, seedAuth } from "../../fixtures/blockstore.fixture";
import { makeConnectClient } from "../../helpers/connect-client";

// Verifies the realtime event broadcast path end-to-end across tabs.
//
// Phase E is real-impl'd — the wasm-side Connect ServerStream bridge in
// clients/core/crates/api-client/src/connect_stream_wasm.rs now drives
// the realtime broadcast path through web-sys fetch + ReadableStream +
// AbortController. Tabs receive `blockstore:op` events live.
test("multi-tab realtime sync: paragraph created in API shows up in both tabs", async ({
  browser,
  token,
  isolatedWorkspace,
}) => {
  const cc = makeConnectClient(token);
  const { id: workspaceID } = isolatedWorkspace;
  const ctxA = await browser.newContext();
  const ctxB = await browser.newContext();
  try {
    for (const ctx of [ctxA, ctxB]) {
      await installApiProxy(ctx);
      await seedAuth(ctx, token);
    }

    const pageA = await ctxA.newPage();
    const pageB = await ctxB.newPage();
    await pageA.goto(`/${orgSlug}/blocks?ws=${workspaceID}`);
    await pageB.goto(`/${orgSlug}/blocks?ws=${workspaceID}`);
    // Wait for both pages to finish hydrating their subtree (DocumentView
    // adds the "+ Add block" button after `useBlock(rootID)` resolves).
    // Without this the ApplyOps below fires before either tab has
    // subscribed to the EventsService stream and the realtime fan-out
    // races the assertion.
    await Promise.all([
      pageA.getByRole("button", { name: "+ Add block" }).waitFor({ state: "visible", timeout: 15_000 }),
      pageB.getByRole("button", { name: "+ Add block" }).waitFor({ state: "visible", timeout: 15_000 }),
    ]);
    // Page hydrated, but EventSubscriptionManager.connect() runs async
    // after the wasm/auth bootstrap. Give the stream a moment to land its
    // first SubscribeRequest with the backend hub before publishing ops
    // — otherwise the fan-out races the subscribe and is dropped.
    await pageA.waitForTimeout(1500);

    const marker = `E2E-SYNC-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    const newID = randomUUID();
    const wsList = await cc.blockstore.listWorkspaces({ orgSlug }) as {
      items: Array<{ id: string; rootBlockId?: string }>;
    };
    const ws = wsList.items.find((w) => w.id === workspaceID)!;
    const rootID = ws.rootBlockId!;
    await cc.blockstore.applyOps({
      orgSlug,
      workspaceId: workspaceID,
      ops: [
        { op: "createBlock", payloadJson: JSON.stringify({ id: newID, type: "paragraph", data: { text: marker }, text: marker }) },
        { op: "addRef", payloadJson: JSON.stringify({ from: rootID, to: newID, rel: "nest", order_key: `zzz${Date.now().toString(36)}` }) },
      ],
      idempotencyKey: `e2e-sync-${newID}`,
    });
    await expect(pageA.getByText(marker)).toBeVisible({ timeout: 10_000 });
    await expect(pageB.getByText(marker)).toBeVisible({ timeout: 10_000 });
  } finally {
    await ctxA.close();
    await ctxB.close();
  }
});
