import { test, expect } from "../../fixtures/index";
import { TEST_USER, TEST_ORG_SLUG, getWebBaseUrl, getApiBaseUrl } from "../../helpers/env";

/**
 * Regression guard for the light-auth rollout:
 *   /login, /register, /forgot-password, /reset-password, /verify-email,
 *   /onboarding, /invite/*, /runners/authorize and both OAuth callbacks
 *   must NEVER load the 40MB agentsmesh-wasm bundle.
 *
 * Wasm only kicks in once the user crosses into (dashboard).
 *
 * Static defenses (ESLint no-restricted-imports +
 * scripts/check-no-wasm-in-marketing.sh) catch import-graph regressions,
 * but a dynamic `import("@/lib/wasm-core")` would slip past both. This
 * spec watches the actual network requests and is the only layer that
 * catches that.
 */

function isWasmRequest(url: string): boolean {
  // Both the .wasm asset itself and the JS chunk wrapping agentsmesh-wasm
  // are indicators that wasm boot has started.
  return url.endsWith(".wasm") || /agentsmesh[-_]wasm/.test(url);
}

test.describe("Pre-dashboard routes are wasm-zero", () => {
  test.use({ storageState: { cookies: [], origins: [] } });

  for (const path of [
    "/login",
    "/register",
    "/forgot-password",
    "/onboarding",
    "/invite/some-token",
    "/runners/authorize",
    "/auth/callback",
    "/auth/sso/callback",
  ]) {
    test(`anonymous visit to ${path} does not request wasm`, async ({ page }) => {
      const wasmRequests: string[] = [];
      page.on("request", (req) => {
        const url = req.url();
        if (isWasmRequest(url)) wasmRequests.push(url);
      });

      await page.goto(path);
      await page.waitForLoadState("networkidle");

      expect(
        wasmRequests,
        `Expected zero wasm requests on ${path}; got:\n${wasmRequests.join("\n")}`,
      ).toEqual([]);
    });
  }
});

test.describe("Dashboard still loads wasm after login", () => {
  test.use({ storageState: { cookies: [], origins: [] } });

  test("wasm boots when navigating into the workspace", async ({ browser }) => {
    // Skip the UI form (CI webpack-dev races against fill). Mirror the
    // lightLogin code path: hit Connect AuthService.Login, seed
    // PersistedSession, then measure what gets requested on the
    // dashboard route.
    const apiBaseUrl = getApiBaseUrl();
    const loginRes = await fetch(`${apiBaseUrl}/proto.auth.v1.AuthService/Login`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Connect-Protocol-Version": "1" },
      body: JSON.stringify({ email: TEST_USER.email, password: TEST_USER.password }),
    });
    expect(loginRes.status).toBe(200);
    const data = await loginRes.json();
    const token = data.token;
    const refresh_token = data.refreshToken ?? data.refresh_token;
    const expires_in = Number(data.expiresIn ?? data.expires_in ?? 3600);
    const baseUrl = getWebBaseUrl();
    const expiresAt = Math.floor(Date.now() / 1000) + (expires_in ?? 3600);

    const context = await browser.newContext();
    await context.addInitScript(
      ({ token, refresh_token, expiresAt, baseUrl }) => {
        const u = new URL(baseUrl);
        const port = u.port ? `_${u.port}` : "";
        const raw = `${u.protocol.replace(":", "")}_${u.hostname.toLowerCase()}${port}`;
        const slug = raw.replace(/[^a-zA-Z0-9]/g, "_").slice(0, 64);
        localStorage.setItem(
          `agentsmesh-auth/${slug}/session`,
          JSON.stringify({
            access_token: token,
            refresh_token,
            expires_at: expiresAt,
            base_url: baseUrl,
            current_org_slug: null,
            schema_version: 1,
          }),
        );
      },
      { token, refresh_token, expiresAt, baseUrl },
    );
    const page = await context.newPage();

    const wasmRequests: string[] = [];
    page.on("request", (req) => {
      if (isWasmRequest(req.url())) wasmRequests.push(req.url());
    });

    // The dashboard layout boots wasm on entry. networkidle is unreliable
    // here — the dashboard keeps long-lived connections (SSE / WS / poll)
    // alive once mounted, so waitForLoadState("networkidle") never resolves
    // within timeout. Wait for the first wasm request instead, which is
    // the actual signal we care about.
    const wasmRequest = page.waitForRequest((req) => isWasmRequest(req.url()), {
      timeout: 30_000,
    });
    await page.goto(`${baseUrl}/${TEST_ORG_SLUG}/workspace`);
    await wasmRequest;

    expect(
      wasmRequests.length,
      "dashboard layout must boot wasm on entry",
    ).toBeGreaterThan(0);
    expect(page.url()).toContain(`/${TEST_ORG_SLUG}`);

    await context.close();
  });
});
