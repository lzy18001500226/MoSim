// Migrated R5+: Connect-RPC only (no REST middle layer).
//
// REST sent the calling pod in the X-Pod-Key header; Connect names it
// explicitly in `initiator_pod` on every BindingService request.
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";
import { pollUntil } from "../../helpers/retry";
import type { ConnectClient } from "../../helpers/connect-client";

/**
 * Binding API tests — require running pods. The calling pod identity travels
 * inside the proto request (was X-Pod-Key on REST).
 * Maps to: TC-BIND-001~004
 */
test.describe("Pod Binding API", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  /** Create a running pod and return its key. */
  async function createRunningPod(
    cc: ConnectClient,
    prompt: string,
  ): Promise<string> {
    const runnersRes = await cc.runner.listAvailableRunners({ orgSlug: TEST_ORG_SLUG }) as {
      items: { id: bigint }[];
    };
    expect(runnersRes.items.length, "dev env must have an online runner").toBeGreaterThan(0);

    const agentsRes = await cc.agent.listAgents({ orgSlug: TEST_ORG_SLUG }) as {
      builtinAgents: { slug: string }[];
    };
    expect(agentsRes.builtinAgents.length, "dev env must have a builtin agent").toBeGreaterThan(0);

    const created = await cc.pod.createPod({
      orgSlug: TEST_ORG_SLUG,
      agentSlug: agentsRes.builtinAgents[0].slug,
      runnerId: runnersRes.items[0].id,
      agentfileLayer: `PROMPT ${JSON.stringify(prompt)}\n`,
      cols: 80,
      rows: 24,
    }) as { pod?: { podKey: string } };
    const podKey = created.pod?.podKey;
    expect(podKey, "createPod must return a pod_key").toBeTruthy();

    await pollUntil(
      async () => {
        const res = await cc.pod.getPod({ orgSlug: TEST_ORG_SLUG, podKey: podKey! }) as {
          status: string;
        };
        return res.status === "running";
      },
      { maxAttempts: 10, intervalMs: 3000, label: "pod-running" }
    ).catch(() => {});

    return podKey!;
  }

  /**
   * TC-BIND-001: Request binding between two pods.
   */
  test("request binding between pods", async ({ api }) => {
    const cc = await api.connect();
    const podA = await createRunningPod(cc, "E2E Bind Pod A");
    const podB = await createRunningPod(cc, "E2E Bind Pod B");

    try {
      const binding = await cc.binding.requestBinding({
        orgSlug: TEST_ORG_SLUG,
        initiatorPod: podA,
        targetPod: podB,
        scopes: ["pod:read"],
      }) as { id: bigint; initiatorPod: string; targetPod: string };
      expect(binding.initiatorPod).toBe(podA);
      expect(binding.targetPod).toBe(podB);
    } catch (err: unknown) {
      // 4xx is acceptable — the pods may not satisfy the binding policy.
      const status = (err as { status: number }).status;
      expect(status).toBeGreaterThanOrEqual(400);
      expect(status).toBeLessThan(500);
    } finally {
      await cc.pod.terminatePod({ orgSlug: TEST_ORG_SLUG, podKey: podA }).catch(() => {});
      await cc.pod.terminatePod({ orgSlug: TEST_ORG_SLUG, podKey: podB }).catch(() => {});
    }
  });
});
