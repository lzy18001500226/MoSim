import { test as setup } from "@playwright/test";
import { ADMIN_USER, getWebBaseUrl, getApiBaseUrl } from "../helpers/env";
import { clearAuthRateLimit } from "../helpers/redis";

const ADMIN_AUTH_FILE = ".auth/admin.json";

setup("authenticate as admin user", async ({ browser }) => {
  clearAuthRateLimit();

  const apiBaseUrl = getApiBaseUrl();
  // R5/R6: REST /api/v1/auth/login removed — Connect-RPC is the only auth wire.
  // Connect+JSON content-type is accepted by the backend Connect handler.
  const loginRes = await fetch(`${apiBaseUrl}/proto.auth.v1.AuthService/Login`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "Connect-Protocol-Version": "1" },
    body: JSON.stringify({ email: ADMIN_USER.email, password: ADMIN_USER.password }),
  });
  if (!loginRes.ok) throw new Error(`admin login failed: ${loginRes.status}`);
  const data = await loginRes.json();
  const token = data.token;
  const refresh_token = data.refreshToken ?? data.refresh_token;
  const expires_in = Number(data.expiresIn ?? data.expires_in ?? 3600);
  const baseUrl = getWebBaseUrl();
  const expiresAt = Math.floor(Date.now() / 1000) + (expires_in ?? 3600);

  const context = await browser.newContext();
  await context.addInitScript(
    ({ token, refresh_token, expiresAt, baseUrl }) => {
      // Mirrors lib/light-session.ts::urlSlug — must stay in sync with
      // Rust SSOT clients/core/crates/auth/src/state.rs::url_slug.
      const u = new URL(baseUrl);
      const port = u.port ? `_${u.port}` : "";
      const raw = `${u.protocol.replace(":", "")}_${u.hostname.toLowerCase()}${port}`;
      const slug = raw.replace(/[^a-zA-Z0-9]/g, "_").slice(0, 64);
      const blob = {
        access_token: token,
        refresh_token,
        expires_at: expiresAt,
        base_url: baseUrl,
        current_org_slug: null,
        schema_version: 1,
      };
      localStorage.setItem(`agentsmesh-auth/${slug}/session`, JSON.stringify(blob));
    },
    { token, refresh_token, expiresAt, baseUrl },
  );

  const page = await context.newPage();
  await page.goto(baseUrl, { waitUntil: "domcontentloaded" });
  await context.storageState({ path: ADMIN_AUTH_FILE });
  await context.close();
});
