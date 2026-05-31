import { test as base, _electron as electron, type ElectronApplication, type Page } from "@playwright/test";
import {
  getApiBaseUrl,
  getElectronMainPath,
  getAuthFile,
  getUserDataDir,
  isCi,
} from "../helpers/env";
import { invokeIpc } from "../helpers/ipc";
import { loadStorageFile, restoreStorage } from "../helpers/storage-state";

// Worker-scoped Electron fixture for IPC smoke tests.
//
// The default `electron.fixture.ts` is test-scoped: each test launches and
// tears down its own Electron app. That's correct for tests that need fresh
// state, but the auto-generated IPC smoke specs (clients/desktop/e2e/tests/
// ipc/_generated/*) just ping each handler — they never mutate state and
// don't depend on isolation. With ~280 of them in a single worker the
// repeated launch/close pattern saturates the macOS process/fd budget and
// triggers `electronApplication.firstWindow` timeouts after ~250 tests
// (the original loop_svc_delete_loop flaky).
//
// This fixture keeps one Electron + one Page alive for the entire worker,
// shared across every test in the spec — each individual test still owns
// its own report / retry / timeout, only the Electron process is shared.
//
// SAFE ONLY for smoke specs that issue read/no-op IPC calls. State-mutating
// tests must keep using the default test-scoped fixture in electron.fixture.ts.

export interface SharedElectronFixtures {
  sharedElectronApp: ElectronApplication;
  sharedPage: Page;
}

export const test = base.extend<Record<string, never>, SharedElectronFixtures>({
  sharedElectronApp: [
    async ({}, use) => {
      const ciArgs = isCi() && process.platform === "linux"
        ? ["--no-sandbox", "--disable-dev-shm-usage"]
        : [];
      const app = await electron.launch({
        args: [getElectronMainPath(), `--user-data-dir=${getUserDataDir()}`, ...ciArgs],
        env: {
          ...process.env,
          AGENTSMESH_API_URL: getApiBaseUrl(),
          NODE_ENV: "test",
          ELECTRON_DISABLE_SECURITY_WARNINGS: "true",
        },
        timeout: isCi() ? 120_000 : 30_000,
      });
      await use(app);
      await app.close().catch(() => undefined);
    },
    { scope: "worker" },
  ],

  sharedPage: [
    async ({ sharedElectronApp }, use) => {
      const page = await sharedElectronApp.firstWindow({ timeout: isCi() ? 90_000 : 30_000 });
      await page.waitForLoadState("domcontentloaded");

      const snap = loadStorageFile(getAuthFile());
      if (snap) {
        await restoreStorage(page, snap);
        await page.reload().catch(() => undefined);
        await page.waitForLoadState("domcontentloaded");
        await invokeIpc(page, "authBootstrap");
      }
      await use(page);
    },
    { scope: "worker" },
  ],
});

export { expect } from "@playwright/test";
