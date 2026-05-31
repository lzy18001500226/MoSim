import { readCurrentUser, readCurrentOrg } from "@/stores/auth";
import { create } from "zustand";
import { getChannelService } from "@/lib/wasm-core";
import { getErrorMessage } from "@/lib/utils";
import {
  listChannelMessages,
  sendChannelMessage,
  editChannelMessage,
  deleteChannelMessage,
  getChannelUnreadCounts,
  markChannelRead,
  muteChannel as muteChannelConnect,
} from "@/lib/api/facade/channelConnect";
import { getCache, updateCache } from "./channelMessageTypes";
import type { ChannelMessageState } from "./channelMessageTypes";
import type { ChannelMessage } from "@/lib/api/facade/channel";
import {
  toWasmProjection,
  fromWasmProjection,
  type WasmChannelMessage,
} from "./channelMessageWasmProjection";
import { registerOrgScopedReset } from "@/lib/org-scope/registry";

export { EMPTY_CACHE, type ChannelMessageCache } from "./channelMessageTypes";

/** Number of messages to fetch on initial channel load. */
export const INITIAL_MESSAGE_LIMIT = 20;
/** Number of messages to fetch when loading older history. */
export const LOAD_MORE_MESSAGE_LIMIT = 30;

const svc = () => getChannelService();

function orgSlug(): string {
  return readCurrentOrg()?.slug ?? "";
}

export function readMessages(channelId: number): { messages: ChannelMessage[]; hasMore: boolean } {
  const raw = svc().get_messages_json(BigInt(channelId));
  if (!raw) return { messages: [], hasMore: false };
  const parsed = typeof raw === "string" ? JSON.parse(raw) : (raw as { messages?: WasmChannelMessage[]; has_more?: boolean });
  const wasmMessages = parsed.messages || [];
  return { messages: wasmMessages.map(fromWasmProjection), hasMore: parsed.has_more ?? false };
}

const bumpMessages = () =>
  useChannelMessageStore.setState((s) => ({ _messagesTick: s._messagesTick + 1 }));

