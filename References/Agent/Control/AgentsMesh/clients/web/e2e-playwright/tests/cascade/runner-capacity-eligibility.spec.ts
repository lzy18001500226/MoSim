// Cascade test (P0): updating a runner's max_concurrent_pods MUST immediately
// affect runner-eligibility — once the runner is at capacity, the next
// ListAvailableRunners call MUST exclude it. If a stale-capacity cache
// (e.g. the Rust core runner state isn't re-evaluated against MaxConcurrentPods
// on every call) crept in, this assertion turns red.
//
// Two scenarios:
//   * Drop max_concurrent_pods to 0 → runner immediately filtered out of
//     ListAvailableRunners. Restore.
//   * is_enabled=false has the same effect — eligibility flips immediately.
//
// We exercise the eligibility query rather than CreatePod because:
//   1. CreatePod under quota pressure depends on whether any *other* runner
//      is eligible (multi-runner dev env) — flaky for a quota-only assertion.
//   2. The eligibility query is the SSOT used by both auto-select and the
//      runner picker dropdown; testing it covers both surfaces.
import { test, expect } from "../../fixtures/index";
import { TEST_USER, TEST_ORG_SLUG } from "../../helpers/env";

interface RunnerSummary {
  id: bigint;
  nodeId: string;
  maxConcurrentPods: number;
  isEnabled: boolean;
  status: string;
}

test.describe("Cascade: runner capacity/enabled → ListAvailableRunners reflects immediately", () => {
  test("setting max_concurrent_pods=0 removes runner from available list", async ({ api }) => {
    await api.login(TEST_USER.email, TEST_USER.password);
    const cc = await api.connect();

    // Pick the dev-runner. The dev seed boots it as enabled with maxConcurrentPods=5.
    const { items: allRunners } = (await cc.runner.listRunners({
      orgSlug: TEST_ORG_SLUG,
    })) as { items: RunnerSummary[] };
    const target = allRunners.find((r) => r.nodeId === "dev-runner");
    expect(target, "dev-runner must exist in seeded dev-org").toBeTruthy();
    const targetId = target!.id;
    const originalMax = target!.maxConcurrentPods;

    try {
      // Sanity: runner is initially in the available list (capacity > 0).
      let avail = (await cc.runner.listAvailableRunners({
        orgSlug: TEST_ORG_SLUG,
      })) as { items: RunnerSummary[] };
      const presentBefore = avail.items.some((r) => r.id === targetId);
      expect(presentBefore, "dev-runner must start in ListAvailableRunners").toBe(true);

      // Cascade: drop capacity to 0. Service-layer query_eligible filters out
      // runners where ar.PodCount >= r.MaxConcurrentPods (backend/internal/
      // service/runner/query_eligible.go:26) so any current/0 ratio excludes it.
      await cc.runner.updateRunner({
        id: targetId,
        orgSlug: TEST_ORG_SLUG,
        maxConcurrentPods: 0,
      });

      avail = (await cc.runner.listAvailableRunners({
        orgSlug: TEST_ORG_SLUG,
      })) as { items: RunnerSummary[] };
      const presentAfter = avail.items.some((r) => r.id === targetId);
      expect(
        presentAfter,
        "dev-runner MUST be excluded from ListAvailableRunners after max=0",
      ).toBe(false);
    } finally {
      // Restore so dependent specs (pod-create / multi-agent-collab / etc.)
      // continue to see an available runner.
      await cc.runner.updateRunner({
        id: targetId,
        orgSlug: TEST_ORG_SLUG,
        maxConcurrentPods: originalMax,
      });

      // Verify restore took effect.
      const avail = (await cc.runner.listAvailableRunners({
        orgSlug: TEST_ORG_SLUG,
      })) as { items: RunnerSummary[] };
      expect(avail.items.some((r) => r.id === targetId)).toBe(true);
    }
  });

  test("setting is_enabled=false removes runner from available list immediately", async ({ api }) => {
    await api.login(TEST_USER.email, TEST_USER.password);
    const cc = await api.connect();

    const { items: allRunners } = (await cc.runner.listRunners({
      orgSlug: TEST_ORG_SLUG,
    })) as { items: RunnerSummary[] };
    const target = allRunners.find((r) => r.nodeId === "dev-runner");
    expect(target).toBeTruthy();
    const targetId = target!.id;

    try {
      await cc.runner.updateRunner({
        id: targetId,
        orgSlug: TEST_ORG_SLUG,
        isEnabled: false,
      });

      const avail = (await cc.runner.listAvailableRunners({
        orgSlug: TEST_ORG_SLUG,
      })) as { items: RunnerSummary[] };
      expect(
        avail.items.some((r) => r.id === targetId),
        "disabled runner MUST be excluded from ListAvailableRunners",
      ).toBe(false);
    } finally {
      await cc.runner.updateRunner({
        id: targetId,
        orgSlug: TEST_ORG_SLUG,
        isEnabled: true,
      });
    }
  });
});
