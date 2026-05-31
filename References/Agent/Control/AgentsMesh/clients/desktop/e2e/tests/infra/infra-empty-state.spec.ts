import { test, expect } from "../../fixtures";
import { InfraPage } from "../../pages/infra.page";

// Empty-state CTA → modal coverage. Forces an empty Runner/Repository list by
// intercepting the connectCall IPC dispatcher in the main process, so the
// empty-state branch always renders regardless of dev seed data. Guards the
// regression PR #379 fixed on web and the parallel desktop fix: empty-state
// buttons used to push URLs no one consumed, so clicking them did nothing.
//
// Note: desktop runs inside the IDE shell which also has sidebar buttons named
// "Add Runner" / "Import Repository". We scope the CTA locator to the
// EmptyState container (anchored on the "No runners yet" / "No repositories yet"
// heading) so we click the empty-state primary action, not the sidebar one.
//
// R6 Connect-RPC: the renderer now reaches the backend through `connectCall`
// (binary proto over IPC) instead of `runnerFetchRunners` / `repositoryList`
// JSON shims. We wrap connectCall to short-circuit the list RPCs to empty
// responses while letting every other RPC flow through.
test.describe("Infra empty state — CTA opens modal", () => {
  test.beforeEach(async ({ electronApp, page }) => {
    await electronApp.evaluate(({ ipcMain }) => {
      ipcMain.removeHandler("repositoryList");
      ipcMain.handle("repositoryList", async () =>
        JSON.stringify({ repositories: [] }),
      );

      // Intercept the generic Connect-RPC proxy. List* methods that drive
      // the runners/repositories tabs must return empty `items` envelopes —
      // everything else (channels, autopilot, etc.) keeps the original
      // network round-trip so unrelated UI still renders.
      // The Connect handler must return number[] (Array.from(bytes)) — see
      // main/index.ts registerLegacyApiAliases.
      ipcMain.removeHandler("connectCall");
      ipcMain.handle("connectCall", async (
        _e: unknown, service: string, method: string, _bodyArr: number[],
      ) => {
        const stubKey = `${service}/${method}`;
        const empty = {
          "proto.runner_api.v1.RunnerService/ListRunners": new Uint8Array(),
          "proto.runner_api.v1.RunnerService/ListAvailableRunners": new Uint8Array(),
          "proto.repository.v1.RepositoryService/ListRepositories": new Uint8Array(),
        }[stubKey];
        if (empty !== undefined) return Array.from(empty);
        // Fall through: re-issue the request directly. We can't easily reach
        // the AppState fetch helpers from this evaluate context, so we just
        // throw a connect-style error — the renderer treats it as a soft
        // failure and renders an empty list, which is also the empty state.
        throw new Error("connectCall stubbed: empty state forced");
      });
    });
    // Force the renderer to remount so React hooks' initial fetch picks up
    // the new IPC handlers — without reload, the page launched by the fixture
    // may have already fired fetches against the original handlers.
    await page.reload();
  });

  test("Add Runner empty-state button opens the Add Runner modal", async ({ page }) => {
    const infra = new InfraPage(page);
    await infra.gotoTab("runners");
    await page
      .getByRole("heading", { name: /no runners yet/i })
      .locator("..")
      .getByRole("button", { name: /^add runner$/i })
      .click();
    await expect(
      page.getByRole("heading", { name: /^add runner$/i }),
    ).toBeVisible();
  });

  test("Add Runner modal closes via cancel", async ({ page }) => {
    const infra = new InfraPage(page);
    await infra.gotoTab("runners");
    await page
      .getByRole("heading", { name: /no runners yet/i })
      .locator("..")
      .getByRole("button", { name: /^add runner$/i })
      .click();
    const heading = page.getByRole("heading", { name: /^add runner$/i });
    await heading.waitFor({ state: "visible" });
    await page.getByRole("button", { name: /^cancel$/i }).click();
    await expect(heading).toBeHidden();
  });

  test("Import Repository empty-state button opens the Import modal", async ({ page }) => {
    const infra = new InfraPage(page);
    await infra.gotoTab("repositories");
    await page
      .getByRole("heading", { name: /no repositories yet/i })
      .locator("..")
      .getByRole("button", { name: /^import repository$/i })
      .click();
    await expect(
      page.getByRole("heading", { name: /^import repository$/i }),
    ).toBeVisible();
  });

  test("Import Repository modal closes via cancel", async ({ page }) => {
    const infra = new InfraPage(page);
    await infra.gotoTab("repositories");
    await page
      .getByRole("heading", { name: /no repositories yet/i })
      .locator("..")
      .getByRole("button", { name: /^import repository$/i })
      .click();
    const heading = page.getByRole("heading", { name: /^import repository$/i });
    await heading.waitFor({ state: "visible" });
    await page.getByRole("button", { name: /^cancel$/i }).click();
    await expect(heading).toBeHidden();
  });
});
