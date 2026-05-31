// Migrated R5+: Connect-RPC only (no REST middle layer).
import { randomUUID } from "crypto";

import { test, expect, orgSlug } from "../../fixtures/blockstore.fixture";
import { makeConnectClient } from "../../helpers/connect-client";

// Trigger fire chain into agent_event blocks: a trigger_def with kind=agent
// matches an op, fireAgentAction writes an agent_event under the trigger
// creator's name (with private ACL), and the agent later reads it via
// memory.retrieve. The webhook variant has its own spec (trigger-fire);
// the agent path needs its own e2e because it touches different code:
// fireAgentAction goes through ApplyOps (recursive into the same service)
// whereas the webhook path uses a plain HTTP client.

interface SubtreeBlock {
  id: string;
  type: string;
  data: Record<string, unknown>;
  meta?: Record<string, unknown>;
}

async function pollUntil<T>(
  fn: () => Promise<T | undefined>,
  timeoutMs: number,
  label: string,
): Promise<T> {
  const deadline = Date.now() + timeoutMs;
  let last: T | undefined;
  while (Date.now() < deadline) {
    try {
      last = await fn();
      if (last !== undefined) return last;
    } catch {
      /* transient; retry */
    }
    await new Promise((r) => setTimeout(r, 100));
  }
  throw new Error(`timeout: ${label}`);
}

test("agent trigger writes an agent_event block on matching task.create", async ({
  token,
  isolatedWorkspace,
}) => {
  const cc = makeConnectClient(token);
  const { id: workspaceID, rootID } = isolatedWorkspace;
  const triggerName = `e2e-agent-trigger-${Date.now()}`;

  // Define an agent trigger. No predicate — every task.create fires.
  await cc.blockstore.applyOps({
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
            action: { kind: "agent", agent_slug: "incident-commander" },
            enabled: true,
          },
          text: triggerName,
        }),
      },
    ],
    idempotencyKey: `e2e-agent-trigger-def-${triggerName}`,
  });

  // Create the matching task. fireAgentAction runs in a goroutine after
  // the originating ApplyOps commits, so we poll the workspace export
  // until the agent_event block surfaces.
  const taskID = randomUUID();
  await cc.blockstore.applyOps({
    orgSlug,
    workspaceId: workspaceID,
    ops: [
      {
        op: "createBlock",
        payloadJson: JSON.stringify({ id: taskID, type: "task", data: { title: "trigger me", status: "todo" } }),
      },
      {
        op: "addRef",
        payloadJson: JSON.stringify({ from: rootID, to: taskID, rel: "nest", order_key: `tr${Date.now().toString(36)}` }),
      },
    ],
    idempotencyKey: `e2e-agent-trigger-task-${taskID}`,
  });

  const ev = await pollUntil(
    async () => {
      // agent_event blocks are written WITHOUT a nest ref to root
      // (fireAgentAction only emits a createBlock op, no addRef), so the
      // /subtree endpoint won't surface them. Use ExportWorkspace which
      // returns every block in the workspace regardless of graph attachment.
      const res = await cc.blockstore.exportWorkspace({
        orgSlug,
        workspaceId: workspaceID,
      }) as { exportJson: string };
      const dump = JSON.parse(res.exportJson) as { blocks?: SubtreeBlock[] };
      const blocks = dump.blocks ?? [];
      return blocks.find(
        (b) => b.type === "agent_event" && b.data?.trigger_name === triggerName,
      );
    },
    8_000,
    `agent_event block for trigger ${triggerName}`,
  );

  expect(ev.data.agent_slug).toBe("incident-commander");
  expect(ev.data.target_type).toBe("task");
  expect(ev.data.target_id).toBe(taskID);
  // Private ACL is the "权限跟着人走" rule in action: the agent_event must
  // be visible only to the trigger's creator so other pods can't pluck it
  // out of a workspace they happen to share with the trigger author.
  const acl = ev.meta?.acl as { visibility?: string } | undefined;
  expect(acl?.visibility).toBe("private");
});
