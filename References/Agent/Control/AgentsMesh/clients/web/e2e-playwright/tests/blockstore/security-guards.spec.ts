// Migrated R5+: Connect-RPC only (no REST middle layer).
import { randomUUID } from "crypto";

import { test, expect, orgSlug } from "../../fixtures/blockstore.fixture";
import { makeConnectClient } from "../../helpers/connect-client";

// Covers F2 (SSRF guard) and F6 (iframe sandbox). These are the two layers
// that together stop a malicious Agent from (a) using the backend as an
// internal-network HTTP probe via trigger webhooks and (b) escaping the
// embed iframe to manipulate the host page.

async function applyTriggerDef(
  cc: ReturnType<typeof makeConnectClient>,
  workspaceID: string,
  triggerName: string,
  action: Record<string, unknown>,
): Promise<Error | null> {
  return cc.blockstore.applyOps({
    orgSlug,
    workspaceId: workspaceID,
    ops: [
      {
        op: "createBlock",
        payloadJson: JSON.stringify({
          type: "trigger_def",
          data: {
            name: triggerName,
            target_type: "task",
            on: "create",
            action,
            enabled: true,
          },
          text: triggerName,
        }),
      },
    ],
    idempotencyKey: `e2e-ssrf-${triggerName}`,
  }).then(() => null).catch((e: Error) => e);
}

test("trigger.define with loopback URL is rejected", async ({ token, isolatedWorkspace }) => {
  const cc = makeConnectClient(token);
  const { id: workspaceID } = isolatedWorkspace;
  const err = await applyTriggerDef(cc, workspaceID, `ssrf-loopback-${Date.now()}`, {
    kind: "webhook",
    url: "http://127.0.0.1:5432/hook",
  });
  expect(err).toBeInstanceOf(Error);
  expect((err as { status?: number }).status).toBe(400);
  expect((err as Error).message).toMatch(/action\.url|private|reserved/i);
});

test("trigger.define with AWS metadata URL is rejected", async ({ token, isolatedWorkspace }) => {
  const cc = makeConnectClient(token);
  const { id: workspaceID } = isolatedWorkspace;
  const err = await applyTriggerDef(cc, workspaceID, `ssrf-aws-${Date.now()}`, {
    kind: "webhook",
    url: "http://169.254.169.254/latest/meta-data/",
  });
  expect((err as { status?: number }).status).toBe(400);
});

test("trigger.define with RFC1918 URL is rejected", async ({ token, isolatedWorkspace }) => {
  const cc = makeConnectClient(token);
  const { id: workspaceID } = isolatedWorkspace;
  const err = await applyTriggerDef(cc, workspaceID, `ssrf-rfc1918-${Date.now()}`, {
    kind: "webhook",
    url: "http://10.0.0.1/hook",
  });
  expect((err as { status?: number }).status).toBe(400);
});

test("trigger.define with javascript: scheme is rejected", async ({ token, isolatedWorkspace }) => {
  const cc = makeConnectClient(token);
  const { id: workspaceID } = isolatedWorkspace;
  const err = await applyTriggerDef(cc, workspaceID, `ssrf-js-${Date.now()}`, {
    kind: "webhook",
    url: "javascript:alert(1)",
  });
  expect((err as { status?: number }).status).toBe(400);
});

// Phase E (wasm Connect ServerStream bridge) is now live (real fetch +
// ReadableStream + AbortController in connect_stream_wasm.rs). With the
// realtime path no longer a stub, the embed iframe should render via the
// regular zustand `_tick` rerender on `loadSubtree` completion. The
// unit-level test for the sandbox attribute lives in EmbedRenderer.test.
test("embed iframe carries a strict sandbox attribute", async ({
  authenticatedPage,
  token,
  isolatedWorkspace,
}) => {
  const cc = makeConnectClient(token);
  const { id: workspaceID, rootID } = isolatedWorkspace;
  // Seed an embed block pointing at a known YouTube URL so the renderer
  // picks the iframe branch. We use raw API write so the test doesn't
  // depend on window.prompt which Playwright handles awkwardly.
  const id = randomUUID();
  await cc.blockstore.applyOps({
    orgSlug,
    workspaceId: workspaceID,
    ops: [
      {
        op: "createBlock",
        payloadJson: JSON.stringify({
          id,
          type: "embed",
          data: { url: "https://www.youtube.com/watch?v=dQw4w9WgXcQ", provider: "youtube" },
          text: "yt",
        }),
      },
      {
        op: "addRef",
        payloadJson: JSON.stringify({ from: rootID, to: id, rel: "nest", order_key: `zzx${Date.now().toString(36)}` }),
      },
    ],
    idempotencyKey: `e2e-sandbox-${id}`,
  });

  await authenticatedPage.goto(`/${orgSlug}/blocks?ws=${workspaceID}`);
  const iframe = authenticatedPage.locator(`iframe[src*="youtube.com/embed"]`).last();
  await expect(iframe).toBeAttached({ timeout: 15_000 });

  const sandbox = await iframe.getAttribute("sandbox");
  expect(sandbox, "iframe must have sandbox attribute").toBeTruthy();
  // The allowed tokens — no allow-top-navigation, no allow-forms.
  expect(sandbox).toContain("allow-scripts");
  expect(sandbox).toContain("allow-same-origin");
  expect(sandbox).not.toContain("allow-top-navigation");
  expect(sandbox).not.toContain("allow-forms");
});
