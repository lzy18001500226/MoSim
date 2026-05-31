import { test, expect } from "../../fixtures/index";
import { SettingsNavPage } from "../../pages/settings/settings-nav.page";
import { TEST_ORG_SLUG } from "../../helpers/env";

test.describe("Personal General Settings", () => {
  /**
   * TC-LANG-001: Language settings page elements
   */
  test("language settings page shows language options", async ({ page }) => {
    const nav = new SettingsNavPage(page, TEST_ORG_SLUG);
    await nav.goto("personal", "general");

    // Should show language section
    const body = await page.textContent("body");
    expect(body).toMatch(/language|语言/i);
  });

  /**
   * TC-LANG-002: Switch language to English
   */
  test("switch language to English", async ({ page }) => {
    const nav = new SettingsNavPage(page, TEST_ORG_SLUG);
    await nav.goto("personal", "general");

    // Find and click English option
    const englishOption = page.getByText("English").first();
    if (await englishOption.isVisible()) {
      await englishOption.click();
      await page.waitForTimeout(1000);

      // After switching, page should show English text
      const body = await page.textContent("body");
      expect(body).toMatch(/Language|Personal|Settings/i);
    }
  });

  /**
   * TC-LANG-003: Switch language to Chinese
   */
  test("switch language to Chinese", async ({ page }) => {
    const nav = new SettingsNavPage(page, TEST_ORG_SLUG);
    await nav.goto("personal", "general");

    const chineseOption = page.getByText("简体中文").first();
    if (await chineseOption.isVisible()) {
      await chineseOption.click();
      await page.waitForTimeout(1000);

      const body = await page.textContent("body");
      expect(body).toMatch(/语言|个人|组织/);
    }
  });
});
