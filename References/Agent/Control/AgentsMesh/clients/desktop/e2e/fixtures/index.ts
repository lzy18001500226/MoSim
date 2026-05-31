import { mergeTests, test as base } from "@playwright/test";
import { test as electronTest } from "./electron.fixture";
import { ApiFixture } from "../../../web/e2e-playwright/fixtures/api.fixture";
import { DbFixture } from "../../../web/e2e-playwright/fixtures/db.fixture";

interface SharedFixtures {
  api: ApiFixture;
  db: DbFixture;
}

/**
 * Reconstruct the API + DB fixtures using desktop's own @playwright/test
 * to avoid Playwright's duplicate-package guard triggered by importing
 * e2e-playwright/fixtures/index.ts (which carries its own @playwright/test binding).
 * The fixture CLASSES (ApiFixture, DbFixture) are framework-agnostic and re-usable.
 */
const sharedTest = base.extend<SharedFixtures>({
  api: async ({}, use) => {
    const api = new ApiFixture();
    await use(api);
  },
  db: async ({}, use) => {
    const db = new DbFixture();
    await use(db);
  },
});

/**
 * Unified desktop e2e test fixture:
 * - Electron lifecycle (`electronApp`, `page`, `authFile`, `skipAuthRestore`, `userDataDir`)
 * - Direct-API helper (`api`) for fast setup/teardown bypassing UI
 * - Direct DB helper (`db`) via docker exec psql
 */
export const test = mergeTests(electronTest, sharedTest);
export { expect } from "@playwright/test";
