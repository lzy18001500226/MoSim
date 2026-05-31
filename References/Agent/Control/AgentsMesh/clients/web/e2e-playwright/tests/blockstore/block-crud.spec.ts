// Migrated R5+: Connect-RPC only (no REST middle layer).
import { randomUUID } from "crypto";

import { test, expect, orgSlug } from "../../fixtures/blockstore.fixture";
import { makeConnectClient } from "../../helpers/connect-client";

// Core CRUD op coverage. createBlock gets exercised in every other spec; the
// rest (updateBlock, deleteBlock, updateRef a.k.a. moveChild) don't. Each has
// subtle contracts (soft-delete, stale-write rejection, nest parent swap)
// worth end-to-end evidence — a regression anywhere shows here as a subtree
// shape mismatch.

async function getSubtreeBlock(
  cc: ReturnType<typeof makeConnectClient>,
  workspaceID: string,
  rootID: string,
  blockID: string,
): Promise<{ data: Record<string, unknown>; text: string | null } | undefined> {
  const res = await cc.blockstore.getSubtree({
    orgSlug,
    workspaceId: workspaceID,
    rootId: rootID,
  }) as { blocks: Array<{ id: string; dataJson: string; text?: string }> };
  const b = res.blocks.find((x) => x.id === blockID);
  if (!b) return undefined;
  return { data: JSON.parse(b.dataJson) as Record<string, unknown>, text: b.text ?? null };
}

async function createTask(
  cc: ReturnType<typeof makeConnectClient>,
  workspaceID: string,
  rootID: string,
  title: string,
): Promise<string> {
  const id = randomUUID();
  await cc.blockstore.applyOps({
    orgSlug,
    workspaceId: workspaceID,
    ops: [
      { op: "createBlock", payloadJson: JSON.stringify({ id, type: "task", data: { title, status: "todo" }, text: title }) },
      { op: "addRef", payloadJson: JSON.stringify({ from: rootID, to: id, rel: "nest", order_key: `zzy${Date.now().toString(36)}${Math.random().toString(36).slice(2, 5)}` }) },
    ],
    idempotencyKey: `e2e-crud-seed-${id}`,
  });
  return id;
}

test("updateBlock round-trips new data and text", async ({ token, isolatedWorkspace }) => {
  const cc = makeConnectClient(token);
  const { id: workspaceID, rootID } = isolatedWorkspace;
  const taskID = await createTask(cc, workspaceID, rootID, "before-update");

  await cc.blockstore.applyOps({
    orgSlug,
    workspaceId: workspaceID,
    ops: [
      {
        op: "updateBlock",
        payloadJson: JSON.stringify({
          id: taskID,
          data: { title: "after-update", status: "done" },
          text: "after-update",
        }),
      },
    ],
    idempotencyKey: `e2e-crud-update-${taskID}`,
  });

  const after = await getSubtreeBlock(cc, workspaceID, rootID, taskID);
  expect(after, "block should still exist after update").toBeDefined();
  expect(after!.data.title).toBe("after-update");
  expect(after!.data.status).toBe("done");
  expect(after!.text).toBe("after-update");
});

test("deleteBlock removes the block from subtree queries", async ({ token, isolatedWorkspace }) => {
  const cc = makeConnectClient(token);
  const { id: workspaceID, rootID } = isolatedWorkspace;
  const taskID = await createTask(cc, workspaceID, rootID, "soft-delete-me");

  await cc.blockstore.applyOps({
    orgSlug,
    workspaceId: workspaceID,
    ops: [{ op: "deleteBlock", payloadJson: JSON.stringify({ id: taskID }) }],
    idempotencyKey: `e2e-crud-delete-${taskID}`,
  });

  const after = await getSubtreeBlock(cc, workspaceID, rootID, taskID);
  expect(after, "soft-deleted block should not surface in subtree").toBeUndefined();
});

test("updateRef moves a block under a new parent", async ({ token, isolatedWorkspace }) => {
  const cc = makeConnectClient(token);
  const { id: workspaceID, rootID } = isolatedWorkspace;
  // Two containers A and B both nested under root; a leaf starts under A
  // and then gets moved under B via updateRef.
  const containerA = randomUUID();
  const containerB = randomUUID();
  const leaf = randomUUID();

  const setupRes = await cc.blockstore.applyOps({
    orgSlug,
    workspaceId: workspaceID,
    ops: [
      { op: "createBlock", payloadJson: JSON.stringify({ id: containerA, type: "list", data: { name: "A" }, text: "A" }) },
      { op: "addRef", payloadJson: JSON.stringify({ from: rootID, to: containerA, rel: "nest", order_key: `zzxa${Date.now()}` }) },
      { op: "createBlock", payloadJson: JSON.stringify({ id: containerB, type: "list", data: { name: "B" }, text: "B" }) },
      { op: "addRef", payloadJson: JSON.stringify({ from: rootID, to: containerB, rel: "nest", order_key: `zzxb${Date.now()}` }) },
      { op: "createBlock", payloadJson: JSON.stringify({ id: leaf, type: "task", data: { title: "moving", status: "todo" }, text: "moving" }) },
      { op: "addRef", payloadJson: JSON.stringify({ from: containerA, to: leaf, rel: "nest", order_key: `aa${Date.now()}` }) },
    ],
    idempotencyKey: `e2e-crud-move-setup-${leaf}`,
  }) as { opIds: unknown[] };
  expect(setupRes.opIds.length).toBe(6);

  // Find the ref id connecting containerA → leaf via the subtree response
  // (the /children endpoint returns Blocks, not Refs — no ref_id exposed).
  const subtree = await cc.blockstore.getSubtree({
    orgSlug,
    workspaceId: workspaceID,
    rootId: rootID,
  }) as { refs: Array<{ id: bigint; fromId: string; toId: string; rel: string }> };
  const leafRef = subtree.refs.find(
    (r) => r.rel === "nest" && r.fromId === containerA && r.toId === leaf,
  );
  expect(leafRef, "leaf should be attached under containerA").toBeDefined();

  // Move: updateRef switches from=A to from=B with a new order_key.
  await cc.blockstore.applyOps({
    orgSlug,
    workspaceId: workspaceID,
    ops: [
      {
        op: "updateRef",
        payloadJson: JSON.stringify({ ref_id: Number(leafRef!.id), from: containerB, order_key: `bb${Date.now()}` }),
      },
    ],
    idempotencyKey: `e2e-crud-move-${leaf}`,
  });

  const after = await cc.blockstore.getSubtree({
    orgSlug,
    workspaceId: workspaceID,
    rootId: rootID,
  }) as { refs: Array<{ id: bigint; fromId: string; toId: string; rel: string }> };
  const leafRefAfter = after.refs.find((r) => r.rel === "nest" && r.toId === leaf);
  expect(leafRefAfter, "moved ref should still exist").toBeDefined();
  expect(leafRefAfter!.fromId).toBe(containerB);
});
