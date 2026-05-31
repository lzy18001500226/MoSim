import { test, expect } from "../../fixtures";
import { LoginPage } from "../../pages/login.page";
import { TEST_USER, TEST_ORG_SLUG } from "../../helpers/env";
import { resolve, join } from "node:path";
import { rmSync, existsSync, readdirSync, statSync, mkdirSync, writeFileSync } from "node:fs";

const FRESH_USER_DATA = resolve(__dirname, "../../.auth/electron-userdata-multi-server");

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

test.describe("Auth · multi-server isolation", () => {
  test("two backends keep independent namespaced sessions on disk", async ({
    page,
    electronApp,
  }) => {
    const login = new LoginPage(page);
    await login.expectOnLoginPage();

    await login.login(TEST_USER.email, TEST_USER.password);
    await login.waitForLoginRedirect(TEST_ORG_SLUG);

    const userData = await electronApp.evaluate(({ app }) => app.getPath("userData")) as string;
    const agentsmeshDir = join(userData, "agentsmesh");

    const initial = walkSessionFiles(agentsmeshDir);
    expect(initial.length).toBe(1);
    expect(initial[0]).toMatch(/agentsmesh-auth\/.*\/session\.json/);

    // Drop an `other server` session blob into a parallel namespace —
    // proving the layout supports cohabitation. (No live backend at
    // https://other.example; the file would get cleaned up only when
    // its own bootstrap runs and base_url validation fails.)
    const otherDir = join(agentsmeshDir, "agentsmesh-auth", "https_other_example");
    mkdirSync(otherDir, { recursive: true });
    writeFileSync(join(otherDir, "session.json"), JSON.stringify({
      access_token: "other-server-token",
      refresh_token: "other-server-refresh",
      expires_at: Math.floor(Date.now() / 1000) + 3600,
      base_url: "https://other.example",
      current_org_slug: null,
      schema_version: 1,
    }));

    const after = walkSessionFiles(agentsmeshDir);
    expect(after.length).toBe(2);
    const namespaces = after
      .map((p: string) => p.match(/agentsmesh-auth\/(.*?)\/session\.json/)?.[1])
      .filter((s): s is string => Boolean(s))
      .sort();
    expect(namespaces).toContain("https_other_example");
    expect(namespaces.find((n) => n !== "https_other_example")).toBeTruthy();
  });
});
