// Migrated R5+: Connect-RPC only (no REST middle layer).
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";
import { textContent } from "../../helpers/test-data";

test.describe("Channel Moderation API", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  let channelId: bigint | null = null;

  test.afterEach(async ({ api }) => {
    if (channelId) {
      const cc = await api.connect();
      await cc.channel.archiveChannel({ orgSlug: TEST_ORG_SLUG, id: channelId }).catch(() => {});
      channelId = null;
    }
  });

  test("archive and unarchive channel", async ({ api }) => {
    const cc = await api.connect();
    const created = await cc.channel.createChannel({
      orgSlug: TEST_ORG_SLUG,
      name: `e2e-archive-${Date.now()}`,
    }) as { id: bigint };
    channelId = created.id;

    await cc.channel.archiveChannel({ orgSlug: TEST_ORG_SLUG, id: created.id });
    await cc.channel.unarchiveChannel({ orgSlug: TEST_ORG_SLUG, id: created.id });
  });

  test("send, edit and delete message", async ({ api }) => {
    const cc = await api.connect();
    const created = await cc.channel.createChannel({
      orgSlug: TEST_ORG_SLUG,
      name: `e2e-msg-${Date.now()}`,
    }) as { id: bigint };
    channelId = created.id;

    // Connect carries structured AST as `contentJson` (string). The server
    // parser still accepts it under the same schema v1.
    const sent = await cc.channel.sendChannelMessage({
      orgSlug: TEST_ORG_SLUG,
      channelId: created.id,
      contentJson: JSON.stringify(textContent("E2E test message")),
    }) as { id: bigint };
    expect(sent.id).toBeTruthy();

    if (sent.id) {
      const edited = await cc.channel.editChannelMessage({
        orgSlug: TEST_ORG_SLUG,
        channelId: created.id,
        messageId: sent.id,
        contentJson: JSON.stringify(textContent("E2E edited message")),
      }) as { id: bigint; body: string };
      expect(edited.body).toBe("E2E edited message");

      await cc.channel.deleteChannelMessage({
        orgSlug: TEST_ORG_SLUG,
        channelId: created.id,
        messageId: sent.id,
      });
    }
  });

  test("mark channel read", async ({ api }) => {
    const cc = await api.connect();
    const created = await cc.channel.createChannel({
      orgSlug: TEST_ORG_SLUG,
      name: `e2e-read-${Date.now()}`,
    }) as { id: bigint };
    channelId = created.id;

    const sent = await cc.channel.sendChannelMessage({
      orgSlug: TEST_ORG_SLUG,
      channelId: created.id,
      contentJson: JSON.stringify(textContent("mark read test")),
    }) as { id: bigint };
    if (sent.id) {
      await cc.channel.markChannelRead({
        orgSlug: TEST_ORG_SLUG,
        channelId: created.id,
        messageId: sent.id,
      });
    }
  });

  test("get channel unread counts", async ({ api }) => {
    const cc = await api.connect();
    const counts = await cc.channel.getChannelUnreadCounts({ orgSlug: TEST_ORG_SLUG }) as {
      unread: Record<string, bigint>;
    };
    expect(counts.unread).toBeDefined();
  });

  test("mute and unmute channel", async ({ api }) => {
    const cc = await api.connect();
    const created = await cc.channel.createChannel({
      orgSlug: TEST_ORG_SLUG,
      name: `e2e-mute-${Date.now()}`,
    }) as { id: bigint };
    channelId = created.id;

    await cc.channel.muteChannel({
      orgSlug: TEST_ORG_SLUG,
      id: created.id,
      muted: true,
    });
  });
});
