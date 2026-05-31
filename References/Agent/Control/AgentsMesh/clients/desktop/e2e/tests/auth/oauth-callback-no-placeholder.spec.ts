import { test, expect } from "../../fixtures";
import { LoginPage } from "../../pages/login.page";
import { resolve, join } from "node:path";
import { rmSync, existsSync, readdirSync, statSync } from "node:fs";

const FRESH_USER_DATA = resolve(__dirname, "../../.auth/electron-userdata-oauth-callback-cleanup");

test.use({
  skipAuthRestore: true,
  userDataDir: FRESH_USER_DATA,
});

test.beforeAll(() => {
  rmSync(FRESH_USER_DATA, { recursive: true, force: true });
});

function walkSessionFiles(root: string): string[] {
  if (!existsSync(root)) return [];
  const out: string[] = [];
  for (const name of readdirSync(root)) {
    const p = join(root, name);
    if (statSync(p).isDirectory()) out.push(...walkSessionFiles(p));
    else if (statSync(p).isFile() && name === "session.json") out.push(p);
  }
  return out;
}

test.describe("Auth · OAuth callback no placeholder", () => {
  test("failed OAuth (bogus token) wipes auth state — no phantom session", async ({
    page,
    electronApp,
  }) => {
    const login = new LoginPage(page);
    await login.expectOnLoginPage();

    // Emit a deep-link as the main process would after open-url. The
    // token is structurally valid but not signed by our backend, so
    // /users/me returns 401 and the catch branch in OAuthCallbackPage
    // must invoke logout() to wipe the placeholder auth state.
    await electronApp.evaluate(({ BrowserWindow }) => {
      const win = BrowserWindow.getAllWindows()[0];
      if (!win) throw new Error("no BrowserWindow");
      win.webContents.send(
        "oauth:callback",
        "agentsmesh://oauth/callback?token=invalid.jwt.token&refresh_token=invalid-refresh",
      );
    });

    await page.waitForFunction(
      () => window.location.hash.includes("/auth/callback"),
      undefined,
      { timeout: 5000 },
    );

    // Wait for either login redirect (logout completed) or error UI.
    await page.waitForFunction(
      () => {
        const hash = window.location.hash;
        if (hash.includes("/login")) return true;
        const text = document.body.textContent || "";
        return /error|failed|invalid/i.test(text);
      },
      undefined,
      { timeout: 15_000 },
    );

    // Critical assertion: no namespaced session got persisted from the
    // bogus token. The Rust manager held a placeholder briefly during
    // getMe; the catch handler logout() must have cleared it.
    const userData = await electronApp.evaluate(({ app }) => app.getPath("userData")) as string;
    const sessionFiles = walkSessionFiles(join(userData, "agentsmesh"));
    expect(sessionFiles.length).toBe(0);
  });
});
