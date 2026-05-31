import type { Locator, Page } from "@playwright/test";
import { TEST_ORG_SLUG } from "../helpers/env";
import { gotoHash, expectHashMatches } from "../helpers/nav";

/**
 * Page Object for Workspace (Pod list + terminal panes).
 * Route: #/:org/workspace
 */
export class WorkspacePage {
  readonly createPodButton: Locator;
  readonly podList: Locator;
  readonly terminalPane: Locator;
  readonly emptyStateCta: Locator;

  constructor(private page: Page) {
    // i18n labels (clients/web/src/messages/{en,zh}/app.json):
    //   workspace.newPod         → "New Pod"  / "新建 Pod"  (sidebar Create button)
    //   workspace.createNewPod   → "New Pod"  / "新建 Pod"  (empty-state CTA)
    // Both English variants land on "New Pod" — the regex MUST cover that
    // bare form. The earlier `create new pod` branch only matched a
    // different surface that no longer exists.
    this.createPodButton = page.getByRole("button", { name: /^\s*\+?\s*(new pod|create (?:new )?pod|新建 ?Pod|新建)\s*$/i }).first();
    this.podList = page.locator('[class*="pod-list"], [data-slot="pod-list"]').first();
    this.terminalPane = page.locator(".xterm, .xterm-viewport").first();
    this.emptyStateCta = page.getByRole("button", { name: /^\s*\+?\s*(new pod|创建新 ?Pod|create (?:new )?pod)\s*$/i });
  }

  async goto(): Promise<void> {
    await gotoHash(this.page, `/${TEST_ORG_SLUG}/workspace`);
  }

  async expectOnPage(): Promise<void> {
    await expectHashMatches(this.page, /\/workspace/);
  }

  async openCreatePodModal(): Promise<void> {
    // Wasm cold-start path on macOS Electron is ~30-50s for the runtime
    // crate + service registry init. domcontentloaded fires far earlier
    // (~5-8s) — the renderer's `useState` selectors haven't yet seen the
    // pod-list snapshot when the spec's `waitForLoadState("domcontentloaded")`
    // returns, so the createPod button stays unmounted. Wait explicitly
    // for the button to attach + become visible before clicking.
    await this.createPodButton.waitFor({ state: "visible", timeout: 60_000 });
    await this.createPodButton.click();
  }

  async selectPodByKey(podKey: string): Promise<void> {
    await this.page.getByText(podKey, { exact: false }).first().click();
  }

  async expectTerminalVisible(): Promise<void> {
    await this.terminalPane.waitFor({ state: "visible", timeout: 15_000 });
  }
}
