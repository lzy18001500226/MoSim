// Migrated R5+: Connect-RPC only (no REST middle layer).
import { randomUUID } from "crypto";

import { test, expect, orgSlug } from "../../fixtures/blockstore.fixture";
import { makeConnectClient } from "../../helpers/connect-client";

// Ref-graph invariants — single nest parent + cycle prevention — are
// end-to-end contracts the frontend relies on. Violations must surface as
// 409 so clients can distinguish structural conflicts from server bugs.
// Covered by backend integration tests; this adds Connect-layer evidence
// that the status code mapping is wired through.

test("addRef(nest) to a block with an existing nest parent → 409", async ({
  token,
  isolatedWorkspace,
}) => {
  const cc = makeConnectClient(token);
  const { id: workspaceID, rootID: root } = isolatedWorkspace;
  const parent = randomUUID();
  const child = randomUUID();
  // Setup: child nested under root.
  await cc.blockstore.applyOps({
    orgSlug,
    workspaceId: workspaceID,
    ops: [
      { op: "createBlock", payloadJson: JSON.stringify({ id: parent, type: "list", data: { name: "p" }, text: "p" }) },
      { op: "addRef", payloadJson: JSON.stringify({ from: root, to: parent, rel: "nest", order_key: `pa${Date.now()}` }) },
      { op: "createBlock", payloadJson: JSON.stringify({ id: child, type: "task", data: { title: "c" }, text: "c" }) },
      { op: "addRef", payloadJson: JSON.stringify({ from: parent, to: child, rel: "nest", order_key: `ch${Date.now()}` }) },
    ],
    idempotencyKey: `e2e-single-parent-setup-${child}`,
  });

  // Attempt: a second nest parent for `child` → must fail with 409.
  await expect(
    cc.blockstore.applyOps({
      orgSlug,
      workspaceId: workspaceID,
      ops: [
        { op: "addRef", payloadJson: JSON.stringify({ from: root, to: child, rel: "nest", order_key: `bad${Date.now()}` }) },
      ],
      idempotencyKey: `e2e-single-parent-bad-${child}`,
    }),
  ).rejects.toMatchObject({ status: 409 });
});

test("addRef(nest) creating a cycle → 409", async ({ token, isolatedWorkspace }) => {
  const cc = makeConnectClient(token);
  const { id: workspaceID, rootID: root } = isolatedWorkspace;
  const a = randomUUID();
  const b = randomUUID();
  // Setup: A contains B.
  await cc.blockstore.applyOps({
    orgSlug,
    workspaceId: workspaceID,
    ops: [
      { op: "createBlock", payloadJson: JSON.stringify({ id: a, type: "list", data: { name: "A" }, text: "A" }) },
      { op: "addRef", payloadJson: JSON.stringify({ from: root, to: a, rel: "nest", order_key: `ca${Date.now()}` }) },
      { op: "createBlock", payloadJson: JSON.stringify({ id: b, type: "list", data: { name: "B" }, text: "B" }) },
      { op: "addRef", payloadJson: JSON.stringify({ from: a, to: b, rel: "nest", order_key: `cb${Date.now()}` }) },
    ],
    idempotencyKey: `e2e-cycle-setup-${a}`,
  });

  // Independent pair to isolate the cycle check from single-parent guard.
  const c = randomUUID();
  const d = randomUUID();
  await cc.blockstore.applyOps({
    orgSlug,
    workspaceId: workspaceID,
    ops: [
      { op: "createBlock", payloadJson: JSON.stringify({ id: c, type: "list", data: { name: "C" }, text: "C" }) },
      { op: "createBlock", payloadJson: JSON.stringify({ id: d, type: "list", data: { name: "D" }, text: "D" }) },
      { op: "addRef", payloadJson: JSON.stringify({ from: c, to: d, rel: "nest", order_key: `cd${Date.now()}` }) },
    ],
    idempotencyKey: `e2e-cycle-pair-${c}`,
  });
  // D → C would form a cycle (C → D → C). Must be rejected.
  await expect(
    cc.blockstore.applyOps({
      orgSlug,
      workspaceId: workspaceID,
      ops: [{ op: "addRef", payloadJson: JSON.stringify({ from: d, to: c, rel: "nest", order_key: `dc${Date.now()}` }) }],
      idempotencyKey: `e2e-cycle-bad-${c}`,
    }),
  ).rejects.toMatchObject({ status: 409 });
});
