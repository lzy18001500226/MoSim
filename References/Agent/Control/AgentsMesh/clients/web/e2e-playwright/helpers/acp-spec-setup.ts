import type { Page } from "@playwright/test";
import type { ApiFixture } from "../fixtures/api.fixture";
import {
  collectConsoleErrors,
  collectPageErrors,
  assertNoWasmRecursiveBorrow,
} from "./console-errors";
import {
  createMockAgentPod,
  workspaceUrlForPod,
  type CreateMockPodOptions,
  type MockAgentPod,
} from "./mock-agent";

// SetupAcpScenarioResult bundles the per-spec context so each test can
// reach for exactly what it needs without a fixture explosion.
export interface SetupAcpScenarioResult {
  pod: MockAgentPod;
  consoleErrors: () => string[];
  pageErrors: () => string[];
  /** Asserts the wasm-bindgen recursive-borrow guard is intact. */
  assertWasmHealthy: () => void;
}

// setupAcpScenarioPage encapsulates the 4-step prologue every ACP UI spec
// repeats: spawn mock pod → wire console/error collectors → navigate to the
// workspace → wait for network idle. Throws when no runner is online —
// the e2e suite contract is "dev env has at least one online runner", so
// returning null here would silently mask a missing prerequisite.
//
// The returned object holds the live error collectors as functions; calling
// them returns the current snapshot, which lets specs assert the recursive-
// borrow guard at any point without recomputing the wiring.
export async function setupAcpScenarioPage(
  page: Page,
  api: ApiFixture,
  opts: CreateMockPodOptions,
): Promise<SetupAcpScenarioResult> {
  const consoleErrors = collectConsoleErrors(page);
  const pageErrors = collectPageErrors(page);

  const pod = await createMockAgentPod(api, opts);
  if (!pod) {
    throw new Error("setupAcpScenarioPage: createMockAgentPod returned null — dev env must have an online runner");
  }

  await page.goto(workspaceUrlForPod(pod.podKey));
  // Connect-RPC EventsService streams keep the page in flight indefinitely
  // on r6, so "networkidle" (the original pre-r6 strategy) times out. "load"
  // matches what pod-create-ui.spec.ts and pod-lifecycle.spec.ts use against
  // the same workspace route.
  await page.waitForLoadState("load");

  return {
    pod,
    consoleErrors: () => consoleErrors,
    pageErrors: () => pageErrors,
    assertWasmHealthy: () => {
      assertNoWasmRecursiveBorrow(consoleErrors);
      assertNoWasmRecursiveBorrow(pageErrors);
    },
  };
}
