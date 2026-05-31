// Migrated R5+: Connect-RPC only (no REST middle layer).
import { randomUUID } from "crypto";

import { test, expect, orgSlug } from "../../fixtures/blockstore.fixture";
import { makeConnectClient } from "../../helpers/connect-client";

// Optimistic concurrency: when two clients both read a block at version T0
// and try to update, the second update must reject (HTTP 409, mapped from
// blockstore.ErrStaleUpdate) rather than silently overwrite. The server
// trusts ExpectedUpdatedAt to detect the conflict; without this spec a
// regression that drops the check would silently lose writes — a bug
// pattern that's invisible to load tests because the response status stays
// 200, only the row contents diverge.

async function fetchBlock(
  cc: ReturnType<typeof makeConnectClient>,
  workspaceID: string,
  rootID: string,
  blockID: string,
): Promise<{ id: string; updated_at: string; data: Record<string, unknown> }> {
  const subtree = await cc.blockstore.getSubtree({
    orgSlug,
    workspaceId: workspaceID,
    rootId: rootID,
  }) as { blocks: Array<{ id: string; updatedAt: string; dataJson: string }> };
  const found = subtree.blocks.find((b) => b.id === blockID);
  if (!found) throw new Error(`block ${blockID} not found in subtree`);
  return { id: found.id, updated_at: found.updatedAt, data: JSON.parse(found.dataJson) as Record<string, unknown> };
}

test("stale ExpectedUpdatedAt → 409, fresh one → 200", async ({
  token,
  isolatedWorkspace,
}) => {
  const cc = makeConnectClient(token);
  const { id: workspaceID, rootID } = isolatedWorkspace;
  const blockID = randomUUID();
  // Seed a task block under the workspace root.
  await cc.blockstore.applyOps({
    orgSlug,
    workspaceId: workspaceID,
    ops: [
      {
        op: "createBlock",
        payloadJson: JSON.stringify({ id: blockID, type: "task", data: { title: "stale", status: "todo" }, text: "stale" }),
      },
      {
        op: "addRef",
        payloadJson: JSON.stringify({ from: rootID, to: blockID, rel: "nest", order_key: `s${Date.now().toString(36)}` }),
      },
    ],
    idempotencyKey: `e2e-stale-setup-${blockID}`,
  });

  const before = await fetchBlock(cc, workspaceID, rootID, blockID);

  // First update with the matching expected_updated_at must succeed.
  await cc.blockstore.applyOps({
    orgSlug,
    workspaceId: workspaceID,
    ops: [
      {
        op: "updateBlock",
        payloadJson: JSON.stringify({
          id: blockID,
          data: { status: "in_progress" },
          expected_updated_at: before.updated_at,
        }),
      },
    ],
    idempotencyKey: `e2e-stale-first-${blockID}`,
  });

  // Second update with the SAME (now stale) expected_updated_at must 409.
  await expect(
    cc.blockstore.applyOps({
      orgSlug,
      workspaceId: workspaceID,
      ops: [
        {
          op: "updateBlock",
          payloadJson: JSON.stringify({
            id: blockID,
            data: { status: "done" },
            expected_updated_at: before.updated_at,
          }),
        },
      ],
      idempotencyKey: `e2e-stale-second-${blockID}`,
    }),
  ).rejects.toMatchObject({ status: 409 });

  // Confirm the block contents reflect the FIRST update only — the stale
  // attempt did not partially apply.
  const after = await fetchBlock(cc, workspaceID, rootID, blockID);
  expect(after.data.status).toBe("in_progress");

  // A fresh expected_updated_at (post-first-write) must again succeed.
  await cc.blockstore.applyOps({
    orgSlug,
    workspaceId: workspaceID,
    ops: [
      {
        op: "updateBlock",
        payloadJson: JSON.stringify({
          id: blockID,
          data: { status: "done" },
          expected_updated_at: after.updated_at,
        }),
      },
    ],
    idempotencyKey: `e2e-stale-third-${blockID}`,
  });
});

test("update without expected_updated_at always succeeds (no version check)", async ({
  token,
  isolatedWorkspace,
}) => {
  // The optimistic check is opt-in: a payload without the field must accept
  // even after the row has been mutated by another writer. Documents the
  // last-write-wins escape hatch the field is the explicit signal for.
  const cc = makeConnectClient(token);
  const { id: workspaceID, rootID } = isolatedWorkspace;
  const blockID = randomUUID();
  await cc.blockstore.applyOps({
    orgSlug,
    workspaceId: workspaceID,
    ops: [
      { op: "createBlock", payloadJson: JSON.stringify({ id: blockID, type: "task", data: { title: "lww", status: "todo" } }) },
      { op: "addRef", payloadJson: JSON.stringify({ from: rootID, to: blockID, rel: "nest", order_key: `l${Date.now().toString(36)}` }) },
    ],
    idempotencyKey: `e2e-lww-setup-${blockID}`,
  });

  await cc.blockstore.applyOps({
    orgSlug,
    workspaceId: workspaceID,
    ops: [{ op: "updateBlock", payloadJson: JSON.stringify({ id: blockID, data: { status: "in_progress" } }) }],
    idempotencyKey: `e2e-lww-first-${blockID}`,
  });
  await cc.blockstore.applyOps({
    orgSlug,
    workspaceId: workspaceID,
    ops: [{ op: "updateBlock", payloadJson: JSON.stringify({ id: blockID, data: { status: "done" } }) }],
    idempotencyKey: `e2e-lww-second-${blockID}`,
  });
});
