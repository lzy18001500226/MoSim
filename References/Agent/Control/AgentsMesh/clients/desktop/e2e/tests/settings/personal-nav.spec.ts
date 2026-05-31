import { test } from "../../fixtures";
import { SettingsPersonalPage } from "../../pages/settings-personal.page";

test("Settings (Personal) · general route opens", async ({ page }) => {
  const settings = new SettingsPersonalPage(page);
  await settings.goto();
  await settings.expectOnPage();
});
