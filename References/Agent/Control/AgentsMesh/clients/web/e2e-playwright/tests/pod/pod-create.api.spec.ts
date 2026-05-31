// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

type Runner = { id: bigint };
type Agent = { slug: string };
type Pod = { podKey: string };

test.describe("Pod Create API", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  /**
   * TC-POD-001: Create basic pod
   */
  test("create basic pod", async ({ api }) => {
    const cc = await api.connect();
    const { items: runners } = await cc.runner.listAvailableRunners({ orgSlug: TEST_ORG_SLUG }) as { items: Runner[] };
    expect(runners.length, "dev environment must have at least one online runner").toBeGreaterThan(0);

    const { builtinAgents: agents } = await cc.agent.listAgents({ orgSlug: TEST_ORG_SLUG }) as { builtinAgents: Agent[] };
    expect(agents.length, "dev environment must have at least one builtin agent").toBeGreaterThan(0);

    const created = await cc.pod.createPod({
      orgSlug: TEST_ORG_SLUG,
      runnerId: runners[0].id,
      agentSlug: agents[0].slug,
    }) as { pod: Pod };
    const podKey = created.pod?.podKey;
    expect(podKey).toBeTruthy();

    if (podKey) {
      await cc.pod.terminatePod({ orgSlug: TEST_ORG_SLUG, podKey });
    }
  });

  /**
   * TC-POD-003: Terminate pod
   */
  test("terminate pod", async ({ api }) => {
    const cc = await api.connect();
    const { items: runners } = await cc.runner.listAvailableRunners({ orgSlug: TEST_ORG_SLUG }) as { items: Runner[] };
    expect(runners.length, "dev environment must have at least one online runner").toBeGreaterThan(0);

    const { builtinAgents: agents } = await cc.agent.listAgents({ orgSlug: TEST_ORG_SLUG }) as { builtinAgents: Agent[] };
    expect(agents.length, "dev environment must have at least one builtin agent").toBeGreaterThan(0);

    const created = await cc.pod.createPod({
      orgSlug: TEST_ORG_SLUG,
      runnerId: runners[0].id,
      agentSlug: agents[0].slug,
    }) as { pod: Pod };
    const podKey = created.pod?.podKey;
    expect(podKey, "createPod must return a pod_key").toBeTruthy();

    // Connect throws on failure — no need to assert status.
    await cc.pod.terminatePod({ orgSlug: TEST_ORG_SLUG, podKey });
  });
});
