import type { Locator, Page } from "@playwright/test";

/**
 * POM for Organization General Settings.
 * URL: /{orgSlug}/settings?scope=organization&tab=general
 * Based on: web/src/components/settings/organization/GeneralSettings.tsx
 */
export class OrgGeneralPage {
  readonly nameInput: Locator;
  readonly slugInput: Locator;
  readonly saveButton: Locator;
  readonly deleteButton: Locator;

  constructor(private page: Page, private orgSlug: string) {
    this.nameInput = page.locator("#org-name");
    this.slugInput = page.locator("#org-slug");
    this.saveButton = page.getByRole("button", { name: /save|保存/i });
    this.deleteButton = page.getByRole("button", { name: /delete|删除组织/i });
  }

  async goto(): Promise<void> {
    await this.page.goto(
      `/${this.orgSlug}/settings?scope=organization&tab=general`
    );
    await this.page.waitForLoadState("load");
  }

  async updateName(newName: string): Promise<void> {
    await this.nameInput.clear();
    await this.nameInput.fill(newName);
    await this.saveButton.click();
  }
}
