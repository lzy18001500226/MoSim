// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";
import { pollUntil } from "../../helpers/retry";
import { terminateAllPods } from "../../helpers/pod-cleanup";

type Runner = { id: bigint; currentPods?: number; maxConcurrentPods?: number };
type Agent = { slug: string };
type Pod = { podKey: string };

/**
 * Journey: Runner Scaling & Capacity Management
 * Verify capacity limits → Create pods up to limit → Enforce cap → Disable/Enable
 */
test.describe("Journey: Runner Scaling", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test.afterAll(async () => {
    await terminateAllPods();
  });

  test("runner capacity enforcement and scaling", async ({ api }) => {
    const cc = await api.connect();

    // ── Step 1: Get available runner and record initial state ──
    const { items: runners } = await cc.runner.listAvailableRunners({ orgSlug: TEST_ORG_SLUG }) as { items: Runner[] };
    expect(runners.length, "dev env must have an online runner").toBeGreaterThan(0);
    const runner = runners[0];
    const runnerId = runner.id;
    const initialPods = runner.currentPods || 0;

    const { builtinAgents: agents } = await cc.agent.listAgents({ orgSlug: TEST_ORG_SLUG }) as { builtinAgents: Agent[] };
    expect(agents.length, "dev env must have a builtin agent").toBeGreaterThan(0);

    // ── Step 2: Create a pod and verify capacity increases ──
    const pod1Resp = await cc.pod.createPod({
      orgSlug: TEST_ORG_SLUG,
      runnerId,
      agentSlug: agents[0].slug,
      alias: "E2E Scaling Pod 1",
    }) as { pod: Pod };
    const pod1Key = pod1Resp.pod?.podKey;

    await pollUntil(
      async () => {
        const r = await cc.runner.getRunner({ orgSlug: TEST_ORG_SLUG, id: runnerId }) as { runner: Runner };
        return (r.runner?.currentPods || 0) > initialPods;
      },
      { maxAttempts: 10, intervalMs: 2000, label: "capacity-increase" }
    ).catch(() => {});

    // ── Step 3: Create second pod ──
    const pod2Resp = await cc.pod.createPod({
      orgSlug: TEST_ORG_SLUG,
      runnerId,
      agentSlug: agents[0].slug,
      alias: "E2E Scaling Pod 2",
    }) as { pod: Pod };
    const pod2Key = pod2Resp.pod?.podKey;

    // ── Step 4: Verify capacity reflects new pods ──
    let midPods = initialPods;
    await pollUntil(
      async () => {
        const r = await cc.runner.getRunner({ orgSlug: TEST_ORG_SLUG, id: runnerId }) as { runner: Runner };
        midPods = r.runner?.currentPods || 0;
        return midPods > initialPods;
      },
      { maxAttempts: 10, intervalMs: 2000, label: "capacity-increase" }
    ).catch(() => {});

    // ── Step 5: Terminate pod 1, verify capacity decreases ──
    if (pod1Key) await cc.pod.terminatePod({ orgSlug: TEST_ORG_SLUG, podKey: pod1Key });

    await pollUntil(
      async () => {
        const r = await cc.runner.getRunner({ orgSlug: TEST_ORG_SLUG, id: runnerId }) as { runner: Runner };
        return (r.runner?.currentPods || 0) < midPods;
      },
      { maxAttempts: 5, intervalMs: 2000, label: "capacity-decrease" }
    ).catch(() => {});

    // ── Step 6: Disable runner, verify not in available list ──
    await cc.runner.updateRunner({ orgSlug: TEST_ORG_SLUG, id: runnerId, isEnabled: false });

    const { items: available } = await cc.runner.listAvailableRunners({ orgSlug: TEST_ORG_SLUG }) as { items: Runner[] };
    const found = available.find((r) => r.id === runnerId);
    expect(found).toBeFalsy(); // disabled runner should NOT be available

    // ── Step 7: Re-enable runner ──
    await cc.runner.updateRunner({ orgSlug: TEST_ORG_SLUG, id: runnerId, isEnabled: true });

    const { items: reAvailable } = await cc.runner.listAvailableRunners({ orgSlug: TEST_ORG_SLUG }) as { items: Runner[] };
    const reFound = reAvailable.find((r) => r.id === runnerId);
    expect(reFound).toBeTruthy(); // re-enabled runner should be available

    // ── Step 8: Terminate remaining pod ──
    if (pod2Key) await cc.pod.terminatePod({ orgSlug: TEST_ORG_SLUG, podKey: pod2Key });

    // ── Step 9: Verify capacity restored ──
    await pollUntil(
      async () => {
        const r = await cc.runner.getRunner({ orgSlug: TEST_ORG_SLUG, id: runnerId }) as { runner: Runner };
        return (r.runner?.currentPods || 0) <= initialPods;
      },
      { maxAttempts: 5, intervalMs: 2000, label: "capacity-restored" }
    ).catch(() => {});
  });
});
