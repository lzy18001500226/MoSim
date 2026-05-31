// AUTO-GENERATED — do not edit by hand. Regenerate: pnpm --filter desktop e2e:gen
import { test } from "../../../fixtures/electron-shared.fixture";
import { invokeIpcContract } from "../../../helpers/ipc-contract";

test.describe.configure({ mode: "serial" });

test.describe("IPC · channel", () => {
  test("channelAddChannelLocal", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "channelAddChannelLocal", returnType: "void" }, "");
  });

  test("channelAddMessage", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "channelAddMessage", returnType: "void" }, 0, "");
  });

  test("channelChannelMembersJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "channelChannelMembersJson", returnType: "string" }, 0);
  });

  test("channelChannelPodsJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "channelChannelPodsJson", returnType: "string" }, 0);
  });

  test("channelChannelsJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "channelChannelsJson", returnType: "string" });
  });

  test("channelClearChannelMentions", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "channelClearChannelMentions", returnType: "void" }, 0);
  });

  test("channelClearChannelUnread", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "channelClearChannelUnread", returnType: "void" }, 0);
  });

  test("channelCurrentChannelJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "channelCurrentChannelJson", returnType: "string" });
  });

  test("channelFilterChannelsJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "channelFilterChannelsJson", returnType: "string" }, "", false);
  });

  test("channelGetChannelJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "channelGetChannelJson", returnType: "string" }, 0);
  });

  test("channelGetLastMessageJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "channelGetLastMessageJson", returnType: "string" }, 0);
  });

  test("channelGetMentionCount", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "channelGetMentionCount", returnType: "number" }, 0);
  });

  test("channelGetMessagesJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "channelGetMessagesJson", returnType: "string" }, 0);
  });

  test("channelGetUnreadCount", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "channelGetUnreadCount", returnType: "number" }, 0);
  });

  test("channelIncrementMention", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "channelIncrementMention", returnType: "void" }, 0);
  });

  test("channelIncrementUnread", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "channelIncrementUnread", returnType: "void" }, 0);
  });

  test("channelMentionCountsJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "channelMentionCountsJson", returnType: "string" });
  });

  test("channelOnNewMessage", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "channelOnNewMessage", returnType: "boolean" }, "");
  });

  test("channelPrependMessages", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "channelPrependMessages", returnType: "void" }, 0, "", false);
  });

  test("channelRemoveChannelLocal", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "channelRemoveChannelLocal", returnType: "void" }, 0);
  });

  test("channelRemoveMessageLocal", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "channelRemoveMessageLocal", returnType: "void" }, 0, 0);
  });

  test("channelSelectChannel", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "channelSelectChannel", returnType: "string" }, 0);
  });

  test("channelSetChannelPodsLocal", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "channelSetChannelPodsLocal", returnType: "any" });
  });

  test("channelSetChannels", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "channelSetChannels", returnType: "void" }, "");
  });

  test("channelSetCurrentChannel", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "channelSetCurrentChannel", returnType: "void" }, 0);
  });

  test("channelSetCurrentUser", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "channelSetCurrentUser", returnType: "void" }, "");
  });

  test("channelSetCurrentUserId", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "channelSetCurrentUserId", returnType: "void" }, 0);
  });

  test("channelSetLastMessage", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "channelSetLastMessage", returnType: "void" }, 0, "");
  });

  test("channelSetMentionCounts", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "channelSetMentionCounts", returnType: "void" }, "");
  });

  test("channelSetMessages", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "channelSetMessages", returnType: "void" }, 0, "", false);
  });

  test("channelSetUnreadCounts", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "channelSetUnreadCounts", returnType: "void" }, "");
  });

  test("channelSortedChannelIdsJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "channelSortedChannelIdsJson", returnType: "string" }, "", false);
  });

  test("channelTotalMentionCount", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "channelTotalMentionCount", returnType: "number" });
  });

  test("channelTotalUnreadCount", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "channelTotalUnreadCount", returnType: "number" });
  });

  test("channelUnreadCountsJson", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "channelUnreadCountsJson", returnType: "string" });
  });

  test("channelUpdateChannelLocal", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "channelUpdateChannelLocal", returnType: "void" }, 0, "");
  });

  test("channelUpdateMessageLocal", async ({ sharedPage }) => {
    await invokeIpcContract(sharedPage, { method: "channelUpdateMessageLocal", returnType: "void" }, 0, "");
  });
});
