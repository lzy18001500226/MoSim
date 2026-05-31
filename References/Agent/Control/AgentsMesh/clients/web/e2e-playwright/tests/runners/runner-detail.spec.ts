// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

test.describe("Runner Detail Page", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("API: get single runner returns wrapped response", async ({ api, db }) => {
    const id = db.queryValue(
      `SELECT id FROM runners WHERE organization_id = (SELECT id FROM organizations WHERE slug = '${TEST_ORG_SLUG}') LIMIT 1`
    );
    expect(id, "dev seed must include at least one runner").toBeTruthy();

    const cc = await api.connect();
    const res = await cc.runner.getRunner({
      orgSlug: TEST_ORG_SLUG,
      id: Number(id),
    }) as { runner: { id?: number } };
    expect(res.runner).toBeTruthy();
    expect(res.runner?.id).toBeTruthy();
  });

  test("UI: runner detail page renders without errors", async ({ page, db }) => {
    const id = db.queryValue(
      `SELECT id FROM runners WHERE organization_id = (SELECT id FROM organizations WHERE slug = '${TEST_ORG_SLUG}') LIMIT 1`
    );
    expect(id, "dev seed must include at least one runner").toBeTruthy();

    const consoleErrors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") consoleErrors.push(msg.text());
    });

    await page.goto(`/${TEST_ORG_SLUG}/runners/${id}`);
    await page.waitForLoadState("load");

    const body = await page.textContent("body");
    expect(body).not.toContain("missing field");

    const jsonErrors = consoleErrors.filter(
      (e) => e.includes("missing field") || e.includes("is not valid JSON")
    );
    expect(jsonErrors).toHaveLength(0);
  });
});
