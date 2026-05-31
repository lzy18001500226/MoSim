import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

// Migrated R5+: was REST `api.post('/api/v1/orgs/{slug}/channels')`, now
// `cc.channel.createChannel({orgSlug, name})`. Method names are PascalCase
// matching the proto declaration (consistent with the wire path).
test.describe("Channel API", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("create channel and verify in list", async ({ api, db }) => {
    const cc = await api.connect();
    try { db.cleanup(`DELETE FROM channels WHERE name = 'E2E Test Channel' AND organization_id = (SELECT id FROM organizations WHERE slug = '${TEST_ORG_SLUG}')`); } catch { /* ignore */ }

    const created = await cc.channel.createChannel({
      orgSlug: TEST_ORG_SLUG,
      name: "E2E Test Channel",
      description: "Created by E2E test",
    }) as { id: string };
    expect(created.id).toBeTruthy();

    const { items } = await cc.channel.listChannels({ orgSlug: TEST_ORG_SLUG }) as { items: unknown[] };
    expect(Array.isArray(items)).toBe(true);

    if (created.id) {
      await cc.channel.archiveChannel({ orgSlug: TEST_ORG_SLUG, id: created.id });
    }
  });

  test("update channel description", async ({ api }) => {
    const cc = await api.connect();
    const created = await cc.channel.createChannel({
      orgSlug: TEST_ORG_SLUG,
      name: "E2E Update Ch " + Date.now(),
    }) as { id: string };
    expect(created.id, "createChannel must return an id").toBeTruthy();

    const updated = await cc.channel.updateChannel({
      orgSlug: TEST_ORG_SLUG,
      id: created.id,
      description: "Updated by E2E",
    }) as { description?: string };
    expect(updated.description).toBe("Updated by E2E");

    await cc.channel.archiveChannel({ orgSlug: TEST_ORG_SLUG, id: created.id });
  });

  test("duplicate channel name returns conflict", async ({ api }) => {
    const cc = await api.connect();
    const name = "E2E Dup Chan " + Date.now();
    const first = await cc.channel.createChannel({ orgSlug: TEST_ORG_SLUG, name }) as { id: string };

    // Connect maps `AlreadyExists` to HTTP 409 — `ConnectError.status` is
    // populated by the typed client and we catch on it rather than reading
    // `res.status` directly (no REST wire surface anymore).
    await expect(
      cc.channel.createChannel({ orgSlug: TEST_ORG_SLUG, name })
    ).rejects.toMatchObject({ status: 409 });

    if (first.id) {
      await cc.channel.archiveChannel({ orgSlug: TEST_ORG_SLUG, id: first.id });
    }
  });
});
