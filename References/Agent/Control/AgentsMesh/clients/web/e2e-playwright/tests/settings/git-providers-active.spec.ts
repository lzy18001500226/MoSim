// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";

/**
 * Regression coverage for the wasm-core field-stripping bug
 * (Rust types missing is_active / has_identity / has_bot_token / has_client_id):
 * every provider used to render the "已禁用 / Disabled" badge regardless
 * of DB state, and the EditProviderDialog toggle silently no-op'd.
 */
test.describe("Settings → Git Providers · is_active flow", () => {
  let providerId: number | undefined;

  test.afterEach(async ({ api }) => {
    if (providerId) {
      const cc = await api.connect();
      await cc.userRepositoryProvider.deleteRepositoryProvider({ id: providerId }).catch(() => null);
      providerId = undefined;
    }
  });

  test("freshly created provider does NOT show disabled badge", async ({ api, page }) => {
    const cc = await api.connect();
    const created = await cc.userRepositoryProvider.createRepositoryProvider({
      providerType: "github",
      name: `E2E UI Active ${Date.now()}`,
      baseUrl: "https://api.github.com",
      botToken: "ghp_e2e_ui_active",
    }) as { id: number; isActive: boolean };
    providerId = created.id;
    expect(created.isActive).toBe(true);

    await page.goto(`/${TEST_ORG_SLUG}/settings?scope=personal&tab=git`);
    await page.waitForLoadState("load");

    const card = page.locator(`[data-testid="git-provider-card"][data-provider-id="${providerId}"]`);
    await expect(card).toBeVisible({ timeout: 10_000 });
    await expect(card).toHaveAttribute("data-is-active", "true");

    const disabledBadge = card.locator('[data-testid="git-provider-disabled-badge"]');
    await expect(disabledBadge).toHaveCount(0);
  });

  test("toggling is_active off in EditDialog persists and shows disabled badge", async ({ api, page }) => {
    const cc = await api.connect();
    const created = await cc.userRepositoryProvider.createRepositoryProvider({
      providerType: "github",
      name: `E2E UI Toggle ${Date.now()}`,
      baseUrl: "https://api.github.com",
      botToken: "ghp_e2e_ui_toggle",
    }) as { id: number };
    providerId = created.id;

    await page.goto(`/${TEST_ORG_SLUG}/settings?scope=personal&tab=git`);
    await page.waitForLoadState("load");

    const card = page.locator(`[data-testid="git-provider-card"][data-provider-id="${providerId}"]`);
    await expect(card).toBeVisible();
    await expect(card.locator('[data-testid="git-provider-disabled-badge"]')).toHaveCount(0);

    await card.locator('[data-testid="git-provider-edit-button"]').click();
    const dialog = page.locator('[data-testid="edit-provider-dialog"]');
    await expect(dialog).toBeVisible();

    const toggle = dialog.locator('[data-testid="edit-provider-active-toggle"]');
    const toggleLabel = dialog.locator('[data-testid="edit-provider-active-toggle-label"]');
    await expect(toggle).toBeChecked();
    await toggleLabel.click();
    await expect(toggle).not.toBeChecked();

    await dialog.locator('[data-testid="edit-provider-save-button"]').click();
    await expect(dialog).toBeHidden();

    await expect(card).toHaveAttribute("data-is-active", "false");
    await expect(card.locator('[data-testid="git-provider-disabled-badge"]')).toBeVisible();

    const verified = await cc.userRepositoryProvider.getRepositoryProvider({ id: providerId! }) as { isActive: boolean };
    expect(verified.isActive).toBe(false);
  });

  test("re-enabling a disabled provider clears the disabled badge", async ({ api, page }) => {
    const cc = await api.connect();
    const created = await cc.userRepositoryProvider.createRepositoryProvider({
      providerType: "github",
      name: `E2E UI ReEnable ${Date.now()}`,
      baseUrl: "https://api.github.com",
      botToken: "ghp_e2e_reenable",
    }) as { id: number };
    providerId = created.id;
    await cc.userRepositoryProvider.updateRepositoryProvider({ id: providerId!, isActive: false });

    await page.goto(`/${TEST_ORG_SLUG}/settings?scope=personal&tab=git`);
    await page.waitForLoadState("load");

    const card = page.locator(`[data-testid="git-provider-card"][data-provider-id="${providerId}"]`);
    await expect(card.locator('[data-testid="git-provider-disabled-badge"]')).toBeVisible();

    await card.locator('[data-testid="git-provider-edit-button"]').click();
    const toggle = page.locator('[data-testid="edit-provider-active-toggle"]');
    const toggleLabel = page.locator('[data-testid="edit-provider-active-toggle-label"]');
    await expect(toggle).not.toBeChecked();
    await toggleLabel.click();
    await expect(toggle).toBeChecked();
    await page.locator('[data-testid="edit-provider-save-button"]').click();
    await expect(page.locator('[data-testid="edit-provider-dialog"]')).toBeHidden();

    await expect(card).toHaveAttribute("data-is-active", "true");
    await expect(card.locator('[data-testid="git-provider-disabled-badge"]')).toHaveCount(0);

    const verified = await cc.userRepositoryProvider.getRepositoryProvider({ id: providerId! }) as { isActive: boolean };
    expect(verified.isActive).toBe(true);
  });
});
