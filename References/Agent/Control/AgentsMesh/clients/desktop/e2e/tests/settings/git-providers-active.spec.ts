import { test, expect } from "../../fixtures";
import { gotoHash } from "../../helpers/nav";

interface Provider { id: bigint | number; isActive: boolean }

/**
 * Desktop counterpart of clients/web/e2e-playwright/tests/settings/git-providers-active.spec.ts.
 *
 * The renderer reuses the web GitSettingsContent + GitProviderCard components,
 * and Desktop ships the same wasm-core artifact. So the regression must be
 * verified on the Electron build too: a freshly created provider should not
 * render the "已禁用 / Disabled" badge, and toggling is_active in the
 * EditProviderDialog must persist to the backend.
 */
test.describe("Desktop · Settings → Git Providers · is_active flow", () => {
  let providerId: number | undefined;

  test.afterEach(async ({ api }) => {
    if (providerId) {
      const cc = await api.connect();
      await cc.userRepositoryProvider.deleteRepositoryProvider({ id: BigInt(providerId) })
        .catch(() => undefined);
      providerId = undefined;
    }
  });

  test("created provider renders without disabled badge", async ({ api, page }) => {
    const cc = await api.connect();
    const created = await cc.userRepositoryProvider.createRepositoryProvider({
      providerType: "github",
      name: `Desktop E2E Active ${Date.now()}`,
      baseUrl: "https://api.github.com",
      botToken: "ghp_desktop_active",
    }) as Provider;
    providerId = Number(created.id);
    expect(created.isActive).toBe(true);

    await gotoHash(page, "/settings/git");
    // useGitSettings's listRepositoryProviders() is mount-scoped — if the
    // page was already on /settings/git the hook doesn't re-run. Trigger
    // a hard reload to force a fresh fetch so the just-created provider
    // appears (we already proved the create call succeeded above).
    await page.reload();
    const card = page.locator(`[data-testid="git-provider-card"][data-provider-id="${providerId}"]`);
    await expect(card).toBeVisible({ timeout: 20_000 });
    await expect(card).toHaveAttribute("data-is-active", "true");
    await expect(card.locator('[data-testid="git-provider-disabled-badge"]')).toHaveCount(0);
  });

  test("toggling is_active off via dialog persists across reload", async ({ api, page }) => {
    const cc = await api.connect();
    const created = await cc.userRepositoryProvider.createRepositoryProvider({
      providerType: "github",
      name: `Desktop E2E Toggle ${Date.now()}`,
      baseUrl: "https://api.github.com",
      botToken: "ghp_desktop_toggle",
    }) as Provider;
    providerId = Number(created.id);

    await gotoHash(page, "/settings/git");
    await page.reload();
    const card = page.locator(`[data-testid="git-provider-card"][data-provider-id="${providerId}"]`);
    await expect(card).toBeVisible({ timeout: 20_000 });

    await card.locator('[data-testid="git-provider-edit-button"]').click();
    const toggle = page.locator('[data-testid="edit-provider-active-toggle"]');
    const toggleLabel = page.locator('[data-testid="edit-provider-active-toggle-label"]');
    await expect(toggle).toBeChecked();
    await toggleLabel.click();
    await expect(toggle).not.toBeChecked();
    await page.locator('[data-testid="edit-provider-save-button"]').click();
    await expect(page.locator('[data-testid="edit-provider-dialog"]')).toBeHidden();

    await expect(card).toHaveAttribute("data-is-active", "false");
    await expect(card.locator('[data-testid="git-provider-disabled-badge"]')).toBeVisible();

    const verified = await cc.userRepositoryProvider.getRepositoryProvider({
      id: BigInt(providerId!),
    }) as Provider;
    expect(verified.isActive).toBe(false);

    await gotoHash(page, "/workspace");
    await gotoHash(page, "/settings/git");
    await expect(card.locator('[data-testid="git-provider-disabled-badge"]')).toBeVisible();
  });
});
