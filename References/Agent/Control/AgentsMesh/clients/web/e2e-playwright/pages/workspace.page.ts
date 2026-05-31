import type { Locator, Page } from "@playwright/test";

/**
 * Page Object Model for the Workspace page.
 * URL: /{orgSlug}/workspace
 * Based on: web/src/app/(dashboard)/[org]/workspace/page.tsx
 */
export class WorkspacePage {
  readonly createPodButton: Locator;
  readonly emptyState: Locator;

  constructor(
    private page: Page,
    private orgSlug: string
  ) {
    this.createPodButton = page.getByRole("button", {
      name: /create.*pod|创建.*pod|新建.*pod/i,
    }).first();
    this.emptyState = page.locator(
      '[data-testid="empty-state"], .text-muted-foreground'
    ).first();
  }

  async goto(): Promise<void> {
    await this.page.goto(`/${this.orgSlug}/workspace`);
    await this.page.waitForLoadState("load");
  }

  /** Check if the terminal grid area exists. */
  async hasTerminalGrid(): Promise<boolean> {
    const grid = this.page.locator(
      '[data-testid="terminal-grid"], .xterm, [role="terminal"], .terminal-container'
    ).first();
    return grid.isVisible().catch(() => false);
  }

  /** Check if any pod tabs are visible. */
  async getPodTabCount(): Promise<number> {
    return this.page
      .locator('[data-testid="pod-tab"], button[role="tab"]')
      .count();
  }

  /** Check if empty state is visible. */
  async isEmptyState(): Promise<boolean> {
    const body = await this.page.textContent("body");
    return /no terminal|暂无|empty/i.test(body ?? "");
  }

  /** Open the create pod modal. */
  async openCreatePodModal(): Promise<void> {
    await this.createPodButton.click();
    await this.page
      .locator('[role="dialog"]')
      .first()
      .waitFor({ state: "visible" });
  }
}
