import { test, expect } from "../../fixtures";
import { LoginPage } from "../../pages/login.page";
import { getApiBaseUrl } from "../../helpers/env";
import { resolve, join } from "node:path";
import { rmSync, mkdirSync, writeFileSync, existsSync } from "node:fs";

// F1 regression guard: ElectronAuthService.is_authenticated() must check
// expires_at, not just `!!_token`. Without this fix, an expired session
// from yesterday would route the renderer to dashboard → API 401 → refresh
// loop. We seed a session whose expires_at is 100s in the past, launch
// Electron, and assert bootstrap cleanup runs (token expired + refresh
// would also fail because the storage refresh_token is bogus).

const FRESH_USER_DATA = resolve(__dirname, "../../.auth/electron-userdata-expired-token");

test.use({
  skipAuthRestore: true,
  userDataDir: FRESH_USER_DATA,
});

test.beforeAll(() => {
  rmSync(FRESH_USER_DATA, { recursive: true, force: true });
});

test.describe("Auth · expired token redirects to login", () => {
  test("session with expires_at in the past does not land on dashboard", async ({ page, electronApp }) => {
    const baseUrl = getApiBaseUrl();
    const slug = baseUrl
      .replace(/\/+$/, "")
      .replace(/^(https?):\/\//, "$1_")
      .toLowerCase()
      .replace(/[^a-z0-9]/g, "_")
      .slice(0, 64);

    const dir = join(FRESH_USER_DATA, "agentsmesh", "agentsmesh-auth", slug);
    mkdirSync(dir, { recursive: true });
    writeFileSync(
      join(dir, "session.json"),
      JSON.stringify({
        access_token: "expired.access.token",
        refresh_token: "stale-refresh-that-server-no-longer-honors",
        expires_at: Math.floor(Date.now() / 1000) - 100,
        base_url: baseUrl,
        current_org_slug: null,
        schema_version: 1,
      }),
      "utf-8",
    );

    const login = new LoginPage(page);
    await page.waitForTimeout(2000);
    await login.expectOnLoginPage();

    const userData = await electronApp.evaluate(({ app }) => app.getPath("userData")) as string;
    expect(existsSync(join(userData, "agentsmesh", "agentsmesh-auth", slug, "session.json"))).toBe(false);
  });
});
