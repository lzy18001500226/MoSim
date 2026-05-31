import { test, expect } from "../../fixtures";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { currentRoute } from "../../helpers/nav";
import { join } from "node:path";
import { existsSync, readdirSync, readFileSync } from "node:fs";

test.describe("Auth · session persistence", () => {
  test("hash route indicates a logged-in page (not /login)", async ({ page }) => {
    // Give React Router a moment to settle after auth-state restore + reload.
    await page.waitForTimeout(500);
    const route = await currentRoute(page);
    expect(route).not.toContain("/login");
    expect(
      route.includes(`/${TEST_ORG_SLUG}/`) ||
      route.includes("/workspace") ||
      route.includes("/onboarding") ||
      route.includes("/settings")
    ).toBe(true);
  });

  test("localStorage has at least one agentsmesh-* key", async ({ page }) => {
    const keys = await page.evaluate(() => Object.keys(window.localStorage).filter((k) => k.startsWith("agentsmesh-")));
    expect(keys.length).toBeGreaterThan(0);
  });

  // I1 invariant — the persisted session must live under a namespaced key
  // (`agentsmesh-auth/<url-slug>/session.json`), not the legacy global
  // `agentsmesh-auth.json`. The legacy key is forensically interesting:
  // its presence after bootstrap would mean we'd silently re-introduced
  // the cross-server contamination bug from v0.31.
  test("session is written to namespaced FileStorage path, no legacy file", async ({ electronApp }) => {
    const userData = await electronApp.evaluate(({ app }) => app.getPath("userData")) as string;
    const dir = join(userData, "agentsmesh");
    expect(existsSync(join(dir, "agentsmesh-auth.json")),
      "v0.31 legacy global key must NOT exist after bootstrap").toBe(false);
    const root = join(dir, "agentsmesh-auth");
    expect(existsSync(root)).toBe(true);
    const namespaces = readdirSync(root).filter((n) => existsSync(join(root, n, "session.json")));
    expect(namespaces.length).toBe(1);
    expect(namespaces[0]).toMatch(/^http_/);
  });

  test("persisted session blob does not contain user identity fields", async ({ electronApp }) => {
    const userData = await electronApp.evaluate(({ app }) => app.getPath("userData")) as string;
    const root = join(userData, "agentsmesh", "agentsmesh-auth");
    expect(existsSync(root)).toBe(true);
    const ns = readdirSync(root).find((n) => existsSync(join(root, n, "session.json")));
    expect(ns).toBeTruthy();
    const blob = readFileSync(join(root, ns!, "session.json"), "utf-8");
    expect(blob).not.toContain("\"email\"");
    expect(blob).not.toContain("\"username\"");
    expect(blob).not.toContain("\"name\"");
    expect(blob).not.toContain("\"avatar_url\"");
    expect(blob).toContain("\"access_token\"");
    expect(blob).toContain("\"refresh_token\"");
    expect(blob).toContain("\"expires_at\"");
    expect(blob).toContain("\"base_url\"");
  });
});
