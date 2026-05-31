import { defineConfig, devices } from "@playwright/test";
import { getWebBaseUrl } from "./helpers/env";

const isCI = !!process.env.CI;

export default defineConfig({
  testDir: "./tests",
  fullyParallel: false,
  forbidOnly: isCI,
  retries: isCI ? 1 : 0,
  workers: 1,
  timeout: isCI ? 90_000 : 60_000,

  expect: {
    timeout: 10_000,
  },

  reporter: isCI
    ? [["list"], ["junit", { outputFile: "report.xml" }]]
    : [["html", { open: "never" }]],

  use: {
    baseURL: getWebBaseUrl(),
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    actionTimeout: 10_000,
    navigationTimeout: 30_000,
  },

  projects: [
    {
      name: "setup",
      testMatch: /global\.setup\.ts/,
    },
    {
      name: "admin-setup",
      testMatch: /admin\.setup\.ts/,
    },
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
        storageState: ".auth/user.json",
      },
      dependencies: ["setup"],
      testIgnore: [/.*admin.*\.spec\.ts/, /tests\/blockstore\/.*\.spec\.ts/],
    },
    {
      name: "admin",
      use: {
        ...devices["Desktop Chrome"],
        storageState: ".auth/admin.json",
      },
      dependencies: ["admin-setup"],
      testMatch: /.*admin.*\.spec\.ts/,
    },
    // Blockstore specs use their own fixture (fixtures/blockstore.fixture.ts)
    // that seeds JWT into localStorage at page boot — incompatible with the
    // suite-wide storageState login. Run them as a separate project so the
    // chromium project's `storageState` doesn't conflict with seedAuth.
    {
      name: "blockstore",
      use: { ...devices["Desktop Chrome"] },
      testMatch: /tests\/blockstore\/.*\.spec\.ts/,
    },
  ],
});
