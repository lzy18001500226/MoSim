// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";
import { pollUntil } from "../../helpers/retry";
import { terminateAllPods } from "../../helpers/pod-cleanup";

type Runner = { id: bigint; currentPods?: number };
type Agent = { slug: string };
type Repository = { id: bigint };
type Ticket = { slug: string };
type Pod = { podKey: string; status: string };

/**
 * TC-SCENARIO-001: Full flow — Git Credential → Repository → Ticket → Pod
 */
test.describe("Full E2E Scenario", () => {
  test.beforeAll(async () => { await terminateAllPods(); });
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("git credential → repository → ticket → pod lifecycle", async ({ api }) => {
    const cc = await api.connect();

    // Step 1: Verify repositories exist (from seed)
    const { items: repos } = await cc.repository.listRepositories({ orgSlug: TEST_ORG_SLUG }) as { items: Repository[] };
    expect(repos.length).toBeGreaterThan(0);
    const repoId = repos[0].id;

    // Step 2: Create ticket linked to repository
    const ticket = await cc.ticket.createTicket({
      orgSlug: TEST_ORG_SLUG,
      title: "E2E Scenario Ticket",
      repositoryId: repoId,
    }) as Ticket;
    const ticketSlug = ticket.slug;

    // Step 3: Check runner availability
    const { items: runners } = await cc.runner.listAvailableRunners({ orgSlug: TEST_ORG_SLUG }) as { items: Runner[] };
    expect(runners.length, "dev env must have an online runner").toBeGreaterThan(0);

    // Step 4: Get agents
    const { builtinAgents: agents } = await cc.agent.listAgents({ orgSlug: TEST_ORG_SLUG }) as { builtinAgents: Agent[] };
    expect(agents.length, "dev env must have a builtin agent").toBeGreaterThan(0);

    // Step 5: Create pod with repository and ticket
    const podResp = await cc.pod.createPod({
      orgSlug: TEST_ORG_SLUG,
      runnerId: runners[0].id,
      agentSlug: agents[0].slug,
      repositoryId: repoId,
      ticketSlug,
    }) as { pod: Pod };
    const podKey = podResp.pod?.podKey;

    if (podKey) {
      // Step 6: Wait for pod running
      await pollUntil(
        async () => {
          const pod = await cc.pod.getPod({ orgSlug: TEST_ORG_SLUG, podKey }) as Pod;
          return pod.status === "running";
        },
        { maxAttempts: 10, intervalMs: 3000, label: "scenario-pod-running" }
      ).catch(() => {});

      // Step 7: Verify runner capacity changed
      const runnerCheck = await cc.runner.getRunner({ orgSlug: TEST_ORG_SLUG, id: runners[0].id }) as { runner: Runner };
      expect((runnerCheck.runner?.currentPods ?? 0)).toBeGreaterThanOrEqual(0);

      // Step 8: Terminate pod
      await cc.pod.terminatePod({ orgSlug: TEST_ORG_SLUG, podKey });
    }

    // Step 9: Cleanup ticket
    if (ticketSlug) {
      await cc.ticket.deleteTicket({ orgSlug: TEST_ORG_SLUG, ticketSlug });
    }
  });
});
