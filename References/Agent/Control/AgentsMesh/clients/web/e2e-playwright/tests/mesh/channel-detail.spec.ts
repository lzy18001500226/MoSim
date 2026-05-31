// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

test.describe("Channel Page", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("API: list channels", async ({ api }) => {
    const cc = await api.connect();
    const { items } = await cc.channel.listChannels({ orgSlug: TEST_ORG_SLUG }) as {
      items: unknown[];
    };
    expect(Array.isArray(items)).toBe(true);
  });

  test("API: create and get channel detail", async ({ api }) => {
    const cc = await api.connect();
    const name = `e2e-ch-${Date.now()}`;
    const created = await cc.channel.createChannel({
      orgSlug: TEST_ORG_SLUG,
      name,
      description: "E2E channel detail test",
    }) as { id: bigint };
    expect(created.id).toBeTruthy();

    const detail = await cc.channel.getChannel({
      orgSlug: TEST_ORG_SLUG,
      id: created.id,
    }) as { id: bigint; name: string };
    expect(detail.name).toBe(name);

    await cc.channel.archiveChannel({ orgSlug: TEST_ORG_SLUG, id: created.id });
  });

  test("UI: channels page loads without errors", async ({ page }) => {
    const consoleErrors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") consoleErrors.push(msg.text());
    });

    await page.goto(`/${TEST_ORG_SLUG}/channels`);
    await page.waitForLoadState("load");

    const jsonErrors = consoleErrors.filter(
      (e) => e.includes("missing field") || e.includes("is not valid JSON")
    );
    expect(jsonErrors).toHaveLength(0);
  });
});
