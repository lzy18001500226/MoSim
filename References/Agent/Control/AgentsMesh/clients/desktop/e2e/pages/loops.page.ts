import type { Locator, Page } from "@playwright/test";
import { TEST_ORG_SLUG } from "../helpers/env";
import { gotoHash, expectHashMatches } from "../helpers/nav";

/**
 * Page Object for Loops (scheduled agent work).
 * Route: #/:org/loops, #/:org/loops/:slug
 */
export class LoopsPage {
  readonly newLoopButton: Locator;
  readonly loopList: Locator;
  readonly runHistoryTable: Locator;
  readonly promptEditor: Locator;
  readonly scheduleInput: Locator;

  constructor(private page: Page) {
    this.newLoopButton = page.getByRole("button", { name: /new loop|new/i }).first();
    this.loopList = page.locator('[data-section="loop-list"]');
    this.runHistoryTable = page.locator('[data-section="run-history"], table').first();
    this.promptEditor = page.locator('textarea[name="prompt"], [data-editor="prompt"]').first();
    this.scheduleInput = page.locator('input[name="schedule"]');
  }

  async goto(): Promise<void> {
    await gotoHash(this.page, `/${TEST_ORG_SLUG}/loops`);
  }

  async expectOnPage(): Promise<void> {
    await expectHashMatches(this.page, /\/loops/);
  }

  async openLoop(slug: string): Promise<void> {
    await gotoHash(this.page, `/${TEST_ORG_SLUG}/loops/${slug}`);
  }
}
