// Migrated R5+: Connect-RPC only (no REST middle layer).
import { createServer, type IncomingMessage, type Server } from "http";
import { AddressInfo } from "net";

import { test, expect, orgSlug } from "../../fixtures/blockstore.fixture";
import { makeConnectClient } from "../../helpers/connect-client";

// Tier 3 闭环 E2E: agent defines a trigger whose predicate matches when a
// task transitions to status=done → creating such a task fires the webhook.
// The test spins up a tiny HTTP listener on the host and points the trigger
// at `localhost` (the only loopback hostname the dev allowlist permits —
// bare `127.0.0.1` is rejected so the security-guards SSRF test stays
// meaningful).
test("trigger.define → matching task.create fires the webhook", async ({
  token,
  isolatedWorkspace,
}) => {
  const cc = makeConnectClient(token);
  const { id: workspaceID, rootID } = isolatedWorkspace;
  // 1. Stand up a temporary webhook listener. Port 0 asks the OS for a free
  // port so concurrent test runs don't collide.
  const received: Array<{ trigger: string; target: { type: string } }> = [];
  const { server, port } = await startLocalWebhook(received);

  try {
    const triggerName = `e2e-trigger-done-${Date.now()}`;
    // Write the trigger as a trigger_def block directly. SSRF guard lives
    // in the service layer (validateTriggerDefData) so private URLs are
    // rejected here too — the dev env allows `localhost` via
    // BLOCKSTORE_WEBHOOK_ALLOW_HOSTS (not the bare 127.0.0.1, since the
    // security-guards e2e relies on that being rejected).
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
              predicate: '{status} == "done"',
              action: {
                kind: "webhook",
                url: `http://localhost:${port}/hook`,
              },
              enabled: true,
            },
            text: triggerName,
          }),
        },
      ],
      idempotencyKey: `e2e-trigger-define-${triggerName}`,
    });

    // 2. Create a matching task. First create one that should NOT fire (status=todo)
    // and verify nothing arrives — rules out "the engine fires for every op".
    await createTask(cc, workspaceID, rootID, "todo");
    await new Promise((r) => setTimeout(r, 500));
    expect(received).toEqual([]);

    // 3. Now create a task with status=done — predicate should match and the
    // webhook should land within a couple of seconds.
    await createTask(cc, workspaceID, rootID, "done");
    await waitUntil(
      () => received.some((r) => r.trigger === triggerName),
      5_000,
      "webhook was not fired for done task",
    );
    const match = received.find((r) => r.trigger === triggerName)!;
    expect(match.target.type).toBe("task");
  } finally {
    await new Promise<void>((resolve) => server.close(() => resolve()));
  }
});

interface HookPayload {
  trigger: string;
  target: { type: string };
}

async function startLocalWebhook(sink: HookPayload[]): Promise<{ server: Server; port: number }> {
  const server = createServer((req: IncomingMessage, res) => {
    const chunks: Buffer[] = [];
    req.on("data", (c: Buffer) => chunks.push(c));
    req.on("end", () => {
      try {
        const body = JSON.parse(Buffer.concat(chunks).toString("utf8"));
        sink.push(body as HookPayload);
      } catch {
        /* malformed — leave unrecorded; test will surface via waitUntil */
      }
      res.statusCode = 200;
      res.end(JSON.stringify({ ok: true }));
    });
  });
  await new Promise<void>((resolve) => server.listen(0, "0.0.0.0", resolve));
  const { port } = server.address() as AddressInfo;
  return { server, port };
}

async function createTask(
  cc: ReturnType<typeof makeConnectClient>,
  workspaceID: string,
  rootID: string,
  status: string,
) {
  const id = crypto.randomUUID();
  await cc.blockstore.applyOps({
    orgSlug,
    workspaceId: workspaceID,
    ops: [
      {
        op: "createBlock",
        payloadJson: JSON.stringify({ id, type: "task", data: { title: `e2e task ${status}`, status }, text: `e2e ${status}` }),
      },
      {
        op: "addRef",
        payloadJson: JSON.stringify({ from: rootID, to: id, rel: "nest", order_key: `zzz${Date.now().toString(36)}` }),
      },
    ],
    idempotencyKey: `e2e-trigger-${id}`,
  });
}

async function waitUntil(pred: () => boolean, timeoutMs: number, label: string) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    if (pred()) return;
    await new Promise((r) => setTimeout(r, 150));
  }
  throw new Error(`timeout waiting for condition: ${label}`);
}
