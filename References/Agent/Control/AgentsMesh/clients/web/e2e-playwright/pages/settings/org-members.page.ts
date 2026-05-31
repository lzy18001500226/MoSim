import type { Locator, Page } from "@playwright/test";

/**
 * POM for Organization Members Settings.
 * URL: /{orgSlug}/settings?scope=organization&tab=members
 * Based on: web/src/components/settings/organization/MembersSettings.tsx
 */
export class OrgMembersPage {
  readonly inviteButton: Locator;
  readonly inviteEmailInput: Locator;
  readonly inviteRoleSelect: Locator;
  readonly sendInviteButton: Locator;

  constructor(private page: Page, private orgSlug: string) {
    this.inviteButton = page.getByRole("button", { name: /invite|邀请/i });
    this.inviteEmailInput = page.locator("#invite-email");
    this.inviteRoleSelect = page.locator("#invite-role");
    this.sendInviteButton = page.getByRole("button", {
      name: /send invite|发送邀请/i,
    });
  }

  async goto(): Promise<void> {
    await this.page.goto(
      `/${this.orgSlug}/settings?scope=organization&tab=members`
    );
    await this.page.waitForLoadState("load");
  }

  async openInviteDialog(): Promise<void> {
    await this.inviteButton.click();
    await this.inviteEmailInput.waitFor({ state: "visible" });
  }

  async inviteMember(email: string, role?: string): Promise<void> {
    await this.openInviteDialog();
    await this.inviteEmailInput.fill(email);
    if (role && await this.inviteRoleSelect.isVisible()) {
      await this.inviteRoleSelect.selectOption(role);
    }
    await this.sendInviteButton.click();
  }

  /** Get a member row by email text. */
  getMemberRow(email: string): Locator {
    return this.page.locator("tr, [role='row']").filter({ hasText: email });
  }
}
