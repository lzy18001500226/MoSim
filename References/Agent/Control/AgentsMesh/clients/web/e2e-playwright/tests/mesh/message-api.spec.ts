// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";

test.describe("Mesh Message API Operations", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("list messages via topology", async ({ api }) => {
    const cc = await api.connect();
    const topology = await cc.mesh.getMeshTopology({ orgSlug: TEST_ORG_SLUG });
    expect(topology).toBeTruthy();
  });

  test("get channel unread counts", async ({ api }) => {
    const cc = await api.connect();
    const counts = await cc.channel.getChannelUnreadCounts({ orgSlug: TEST_ORG_SLUG }) as {
      unread: Record<string, bigint>;
    };
    expect(counts.unread).toBeDefined();
  });
});
