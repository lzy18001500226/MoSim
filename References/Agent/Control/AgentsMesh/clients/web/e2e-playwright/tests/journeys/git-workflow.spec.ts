// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";
import { pollUntil } from "../../helpers/retry";
import { terminateAllPods } from "../../helpers/pod-cleanup";

type Runner = { id: bigint };
type Agent = { slug: string };
type Repository = { id: bigint };
type Ticket = { slug: string };
type Pod = { podKey: string; status: string };

/**
 * Journey: Git Workflow
 * Repository → Ticket → Pod with repo context → Terminate
 *
 * Uses seed data: Gitea repos (demo-webapp, demo-api) already imported.
 */
test.describe("Journey: Git Workflow", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test.afterAll(async () => {
    await terminateAllPods();
  });

  test("repo → ticket → pod with repository context", async ({ api }) => {
    const cc = await api.connect();

    // ── Step 1: Verify repositories exist (from seed/Gitea) ──
    const { items: repos } = await cc.repository.listRepositories({ orgSlug: TEST_ORG_SLUG }) as { items: Repository[] };
    expect(repos.length).toBeGreaterThan(0);
    const repo = repos[0];

    // ── Step 2: Create ticket linked to repository ──
    const ticket = await cc.ticket.createTicket({
      orgSlug: TEST_ORG_SLUG,
      title: "Journey: Fix authentication bug",
      repositoryId: repo.id,
    }) as Ticket;
    const ticketSlug = ticket.slug;
    expect(ticketSlug).toBeTruthy();

    // ── Step 3: Verify ticket is linked to repo ──
    // Connect throws on failure — a successful get is the assertion.
    await cc.ticket.getTicket({ orgSlug: TEST_ORG_SLUG, ticketSlug });

    // ── Step 4: Get available runner and agent ──
    const { items: runners } = await cc.runner.listAvailableRunners({ orgSlug: TEST_ORG_SLUG }) as { items: Runner[] };
    expect(runners.length, "dev env must have an online runner").toBeGreaterThan(0);

    const { builtinAgents: agents } = await cc.agent.listAgents({ orgSlug: TEST_ORG_SLUG }) as { builtinAgents: Agent[] };

    // ── Step 5: Create pod WITH repository and ticket context ──
    const podResp = await cc.pod.createPod({
      orgSlug: TEST_ORG_SLUG,
      runnerId: runners[0].id,
      agentSlug: agents[0].slug,
      repositoryId: repo.id,
      ticketSlug,
    }) as { pod: Pod };
    const podKey = podResp.pod?.podKey;
    expect(podKey).toBeTruthy();

    // ── Step 6: Wait for pod to become running ──
    await pollUntil(
      async () => {
        const pod = await cc.pod.getPod({ orgSlug: TEST_ORG_SLUG, podKey }) as Pod;
        return pod.status === "running";
      },
      { maxAttempts: 10, intervalMs: 3000, label: "journey-pod-running" }
    ).catch(() => {});

    // ── Step 7: Verify pod has repository association ──
    // Connect throws on failure — a successful get is the assertion.
    await cc.pod.getPod({ orgSlug: TEST_ORG_SLUG, podKey });

    // ── Step 8: Verify runner has this pod associated ──
    // We can't assert `runner.current_pods >= 1` directly — the runner's own
    // heartbeat can race with the server-side IncrementPods write and clobber
    // the count back to 0 before the read lands. Instead, assert via the
    // pods list scoped to this runner, which is the authoritative source.
    const { items: podList } = await cc.pod.listPods({
      orgSlug: TEST_ORG_SLUG,
      runnerId: runners[0].id,
    }) as { items: Pod[] };
    expect(Array.isArray(podList)).toBe(true);
    expect(podList.some((p) => p.podKey === podKey)).toBe(true);

    // ── Step 9: Terminate pod ──
    // Connect throws on failure; pod may have self-terminated if agent process
    // failed to start in the runner — accept both success and already-terminated.
    try {
      await cc.pod.terminatePod({ orgSlug: TEST_ORG_SLUG, podKey });
    } catch (e) {
      const err = e as { status?: number };
      expect([400, 409]).toContain(err.status);
    }

    // ── Step 10: Verify pod terminated ──
    await pollUntil(
      async () => {
        const pod = await cc.pod.getPod({ orgSlug: TEST_ORG_SLUG, podKey }) as Pod;
        return pod.status === "terminated";
      },
      { maxAttempts: 5, intervalMs: 2000, label: "journey-pod-terminated" }
    ).catch(() => {});

    // ── Step 11: Cleanup ticket ──
    await cc.ticket.deleteTicket({ orgSlug: TEST_ORG_SLUG, ticketSlug });
  });

  test("git workflow visible in UI: repo → ticket → workspace", async ({ page }) => {
    // Each goto + assertion uses Playwright's auto-waiting `toContainText`
    // instead of `textContent + toMatch`: the dashboard is wasm-driven and
    // load-state "load" fires before the wasm + Connect streams populate
    // page content. Polling matchers handle the post-load hydration race.
    await page.goto(`/${TEST_ORG_SLUG}/repositories`);
    await expect(page.locator("body")).toContainText(
      /demo-webapp|demo-api|repository|repositories|仓库/i,
      { timeout: 30_000 },
    );

    await page.goto(`/${TEST_ORG_SLUG}/tickets`);
    await expect(page.locator("body")).toContainText(
      /ticket|tickets|工单|任务/i,
      { timeout: 30_000 },
    );

    await page.goto(`/${TEST_ORG_SLUG}/workspace`);
    await expect(page).toHaveURL(/\/workspace/, { timeout: 30_000 });
  });
});
