// Migrated R5+: Connect-RPC only (no REST middle layer).
import { randomUUID } from "crypto";

import { test, expect, orgSlug } from "../../fixtures/blockstore.fixture";
import { makeConnectClient } from "../../helpers/connect-client";

// Guards the F4 fix: repeating an ApplyOps call with the same idempotency_key
// must return the FULL op_id list from the original batch, not just the head.
// Before the fix a 2-op batch returned 1 op_id on replay, leaving clients
// unable to distinguish "second op never ran" from "it ran but wasn't
// reported". Drop this spec and the contract regression is silent.

test("idempotent replay returns the full op_id batch", async ({ token, isolatedWorkspace }) => {
  const cc = makeConnectClient(token);
  const { id: workspaceID, rootID } = isolatedWorkspace;
  const taskID = randomUUID();
  const key = `e2e-idem-${taskID}`;
  const ops = [
    {
      op: "createBlock",
      payloadJson: JSON.stringify({
        id: taskID,
        type: "task",
        data: { title: "idem test", status: "todo" },
        text: "idem test",
      }),
    },
    {
      op: "addRef",
      payloadJson: JSON.stringify({ from: rootID, to: taskID, rel: "nest", order_key: `zzy${Date.now().toString(36)}` }),
    },
  ];

  const first = await cc.blockstore.applyOps({
    orgSlug,
    workspaceId: workspaceID,
    ops,
    idempotencyKey: key,
  }) as { opIds: bigint[]; wasReplay: boolean };
  expect(first.wasReplay).toBe(false);
  expect(first.opIds).toHaveLength(2);

  const second = await cc.blockstore.applyOps({
    orgSlug,
    workspaceId: workspaceID,
    ops,
    idempotencyKey: key,
  }) as { opIds: bigint[]; wasReplay: boolean };
  expect(second.wasReplay).toBe(true);
  // Full batch must round-trip — identical ids in identical order.
  expect(second.opIds).toEqual(first.opIds);

  // And the underlying block must exist exactly once (idempotency isn't
  // faking the response — no duplicate row was inserted).
  const subtree = await cc.blockstore.getSubtree({
    orgSlug,
    workspaceId: workspaceID,
    rootId: rootID,
  }) as { blocks: Array<{ id: string }> };
  const matches = subtree.blocks.filter((b) => b.id === taskID);
  expect(matches).toHaveLength(1);
});
