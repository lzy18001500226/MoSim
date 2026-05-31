import { test, expect } from "../../fixtures";
import { WorkspacePage } from "../../pages/workspace.page";
import { invokeIpc } from "../../helpers/ipc";

// Regression coverage for ElectronRepoState stub bug — the most user-visible
// symptom was an empty "Select Repository" dropdown inside the Create Pod
// dialog's Advanced Options section, even though backend had repositories
// imported. RepositorySelect renders `<option value={repo.id}>{repo.slug}</option>`
// for every entry in useRepositories(), which on desktop read from the
// no-op stub instead of the cache ElectronRepositoryService now owns.
//
// Locale is pinned to English by clients/desktop/e2e/fixtures/electron.fixture.ts
// — selectors target the English UI strings deliberately.
test.describe("Desktop · Create Pod dialog · repository dropdown", () => {
  test("dropdown lists backend repositories", async ({ page }) => {
    const raw = await invokeIpc<string>(page, "repositoryList");
    const { repositories = [] } = JSON.parse(raw) as {
      repositories?: { id: number; slug: string }[];
    };
    expect(repositories.length, "dev seed must include at least one repository").toBeGreaterThan(0);

    const workspace = new WorkspacePage(page);
    await workspace.goto();
    await page.waitForLoadState("domcontentloaded");
    await workspace.openCreatePodModal();

    // The modal mounts a role="dialog" with aria-labelledby="create-pod-title"
    // (see CreatePodModal.tsx). Wait on that — click → dialog render is async
    // and `getByRole("button", {name: /advanced options/i})` was timing out
    // because we asked for it before the dialog had attached.
    const dialog = page.getByRole("dialog", { name: /create new pod/i });
    await expect(dialog).toBeVisible({ timeout: 10_000 });

    // CreatePodForm only renders the AdvancedFormSection (and therefore the
    // repository select) once an Agent has been picked. Without this step
    // the Advanced Options trigger never mounts and the test below would
    // time out at 30s. Pick the first non-placeholder agent option to
    // satisfy that gate.
    const agentSelect = dialog.locator("#agent-select");
    await expect(agentSelect).toBeVisible({ timeout: 10_000 });
    const firstAgent = await agentSelect.locator("option").nth(1).getAttribute("value");
    expect(firstAgent, "no agents available — runner seed missing?").toBeTruthy();
    await agentSelect.selectOption(firstAgent!);

    // AdvancedOptions wraps RepositorySelect in a Radix Collapsible that
    // starts closed. Scope the selector to the dialog to avoid colliding
    // with any unrelated "Advanced Options" controls elsewhere on the page.
    await dialog.getByRole("button", { name: /^advanced options$/i }).click();

    const select = dialog.locator("#repository-select");
    await expect(select).toBeVisible({ timeout: 10_000 });

    // Placeholder <option value=""> + one <option> per backend repo. Stub
    // regression collapses this to just the placeholder.
    const expectedMin = 1 + repositories.length;
    await expect
      .poll(() => select.locator("option").count(), {
        timeout: 10_000,
        message: "dropdown should contain placeholder + at least one repo — ElectronRepoState stub regressed?",
      })
      .toBeGreaterThanOrEqual(expectedMin);

    // First backend repo's slug must surface as an <option>.
    const firstSlug = repositories[0].slug;
    await expect(
      select.locator("option", { hasText: firstSlug }),
      `expected option for repo slug "${firstSlug}"`,
    ).toHaveCount(1);
  });
});
