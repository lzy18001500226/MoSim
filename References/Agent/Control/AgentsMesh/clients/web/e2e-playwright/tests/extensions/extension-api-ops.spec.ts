// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

test.describe("Extension Management API", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("list skill registries", async ({ api }) => {
    const cc = await api.connect();
    const res = await cc.skillRegistry.listSkillRegistries({ orgSlug: TEST_ORG_SLUG }) as { items: unknown[] };
    expect(Array.isArray(res.items)).toBe(true);
  });

  test("list skill registry overrides", async ({ api }) => {
    const cc = await api.connect();
    const res = await cc.skillRegistry.listSkillRegistryOverrides({ orgSlug: TEST_ORG_SLUG }) as { items: unknown[] };
    expect(Array.isArray(res.items)).toBe(true);
  });

  test("list market skills", async ({ api }) => {
    const cc = await api.connect();
    const res = await cc.market.listMarketSkills({ orgSlug: TEST_ORG_SLUG }) as { items: unknown[] };
    expect(Array.isArray(res.items)).toBe(true);
  });

  test("list market mcp servers", async ({ api }) => {
    const cc = await api.connect();
    const res = await cc.market.listMarketMcpServers({ orgSlug: TEST_ORG_SLUG }) as { items: unknown[] };
    expect(Array.isArray(res.items)).toBe(true);
  });

  test("list repo skills", async ({ api, db }) => {
    const id = db.queryValue(
      `SELECT id FROM repositories WHERE organization_id = (SELECT id FROM organizations WHERE slug = '${TEST_ORG_SLUG}') LIMIT 1`
    );
    if (!id) return;
    const cc = await api.connect();
    const res = await cc.repoSkill.listRepoSkills({
      orgSlug: TEST_ORG_SLUG,
      repositoryId: Number(id),
    }) as { items: unknown[] };
    expect(Array.isArray(res.items)).toBe(true);
  });

  test("list repo mcp servers", async ({ api, db }) => {
    const id = db.queryValue(
      `SELECT id FROM repositories WHERE organization_id = (SELECT id FROM organizations WHERE slug = '${TEST_ORG_SLUG}') LIMIT 1`
    );
    if (!id) return;
    const cc = await api.connect();
    const res = await cc.repoMcp.listRepoMcpServers({
      orgSlug: TEST_ORG_SLUG,
      repositoryId: Number(id),
    }) as { items: unknown[] };
    expect(Array.isArray(res.items)).toBe(true);
  });
});
