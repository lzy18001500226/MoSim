// Cascade test (P0): deleting a runner that is referenced by a Loop must
// be rejected (ErrRunnerHasLoopRefs). This is the only `cannot delete:
// resource has references` invariant the runner service enforces today
// (backend/internal/service/runner/registration.go:12) — without it, a
// loop would silently point at runner_id of a row that no longer exists,
// and the next TriggerLoop would fail in confusing ways at dispatch time.
//
// Scope of this spec:
//   * Asserts the existing protection works (regression guard).
//   * Documents the asymmetry: Pod refs are NOT checked (CountLoopsByRunner
//     only), so deleting a runner with active pods orphans them. The
//     orphan-pod path is a separate audit finding tracked in the cascade
//     punch list — testing it would require boot-time pod state assumptions
//     that are too coupled to the dev seed; instead this spec locks in
//     the loop-ref guard so any future refactor of DeleteRunner has to
//     keep at least the loop check intact.
import { test, expect } from "../../fixtures/index";
import { TEST_USER, TEST_ORG_SLUG } from "../../helpers/env";

interface RunnerSummary {
  id: bigint;
  nodeId: string;
}

test.describe("Cascade: runner delete blocked by loop reference", () => {
  test("DeleteRunner returns FailedPrecondition when a Loop references it", async ({ api, db }) => {
    await api.login(TEST_USER.email, TEST_USER.password);
    const cc = await api.connect();

    const { items: allRunners } = (await cc.runner.listRunners({
      orgSlug: TEST_ORG_SLUG,
    })) as { items: RunnerSummary[] };
    const target = allRunners.find((r) => r.nodeId === "dev-runner");
    expect(target).toBeTruthy();
    const targetId = target!.id;

    // Create a loop that pins this runner.
    const loopSlug = `cascade-loop-${Date.now()}`;
    let loopId: bigint | undefined;
    try {
      const createResp = (await cc.loop.createLoop({
        orgSlug: TEST_ORG_SLUG,
        name: "Cascade delete-runner guard",
        slug: loopSlug,
        agentSlug: "e2e-echo",
        permissionMode: "bypassPermissions",
        promptTemplate: "noop",
        promptVariablesJson: "{}",
        configOverridesJson: "{}",
        autopilotConfigJson: "{}",
        branchName: "",
        executionMode: "direct",
        cronExpression: "",
        callbackUrl: "",
        sandboxStrategy: "fresh",
        concurrencyPolicy: "skip",
        runnerId: targetId,
      })) as { id: bigint };
      loopId = createResp.id;
      expect(loopId).toBeTruthy();

      // Cascade assertion: delete must fail because a loop references it.
      let deleteBlocked = false;
      let deleteErr: unknown = null;
      try {
        await cc.runner.deleteRunner({ id: targetId, orgSlug: TEST_ORG_SLUG });
      } catch (err) {
        deleteErr = err;
        const code = (err as { code?: string }).code ?? "";
        const status = (err as { status?: number }).status;
        const msg = String((err as { message?: string }).message ?? "");
        // Backend maps ErrRunnerHasLoopRefs to FailedPrecondition (Connect)
        // / 412 (HTTP). We accept any 4xx with the "loop" hint to stay
        // robust against future error-code refinement.
        if (
          code === "failed_precondition" ||
          status === 412 ||
          status === 409 ||
          msg.toLowerCase().includes("loop")
        ) {
          deleteBlocked = true;
        }
      }
      expect(
        deleteBlocked,
        `DeleteRunner must be blocked while a Loop references it; got: ${JSON.stringify(deleteErr)}`,
      ).toBe(true);

      // Sanity: runner is still present after the blocked delete.
      const afterAttempt = (await cc.runner.listRunners({
        orgSlug: TEST_ORG_SLUG,
      })) as { items: RunnerSummary[] };
      expect(afterAttempt.items.some((r) => r.id === targetId)).toBe(true);
    } finally {
      // Tear down the loop. If the spec failed mid-way, this still keeps
      // the seed clean for subsequent runs.
      if (loopId !== undefined) {
        try {
          await cc.loop.deleteLoop({ orgSlug: TEST_ORG_SLUG, loopSlug });
        } catch {
          // Fall back to DB cleanup so a busted teardown doesn't leak rows.
          db.cleanup(`DELETE FROM loops WHERE slug = '${loopSlug}'`);
        }
      }
    }
  });
});
