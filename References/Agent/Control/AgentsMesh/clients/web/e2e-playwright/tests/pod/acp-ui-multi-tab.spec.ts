import { test, expect } from "../../fixtures/index";
import { clearAuthRateLimit } from "../../helpers/redis";
import { terminateAllPods } from "../../helpers/pod-cleanup";
import {
  createMockAgentPod,
  workspaceUrlForPod,
} from "../../helpers/mock-agent";

// Multi-tab synchronization regression for the Phase D refactor
// (AcpPermissionModeSelector → useAcpSessionField). Two browser tabs
// (same context = same auth cookie + shared relay subscription topology)
// open the same pod. A mode change in tab A must propagate to tab B's
// selector via the configChanged broadcast — no manual refresh required.
//
// Before Phase D this would silently desync because each Selector kept
// its own useState; Phase D made the value server-derived through the
// wasm session cache, and Phase B added the broadcast that updates it.
// See acp-ui-echo.spec.ts header — same r6 fix applies.
test.describe("ACP UI: multi-tab Selector synchronization", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });
  test.afterEach(async () => { await terminateAllPods(); });

  test("mode change in tab A appears in tab B without refresh", async ({ context, api }) => {
    const pod = await createMockAgentPod(api, {
      mode: "acp",
      scenario: "config_change_plan",
      prompt: "multi-tab probe",
    });

    const tabA = await context.newPage();
    const tabB = await context.newPage();

    await Promise.all([
      tabA.goto(workspaceUrlForPod(pod.podKey)),
      tabB.goto(workspaceUrlForPod(pod.podKey)),
    ]);
    // Use "load" — see acp-ui-config-change.spec.ts header for the same r6
    // Connect-RPC streaming rationale.
    await Promise.all([
      tabA.waitForLoadState("load"),
      tabB.waitForLoadState("load"),
    ]);

    // Wait for both tabs to render the initial activity (so both have
    // an active relay subscription and a mounted Selector).
    await Promise.all([
      expect(tabA.getByText("Ready for mode switches", { exact: false })).toBeVisible({ timeout: 15_000 }),
      expect(tabB.getByText("Ready for mode switches", { exact: false })).toBeVisible({ timeout: 15_000 }),
    ]);

    // Drive the change from tab A. DropdownMenuTrigger carries the active
    // mode's i18n description as `title` (see AcpPermissionModeSelector).
    await tabA.locator('button[title*="Mode" i], button[title*="Approve" i], button[title*="Auto-approve" i]').first().click();
    await tabA.getByText("Default", { exact: true }).first().click();

    // Tab B must observe the new label through the broadcast → wasm
    // → useAcpSessionField path. Without Phase B's configChanged
    // event or Phase D's server-derived read, this would time out.
    await expect(
      tabB.locator('button:has-text("Default")').first()
    ).toBeVisible({ timeout: 10_000 });

    // Symmetry check: tab A also reflects the change locally (sanity
    // — it was the originator, the local optimistic update used to
    // come from useState and now comes from the same broadcast path).
    await expect(
      tabA.locator('button:has-text("Default")').first()
    ).toBeVisible({ timeout: 5_000 });

    await tabA.close();
    await tabB.close();
  });
});
