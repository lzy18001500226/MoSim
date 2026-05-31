import { test, expect } from "../../fixtures";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { gotoHash } from "../../helpers/nav";

/**
 * Regression coverage for the `useLocalRunnerOnboarding` hook + ThisMacSection
 * UI on the desktop. Stubs in `clients/desktop/src/main/local_runner_stubs.ts`
 * intercept every `localRunner*` IPC when `NODE_ENV=test`, so this spec runs
 * end-to-end without needing a real `agentsmesh-runner` binary on PATH.
 *
 * Bugs this guards against:
 *
 *  • Hook refresh guard pinned phase in installing forever after onRegister
 *    completed every step successfully — the user saw "Working… / Starting
 *    service…" indefinitely while the runner was already up. The fix moved
 *    the `if (phase.kind === "installing") return` guard from inside refresh
 *    to the setInterval handler. Coverage: card transitions to the syncing
 *    row at the end of the click flow.
 *
 *  • Backend `POST /runners/grpc/tokens` used to omit the `id` field, which
 *    the Rust client deserialises as a required `i64`. Step 2 (token mint)
 *    threw `missing field 'id'`. Coverage: the syncing row appears, which
 *    is only reachable if create_token round-trips successfully.
 *
 * Selector strategy: data-testid attributes on the trigger button and the
 * syncing row. Role+text selectors used to be flaky against React 18 batched
 * renders + Button's `transition-colors` CSS — Playwright's stability check
 * sometimes flagged the click target as "not stable" or "detached" purely
 * from rerender churn around the click moment. testid + `force: true`
 * sidesteps that false-positive without weakening the assertion.
 */
test.describe("Desktop ThisMacSection onboarding", () => {
  test("registering this Mac transitions through every step to syncing", async ({ page }) => {
    await gotoHash(page, `/${TEST_ORG_SLUG}/infra?tab=runners`);

    // Wait for the hook's initial refresh() to drain so the OnboardingBlock
    // is mounted (phase: loading → idle.not_installed). Without this we race
    // the hook's first useEffect tick and the button selector resolves
    // against a still-loading "Checking…" row.
    const button = page.getByTestId("this-mac-register-btn");
    await expect(button).toBeVisible({ timeout: 15_000 });
    await expect(button).toBeEnabled();

    // force:true bypasses Playwright's actionability checks (visible/enabled/
    // stable/receives-events). The actionability we care about is the first
    // three — stability is what flakes here, and the click handler doesn't
    // need to bubble through any other element so receives-events is a
    // non-issue. The stub IPC path is synchronous from React's POV.
    await button.click({ force: true });

    // After all 5 onboarding steps complete the stub flips service_status to
    // "running" and useLocalRunnerOnboarding's refresh() sets phase to
    // idle.running. Since the IPC stubs don't fake a backend heartbeat,
    // matchingRunner stays null → ThisMacSection renders the syncing row,
    // which is the high-fidelity proof that the 5-step state machine drained
    // without getting pinned in "Working…" (the regression we care about).
    const syncing = page.getByTestId("this-mac-syncing");
    await expect(syncing).toBeVisible({ timeout: 15_000 });

    // The trigger must be gone so re-clicking it can't fire onRegister twice.
    await expect(button).toHaveCount(0);
  });
});
