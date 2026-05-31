import { test, expect } from "../../fixtures";
import { LoginPage } from "../../pages/login.page";
import { resolve, join } from "node:path";
import { rmSync, mkdirSync, writeFileSync, existsSync, readdirSync, statSync } from "node:fs";

const FRESH_USER_DATA = resolve(__dirname, "../../.auth/electron-userdata-legacy-purge");

test.use({
  skipAuthRestore: true,
  userDataDir: FRESH_USER_DATA,
});

test.beforeAll(() => {
  rmSync(FRESH_USER_DATA, { recursive: true, force: true });
  // Mimic v0.31 layout: userData/agentsmesh/agentsmesh-auth.json. Note this
  // path must match what app.getPath("userData") will resolve to —
  // Electron's userData == --user-data-dir argument we pass in fixtures.
  const dir = join(FRESH_USER_DATA, "agentsmesh");
  mkdirSync(dir, { recursive: true });
  writeFileSync(
    join(dir, "agentsmesh-auth.json"),
    JSON.stringify({
      token: "stale-dev-token",
      refresh_token: "stale-dev-refresh",
      user: {
        id: 1,
        email: "dev@agentsmesh.local",
        username: "devuser",
        name: "Dev User",
        avatar_url: null,
      },
      organizations: [],
      current_org: null,
    }),
    "utf-8",
  );
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

test.describe("Auth · legacy data purged", () => {
  test("v0.31 legacy auth file is unlinked on first bootstrap", async ({ page, electronApp }) => {
    const login = new LoginPage(page);
    await login.expectOnLoginPage();

    // Resolve the actual userData dir from Electron — it normally matches
    // the argument we passed, but we go through the API to be safe.
    const userData = await electronApp.evaluate(({ app }) => app.getPath("userData")) as string;
    const agentsmeshDir = join(userData, "agentsmesh");

    expect(existsSync(join(agentsmeshDir, "agentsmesh-auth.json")),
      "legacy global key file must be unlinked by bootstrap step 1").toBe(false);

    expect(walkSessionFiles(agentsmeshDir).length,
      "no namespaced session was forged out of legacy data").toBe(0);
  });
});
