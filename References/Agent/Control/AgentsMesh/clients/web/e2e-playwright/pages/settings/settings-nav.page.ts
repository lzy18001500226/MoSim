import type { Locator, Page } from "@playwright/test";

/**
 * Page Object Model for the Settings page navigation.
 * URL pattern: /{orgSlug}/settings?scope={scope}&tab={tab}
 */

export type SettingsScope = "personal" | "organization";

export type OrgTab = "general" | "members" | "runners" | "api-keys" | "billing" | "usage" | "extensions";
export type PersonalTab = "general" | "git" | "agents" | "notifications";

export class SettingsNavPage {
  constructor(
    private page: Page,
    private orgSlug: string
  ) {}

  /** Navigate to a specific settings tab. */
  async goto(scope: SettingsScope, tab: string): Promise<void> {
    await this.page.goto(
      `/${this.orgSlug}/settings?scope=${scope}&tab=${tab}`
    );
    await this.page.waitForLoadState("load");
  }

  /** Get the scope toggle button. */
  getScopeButton(scope: SettingsScope): Locator {
    const label = scope === "personal"
      ? /personal|个人/i
      : /organization|组织/i;
    return this.page.getByRole("button", { name: label });
  }

  /** Switch to a different scope. */
  async switchScope(scope: SettingsScope): Promise<void> {
    await this.getScopeButton(scope).click();
  }
}
