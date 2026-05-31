// Migrated R5+: Connect-RPC only (no REST middle layer).
//
// Reply-to chains are the only way conversations stay readable past 50+
// messages. Backend stores reply_to in messages.reply_to → ParentMessageID,
// and SendChannelMessageRequest accepts it. This spec proves the round-trip:
// send A → send B with reply_to=A → list messages and assert B.reply_to == A.id.
// Without it, a reply field rename or DB-column drop would silently turn
// every reply into a top-level message and nobody would notice until users
// reported "lost context" two weeks later.
import { test, expect } from "../../fixtures/index";
import { TEST_ORG_SLUG } from "../../helpers/env";
import { clearAuthRateLimit } from "../../helpers/redis";
import { textContent } from "../../helpers/test-data";

test.describe("Channel reply-to chain", () => {
  test.beforeEach(async () => { clearAuthRateLimit(); });

  test("reply_to round-trips through both send and list endpoints", async ({ api }) => {
    const cc = await api.connect();
    const channel = await cc.channel.createChannel({
      orgSlug: TEST_ORG_SLUG,
      name: "E2E ReplyRT " + Date.now(),
      visibility: "public",
    }) as { id: bigint };

    try {
      const parent = await cc.channel.sendChannelMessage({
        orgSlug: TEST_ORG_SLUG,
        channelId: channel.id,
        contentJson: JSON.stringify(textContent("the parent")),
      }) as { id: bigint; replyTo?: bigint };
      expect(parent.replyTo == null).toBe(true);

      const child = await cc.channel.sendChannelMessage({
        orgSlug: TEST_ORG_SLUG,
        channelId: channel.id,
        contentJson: JSON.stringify(textContent("the reply")),
        replyTo: parent.id,
      }) as { id: bigint; replyTo: bigint };
      expect(child.replyTo).toBe(parent.id);

      const list = await cc.channel.listChannelMessages({
        orgSlug: TEST_ORG_SLUG,
        channelId: channel.id,
      }) as { items: { id: bigint; replyTo?: bigint }[] };
      const fetchedChild = list.items.find((m) => m.id === child.id);
      expect(fetchedChild?.replyTo).toBe(parent.id);
    } finally {
      await cc.channel.archiveChannel({ orgSlug: TEST_ORG_SLUG, id: channel.id });
    }
  });
});
