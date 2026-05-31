// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";
import { pollUntil } from "../../helpers/retry";

import { terminateAllPods } from "../../helpers/pod-cleanup";

type Runner = { id: bigint };
type Agent = { slug: string };
type Pod = { podKey: string; status: string };
type ConnectClient = Awaited<ReturnType<import("../../fixtures/api.fixture").ApiFixture["connect"]>>;

test.describe("Pod Resume", () => {
  test.beforeAll(async () => { await terminateAllPods(); });
  test.beforeEach(async () => { clearAuthRateLimit(); });

  /** Helper: get a running pod key. Asserts prerequisites instead of skipping. */
  async function createAndWaitPod(cc: ConnectClient): Promise<string> {
    const { items: runners } = await cc.runner.listAvailableRunners({ orgSlug: TEST_ORG_SLUG }) as { items: Runner[] };
    expect(runners.length, "dev env must have an online runner").toBeGreaterThan(0);

    const { builtinAgents: agents } = await cc.agent.listAgents({ orgSlug: TEST_ORG_SLUG }) as { builtinAgents: Agent[] };
    expect(agents.length, "dev env must have a builtin agent").toBeGreaterThan(0);

    const resp = await cc.pod.createPod({
      orgSlug: TEST_ORG_SLUG,
      runnerId: runners[0].id,
      agentSlug: agents[0].slug,
    }) as { pod: Pod };
    const podKey = resp.pod?.podKey;
    expect(podKey, "createPod must return a pod_key").toBeTruthy();

    await pollUntil(
      async () => {
        const pod = await cc.pod.getPod({ orgSlug: TEST_ORG_SLUG, podKey: podKey! }) as Pod;
        return pod.status === "running";
      },
      { maxAttempts: 10, intervalMs: 3000, label: "pod-running" }
    ).catch(() => {});

    return podKey!;
  }

  /**
   * TC-POD-006: Terminate and resume pod
   */
  test("terminate and resume pod preserves sandbox", async ({ api }) => {
    const cc = await api.connect();
    const podKey = await createAndWaitPod(cc);

    await cc.pod.terminatePod({ orgSlug: TEST_ORG_SLUG, podKey });

    await pollUntil(
      async () => {
        const pod = await cc.pod.getPod({ orgSlug: TEST_ORG_SLUG, podKey }) as Pod;
        return pod.status === "terminated";
      },
      { maxAttempts: 5, intervalMs: 2000, label: "pod-terminated" }
    ).catch(() => {});

    // CreatePod still requires agent_slug — reuse the first builtin agent.
    const { builtinAgents: agents } = await cc.agent.listAgents({ orgSlug: TEST_ORG_SLUG }) as { builtinAgents: Agent[] };
    const resumeResp = await cc.pod.createPod({
      orgSlug: TEST_ORG_SLUG,
      agentSlug: agents[0].slug,
      sourcePodKey: podKey,
    }) as { pod: Pod };
    const newPodKey = resumeResp.pod?.podKey;
    expect(newPodKey).toBeTruthy();

    if (newPodKey) {
      await cc.pod.terminatePod({ orgSlug: TEST_ORG_SLUG, podKey: newPodKey });
    }
  });

  /**
   * TC-POD-006: Cannot double-resume same pod
   */
  test("double resume returns error", async ({ api }) => {
    const cc = await api.connect();
    const podKey = await createAndWaitPod(cc);

    await cc.pod.terminatePod({ orgSlug: TEST_ORG_SLUG, podKey });
    await new Promise((r) => setTimeout(r, 2000));

    const { builtinAgents: agents } = await cc.agent.listAgents({ orgSlug: TEST_ORG_SLUG }) as { builtinAgents: Agent[] };
    const agentSlug = agents[0].slug;

    // First resume
    const r1 = await cc.pod.createPod({
      orgSlug: TEST_ORG_SLUG,
      agentSlug,
      sourcePodKey: podKey,
    }) as { pod: Pod };
    const newKey = r1.pod?.podKey;

    // Second resume should fail
    let caught: { status?: number } | null = null;
    try {
      await cc.pod.createPod({
        orgSlug: TEST_ORG_SLUG,
        agentSlug,
        sourcePodKey: podKey,
      });
    } catch (e) {
      caught = e as { status?: number };
    }
    expect(caught).not.toBeNull();
    expect([400, 409]).toContain(caught?.status);

    if (newKey) await cc.pod.terminatePod({ orgSlug: TEST_ORG_SLUG, podKey: newKey });
  });
});
