import type { Locator, Page } from "@playwright/test";
import { TEST_ORG_SLUG } from "../helpers/env";
import { gotoHash, expectHashMatches } from "../helpers/nav";

/**
 * Page Object for Mesh topology view.
 * Route: #/:org/mesh
 */
export class MeshPage {
  readonly topologyCanvas: Locator;
  readonly runnerNodes: Locator;
  readonly podNodes: Locator;
  readonly filterControls: Locator;

  constructor(private page: Page) {
    this.topologyCanvas = page.locator('.react-flow, [data-section="mesh-topology"]').first();
    this.runnerNodes = page.locator('[data-node-type="runner"]');
    this.podNodes = page.locator('[data-node-type="pod"]');
    this.filterControls = page.locator('[data-section="mesh-filters"]');
  }

  async goto(): Promise<void> {
    await gotoHash(this.page, `/${TEST_ORG_SLUG}/mesh`);
  }

  async expectOnPage(): Promise<void> {
    await expectHashMatches(this.page, /\/mesh/);
  }
}
