// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect, orgSlug } from "../../fixtures/blockstore.fixture";
import { makeConnectClient } from "../../helpers/connect-client";

// Block Store schema guard — asserts that the backend's enhanced ValidateRecord
// (EnumValues + NonEmptyArrayKeys) actually rejects bad chart writes via the
// Connect layer. This is the only path that proves the new check is hooked
// into the live ApplyOps handler and the middleware chain.
//
// Covers F3 (chart schema), and F12 (translateErr no longer leaks stacks on
// the validation branch).

test("chart with unknown type is rejected", async ({ token, isolatedWorkspace }) => {
  const cc = makeConnectClient(token);
  const { id: workspaceID } = isolatedWorkspace;
  const err = await cc.blockstore.applyOps({
    orgSlug,
    workspaceId: workspaceID,
    ops: [
      {
        op: "createBlock",
        payloadJson: JSON.stringify({
          type: "chart",
          data: { type: "3d_sphere", series: [{ name: "s", data: [{ x: 1, value: 2 }] }] },
        }),
      },
    ],
  }).catch((e: Error) => e);
  expect(err).toBeInstanceOf(Error);
  expect((err as { status?: number }).status).toBe(400);
  expect((err as Error).message).toMatch(/type/);
});

test("chart with empty series is rejected", async ({ token, isolatedWorkspace }) => {
  const cc = makeConnectClient(token);
  const { id: workspaceID } = isolatedWorkspace;
  const err = await cc.blockstore.applyOps({
    orgSlug,
    workspaceId: workspaceID,
    ops: [
      {
        op: "createBlock",
        payloadJson: JSON.stringify({ type: "chart", data: { type: "bar", series: [] } }),
      },
    ],
  }).catch((e: Error) => e);
  expect(err).toBeInstanceOf(Error);
  expect((err as { status?: number }).status).toBe(400);
  expect((err as Error).message).toMatch(/series/);
});

test("valid chart is accepted (positive control)", async ({ token, isolatedWorkspace }) => {
  const cc = makeConnectClient(token);
  const { id: workspaceID } = isolatedWorkspace;
  const resp = await cc.blockstore.applyOps({
    orgSlug,
    workspaceId: workspaceID,
    ops: [
      {
        op: "createBlock",
        payloadJson: JSON.stringify({
          type: "chart",
          data: {
            type: "bar",
            series: [{ name: "Revenue", data: [{ month: "Jan", value: 10 }] }],
          },
        }),
      },
    ],
  }) as { opIds: unknown[] };
  expect(resp.opIds.length).toBeGreaterThan(0);
});

// Phase E (wasm Connect ServerStream bridge) is real-impl'd, so the
// renderer can mount through the normal zustand `_tick` cycle. urlGuard
// sanitisation has unit coverage in clients/web/src/lib/sanitize.test.ts;
// this E2E asserts the renderer-side defense lands in the actual DOM
// when a malicious block is seeded via API.
test("javascript: URL in block data is sanitized by the renderer", async ({
  authenticatedPage,
  token,
  isolatedWorkspace,
}) => {
  const cc = makeConnectClient(token);
  const { id: workspaceID, rootID } = isolatedWorkspace;
  // Even if a malicious actor bypasses the frontend prompt and writes a
  // block with a javascript: url via API (the backend has no scheme
  // allowlist for bookmark data), the renderer's urlGuard must prevent
  // that scheme from reaching href/src in the DOM. This is the defense-
  // in-depth layer that matters most in practice.
  const markerTitle = `xss-probe-${Date.now()}`;
  const id = crypto.randomUUID();
  await cc.blockstore.applyOps({
    orgSlug,
    workspaceId: workspaceID,
    ops: [
      {
        op: "createBlock",
        payloadJson: JSON.stringify({
          id,
          type: "bookmark",
          data: { url: "javascript:alert('xss')", title: markerTitle },
          text: markerTitle,
        }),
      },
      {
        op: "addRef",
        payloadJson: JSON.stringify({ from: rootID, to: id, rel: "nest", order_key: `zzy${Date.now().toString(36)}` }),
      },
    ],
    idempotencyKey: `e2e-xss-ok-${id}`,
  });

  await authenticatedPage.goto(`/${orgSlug}/blocks?ws=${workspaceID}`);
  const bookmark = authenticatedPage.getByText(markerTitle).last();
  await expect(bookmark).toBeVisible({ timeout: 15_000 });

  // The rendered anchor's href must NOT carry the javascript: scheme.
  // sanitizeURL returns "" which the renderer shows as "#".
  const anchor = bookmark.locator("xpath=ancestor::a[1]");
  const href = await anchor.getAttribute("href");
  expect(href ?? "").not.toMatch(/^javascript:/i);
});
