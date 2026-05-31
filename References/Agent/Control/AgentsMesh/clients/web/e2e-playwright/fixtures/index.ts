import { test as base } from "@playwright/test";
import { DbFixture } from "./db.fixture";
import { ApiFixture } from "./api.fixture";

/**
 * Extended test fixtures with database and API helpers.
 * Usage: import { test, expect } from '@fixtures/index';
 */

interface Fixtures {
  db: DbFixture;
  api: ApiFixture;
}

export const test = base.extend<Fixtures>({
  db: async ({}, use) => {
    const db = new DbFixture();
    await use(db);
  },

  api: async ({}, use) => {
    const api = new ApiFixture();
    await use(api);
  },
});

export { expect } from "@playwright/test";