export const useChannelMessageStore = create<ChannelMessageState>((set, get) => ({
  cache: {},
  _messagesTick: 0,
  _unreadTick: 0,

  fetchMessages: async (channelId, limit = INITIAL_MESSAGE_LIMIT, beforeId) => {
    const isLoadMore = beforeId !== undefined;
    const current = getCache(get(), channelId);
    if (isLoadMore ? current.loadingMore : current.loading) return;

    set((state) =>
      updateCache(state, channelId, isLoadMore ? { loadingMore: true } : { loading: true, error: null }),
    );

    try {
      const { items, has_more } = await listChannelMessages(orgSlug(), channelId, {
        beforeId,
        limit,
      });
      const wasmItems = items.map(toWasmProjection);
      if (isLoadMore) {
        svc().prepend_messages(BigInt(channelId), JSON.stringify(wasmItems), has_more);
      } else {
        svc().set_messages(BigInt(channelId), JSON.stringify(wasmItems), has_more);
      }
      set((state) => updateCache(state, channelId, {
        loading: false, loadingMore: false, error: null,
      }));
      bumpMessages();
    } catch (error: unknown) {
      const msg = getErrorMessage(error, "Unknown error");
      console.error("Failed to fetch messages:", msg);
      set((state) => updateCache(state, channelId, {
        loading: false, loadingMore: false, error: isLoadMore ? null : msg,
      }));
    }
  },

  sendMessage: async (channelId, payload, podKey) => {
    try {
      const msg = await sendChannelMessage(orgSlug(), channelId, {
        source: payload.source,
        mentions: payload.mentions && Object.keys(payload.mentions).length > 0 ? payload.mentions : undefined,
        attachment_key: payload.attachment_key,
        pod_key: podKey,
      });

      // POST response may lack sender_user — backfill from auth store.
      if (!msg.sender_user && msg.sender_user_id) {
        const authUser = readCurrentUser();
        if (authUser && authUser.id === msg.sender_user_id) {
          msg.sender_user = {
            id: authUser.id,
            username: authUser.username,
            name: authUser.name,
            avatar_url: authUser.avatar_url,
          };
        }
      }

      svc().add_message(BigInt(channelId), JSON.stringify(toWasmProjection(msg)));
      bumpMessages();
      return msg;
    } catch (error: unknown) {
      console.error("Failed to send message:", getErrorMessage(error, "Unknown error"));
      throw error;
    }
  },

  addMessage: (_channelId, message) => {
    svc().on_new_message(JSON.stringify(toWasmProjection(message)));
    bumpMessages();
  },

  editMessage: async (channelId, messageId, payload) => {
    try {
      const updated = await editChannelMessage(orgSlug(), channelId, messageId, {
        source: payload.source,
        mentions: payload.mentions && Object.keys(payload.mentions).length > 0 ? payload.mentions : undefined,
      });
      svc().update_message_local(BigInt(channelId), JSON.stringify(toWasmProjection(updated)));
      bumpMessages();
    } catch (error: unknown) {
      console.error("Failed to edit message:", getErrorMessage(error, "Unknown error"));
      throw error;
    }
  },

  deleteMessage: async (channelId, messageId) => {
    try {
      await deleteChannelMessage(orgSlug(), channelId, messageId);
      svc().remove_message_local(BigInt(channelId), BigInt(messageId));
      bumpMessages();
    } catch (error: unknown) {
      console.error("Failed to delete message:", getErrorMessage(error, "Unknown error"));
      throw error;
    }
  },

  updateMessage: (channelId, data) => {
    svc().update_message_local(BigInt(channelId), JSON.stringify(toWasmProjection(data)));
    bumpMessages();
  },

  removeMessage: (channelId, messageId) => {
    svc().remove_message_local(BigInt(channelId), BigInt(messageId));
    bumpMessages();
  },

  fetchUnreadCounts: async () => {
    try {
      const unread = await getChannelUnreadCounts(orgSlug());
      svc().set_unread_counts(JSON.stringify(unread));
      set((s) => ({ _unreadTick: s._unreadTick + 1 }));
    } catch (error: unknown) {
      console.error("Failed to fetch unread counts:", getErrorMessage(error, "Unknown error"));
    }
  },

  markRead: async (channelId, messageId) => {
    try {
      await markChannelRead(orgSlug(), channelId, messageId);
      svc().clear_channel_unread(BigInt(channelId));
      set((s) => ({ _unreadTick: s._unreadTick + 1 }));
    } catch (error: unknown) {
      console.error("Failed to mark channel as read:", getErrorMessage(error, "Unknown error"));
    }
  },

  muteChannel: async (channelId, muted) => {
    try {
      await muteChannelConnect(orgSlug(), channelId, muted);
    } catch (error: unknown) {
      console.error("Failed to update mute setting:", getErrorMessage(error, "Unknown error"));
      throw error;
    }
  },

  incrementUnread: (channelId) => {
    svc().increment_unread(BigInt(channelId));
    set((s) => ({ _unreadTick: s._unreadTick + 1 }));
  },

  clearChannelUnread: (channelId) => {
    svc().clear_channel_unread(BigInt(channelId));
    set((s) => ({ _unreadTick: s._unreadTick + 1 }));
  },
}));

export {
  useChannelMessages,
  useUnreadCounts,
  useUnreadCount,
  useTotalUnreadCount,
  type ChannelMessagesView,
} from "./channelMessageSelectors";

registerOrgScopedReset(() => {
  const ch = svc() as unknown as { set_unread_counts?: (json: string) => void };
  ch.set_unread_counts?.("{}");
  useChannelMessageStore.setState((s) => ({
    cache: {},
    _messagesTick: s._messagesTick + 1,
    _unreadTick: s._unreadTick + 1,
  }));
});
