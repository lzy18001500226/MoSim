// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { OrgGeneralPage } from "../../pages/settings/org-general.page";
import { TEST_ORG_SLUG } from "../../helpers/env";

test.describe("Organization General Settings", () => {
  let orgPage: OrgGeneralPage;

  test.beforeEach(async ({ page }) => {
    orgPage = new OrgGeneralPage(page, TEST_ORG_SLUG);
    await orgPage.goto();
  });

  /**
   * TC-ORGSET-001: Get org details (API)
   */
  test("get org details via API", async ({ api }) => {
    const cc = await api.connect();
    const org = await cc.org.getOrg({ orgSlug: TEST_ORG_SLUG }) as { slug: string; name: string };
    expect(org.slug).toBe(TEST_ORG_SLUG);
    expect(org.name).toBeTruthy();
  });

  /**
   * TC-ORGSET-002: Settings page elements
   */
  test("settings page displays required elements", async () => {
    await expect(orgPage.nameInput).toBeVisible();
    await expect(orgPage.slugInput).toBeVisible();
    await expect(orgPage.saveButton).toBeVisible();
  });

  /**
   * TC-ORGSET-004: Slug is disabled
   */
  test("org slug field is disabled", async () => {
    await expect(orgPage.slugInput).toBeDisabled();
    const slugValue = await orgPage.slugInput.inputValue();
    expect(slugValue).toBe(TEST_ORG_SLUG);
  });

  /**
   * TC-ORGSET-003: Update org name
   */
  test("update org name and verify persistence", async ({ page, db }) => {
    // Save original name
    const originalName = await orgPage.nameInput.inputValue();

    // Update
    await orgPage.updateName("E2E Test Organization Name");
    await page.waitForTimeout(1000);

    // Refresh and verify
    await page.reload();
    await orgPage.nameInput.waitFor({ state: "visible" });
    const updatedValue = await orgPage.nameInput.inputValue();
    expect(updatedValue).toBe("E2E Test Organization Name");

    // Restore original
    db.cleanup(
      `UPDATE organizations SET name = '${originalName}' WHERE slug = '${TEST_ORG_SLUG}'`
    );
  });
});
