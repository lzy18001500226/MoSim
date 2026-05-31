// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

const REPO_ID = 1; // demo-webapp from seed

/**
 * Extensions Skills comprehensive tests.
 * Maps to: TC-SKILL-001~007, TC-EXTSET-001~002
 */
test.describe("Extensions Skills", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("list user skills for repository", async ({ api }) => {
    const cc = await api.connect();
    const res = await cc.repoSkill.listRepoSkills({
      orgSlug: TEST_ORG_SLUG,
      repositoryId: REPO_ID,
      scope: "user",
    }) as { items: unknown[] };
    expect(Array.isArray(res.items)).toBe(true);
  });

  test("list org skills for repository", async ({ api }) => {
    const cc = await api.connect();
    const res = await cc.repoSkill.listRepoSkills({
      orgSlug: TEST_ORG_SLUG,
      repositoryId: REPO_ID,
      scope: "org",
    }) as { items: unknown[] };
    expect(Array.isArray(res.items)).toBe(true);
  });

  test("marketplace skills endpoint works", async ({ api }) => {
    const cc = await api.connect();
    const res = await cc.market.listMarketSkills({ orgSlug: TEST_ORG_SLUG }) as { items: unknown[] };
    expect(Array.isArray(res.items)).toBe(true);
  });

  test("extensions settings page shows skills section", async ({ page }) => {
    await page.goto(`/${TEST_ORG_SLUG}/settings?scope=organization&tab=extensions`);
    await page.waitForLoadState("load");
    const body = await page.textContent("body");
    expect(body).toMatch(/skill|extension|扩展|技能/i);
  });

  test("extensions page shows registries and templates tabs", async ({ page }) => {
    await page.goto(`/${TEST_ORG_SLUG}/settings?scope=organization&tab=extensions`);
    await page.waitForLoadState("load");
    const body = await page.textContent("body");
    expect(body).toMatch(/registr|template|MCP|注册|模板/i);
  });

  test("skill registries list endpoint works", async ({ api }) => {
    const cc = await api.connect();
    const res = await cc.skillRegistry.listSkillRegistries({ orgSlug: TEST_ORG_SLUG }) as { items: unknown[] };
    expect(Array.isArray(res.items)).toBe(true);
  });
});
