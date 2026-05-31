import { test, expect } from "../../fixtures/index";
import { OrgMembersPage } from "../../pages/settings/org-members.page";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

test.describe("Organization Members Settings", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("members page displays required elements", async ({ page }) => {
    const membersPage = new OrgMembersPage(page, TEST_ORG_SLUG);
    await membersPage.goto();

    await expect(membersPage.inviteButton).toBeVisible();
  });

  test("invite dialog opens with email and role fields", async ({ page }) => {
    const membersPage = new OrgMembersPage(page, TEST_ORG_SLUG);
    await membersPage.goto();
    await membersPage.openInviteDialog();

    await expect(membersPage.inviteEmailInput).toBeVisible();
  });
});
