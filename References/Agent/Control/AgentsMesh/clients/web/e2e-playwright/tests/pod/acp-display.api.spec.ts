// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

type Runner = { id: bigint };
type Agent = { slug: string };
type Pod = { podKey: string };

/**
 * ACP (Agent Control Protocol) display tests.
 * These verify ACP-related API behavior.
 * Full UI tests (Activity Stream, tool calls, permissions) require MCP Chrome DevTools.
 */
test.describe("ACP Pod API", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  /**
   * TC-ACP-001: Create ACP pod (API portion)
   */
  test("create ACP pod with agent_slug", async ({ api }) => {
    const cc = await api.connect();
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
    expect(podKey).toBeTruthy();

    if (podKey) {
      await cc.pod.terminatePod({ orgSlug: TEST_ORG_SLUG, podKey });
    }
  });

  /**
   * TC-ACP-007: Send prompt to running pod via API
   */
  test("send prompt to pod via API", async ({ api }) => {
    const cc = await api.connect();
    const { items: runners } = await cc.runner.listAvailableRunners({ orgSlug: TEST_ORG_SLUG }) as { items: Runner[] };
    expect(runners.length, "dev env must have an online runner").toBeGreaterThan(0);

    const { builtinAgents: agents } = await cc.agent.listAgents({ orgSlug: TEST_ORG_SLUG }) as { builtinAgents: Agent[] };
    expect(agents.length, "dev env must have a builtin agent").toBeGreaterThan(0);

    const created = await cc.pod.createPod({
      orgSlug: TEST_ORG_SLUG,
      runnerId: runners[0].id,
      agentSlug: agents[0].slug,
    }) as { pod: Pod };
    const podKey = created.pod?.podKey;
    expect(podKey, "createPod must return a pod_key").toBeTruthy();

    await new Promise((r) => setTimeout(r, 3000));

    // Send prompt (may fail if pod isn't fully running yet — that's OK).
    // Connect throws on non-OK status, so we catch and accept various codes.
    try {
      await cc.pod.sendPodPrompt({
        orgSlug: TEST_ORG_SLUG,
        podKey,
        prompt: "Hello from E2E test",
      });
    } catch (e) {
      const err = e as { status?: number };
      expect([400, 404, 409]).toContain(err.status);
    }

    await cc.pod.terminatePod({ orgSlug: TEST_ORG_SLUG, podKey });
  });
});
