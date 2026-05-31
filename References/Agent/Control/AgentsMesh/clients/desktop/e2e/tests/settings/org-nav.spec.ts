import { test } from "../../fixtures";
import { SettingsOrgPage } from "../../pages/settings-org.page";

test("Settings (Org) · route opens", async ({ page }) => {
  const settings = new SettingsOrgPage(page);
  await settings.goto();
  await settings.expectOnPage();
});
