// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";
import { collectConsoleErrors, assertNoWasmErrors } from "../../helpers/console-errors";

test.describe("Channel Operations", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("channels: select channel and view messages", async ({ page, api }) => {
    const cc = await api.connect();
    // Ensure there's at least one channel — create a deterministic one rather
    // than skipping when the org slate is bare.
    let { items } = await cc.channel.listChannels({ orgSlug: TEST_ORG_SLUG }) as {
      items: { id?: bigint | number }[];
    };
    let createdId: bigint | number | undefined;
    if (!items || items.length === 0) {
      const ch = await cc.channel.createChannel({
        orgSlug: TEST_ORG_SLUG,
        name: "E2E ChOps Seed " + Date.now(),
      }) as { id: bigint | number };
      createdId = ch.id;
      items = [{ id: ch.id }];
    }
    expect(items.length).toBeGreaterThan(0);

    const errors = collectConsoleErrors(page);
    await page.goto(`/${TEST_ORG_SLUG}/channels`);
    await page.waitForLoadState("load");

    const firstChannel = page.locator(`[data-channel-id], a[href*="channels"]`).first();
    if (await firstChannel.isVisible({ timeout: 3000 }).catch(() => false)) {
      await firstChannel.click();
      await page.waitForTimeout(1000);
    }
    assertNoWasmErrors(errors);

    if (createdId !== undefined) {
      await cc.channel.archiveChannel({ orgSlug: TEST_ORG_SLUG, id: createdId });
    }
  });

  test("channels: create channel dialog", async ({ page }) => {
    const errors = collectConsoleErrors(page);
    await page.goto(`/${TEST_ORG_SLUG}/channels`);
    await page.waitForLoadState("load");

    const createBtn = page.getByRole("button", { name: /新建|Create|New/i }).first();
    if (await createBtn.isVisible({ timeout: 3000 }).catch(() => false)) {
      await createBtn.click();
      await page.waitForTimeout(500);
    }
    assertNoWasmErrors(errors);
  });
});
