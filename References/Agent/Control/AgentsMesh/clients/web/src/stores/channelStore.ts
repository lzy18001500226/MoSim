import { create } from "zustand";
import { getErrorMessage } from "@/lib/utils";
import { getChannelService } from "@/lib/wasm-core";
import { readCurrentOrg } from "@/stores/auth";
import {
  listChannels,
  getChannel as getChannelConnect,
  createChannel as createChannelConnect,
  updateChannel as updateChannelConnect,
  archiveChannel as archiveChannelConnect,
  unarchiveChannel as unarchiveChannelConnect,
  joinChannelPod,
  leaveChannelPod,
  joinChannel as joinChannelConnect,
  leaveChannel as leaveChannelConnect,
  inviteChannelMembers,
  listChannelMembers,
} from "@/lib/api/facade/channelConnect";
import type { Channel } from "./channelTypes";
import { readChannel } from "./channelSelectors";

export type { Channel, ChannelLastMessage, ChannelMember } from "./channelTypes";
export { useChannels, useCurrentChannel, useChannelMembers, getLastMessage } from "./channelSelectors";

const svc = () => getChannelService();
const bump = () => useChannelStore.setState((s) => ({ _tick: s._tick + 1 }));

function orgSlug(): string {
  return readCurrentOrg()?.slug ?? "";
}

interface ChannelState {
  _tick: number; loading: boolean; channelLoading: boolean;
  error: string | null; selectedChannelId: number | null; searchQuery: string; showArchived: boolean;
  currentChannel: Channel | null;
  setSelectedChannelId: (id: number | null) => void; setSearchQuery: (q: string) => void; setShowArchived: (s: boolean) => void;
  fetchChannels: (f?: { includeArchived?: boolean }) => Promise<void>; fetchChannel: (id: number) => Promise<void>;
  createChannel: (d: {
    name: string; description?: string; document?: string;
    repositoryId?: number; ticketSlug?: string;
    visibility?: "public" | "private"; memberIds?: number[];
  }) => Promise<Channel>;
  updateChannel: (id: number, d: Partial<{ name: string; description: string; document: string }>) => Promise<Channel>;
  archiveChannel: (id: number) => Promise<void>; unarchiveChannel: (id: number) => Promise<void>;
  joinChannel: (channelId: number, podKey: string) => Promise<void>; leaveChannel: (channelId: number, podKey: string) => Promise<void>;
  joinUserChannel: (channelId: number) => Promise<void>;
  leaveUserChannel: (channelId: number) => Promise<void>;
  inviteMembers: (channelId: number, userIds: number[]) => Promise<void>;
  patchChannelMemberCount: (channelId: number, delta: number) => void;
  setCurrentChannel: (ch: Channel | null) => void; clearError: () => void;
}

export const useChannelStore = create<ChannelState>((set, get) => ({
  _tick: 0, loading: false, channelLoading: false,
  error: null, selectedChannelId: null, searchQuery: "", showArchived: false,
  currentChannel: null,

  setSelectedChannelId: (id) => {
    set({ selectedChannelId: id });
    if (id !== null) {
      svc().select_channel(BigInt(id));
      bump();
      get().fetchChannel(id);
    } else {
      svc().select_channel(undefined as unknown as bigint);
      bump();
    }
  },

  setSearchQuery: (query) => set({ searchQuery: query }),
  setShowArchived: (show) => set({ showArchived: show }),

  fetchChannels: async (filters) => {
    set({ error: null });
    try {
      const { items } = await listChannels(orgSlug(), {
        includeArchived: filters?.includeArchived,
      });
      svc().set_channels(JSON.stringify(items));
      bump();
    } catch (e: unknown) { set({ error: getErrorMessage(e, "Failed to fetch channels") }); }
  },

  fetchChannel: async (id) => {
    set({ channelLoading: true, error: null });
    try {
      const channel = await getChannelConnect(orgSlug(), id);
      svc().update_channel_local(BigInt(id), JSON.stringify(channel));
      set({ channelLoading: false, _tick: get()._tick + 1 });
    } catch (e: unknown) { set({ error: getErrorMessage(e, "Failed to fetch channel"), channelLoading: false }); }
  },

  createChannel: async (data) => {
    set({ error: null });
    try {
      const channel = await createChannelConnect(orgSlug(), {
        name: data.name, description: data.description, document: data.document,
        repository_id: data.repositoryId, ticket_slug: data.ticketSlug,
        visibility: data.visibility, member_ids: data.memberIds,
      });
      svc().add_channel_local(JSON.stringify(channel));
      bump();
      return channel as unknown as Channel;
    } catch (e: unknown) { set({ error: getErrorMessage(e, "Failed to create channel") }); throw e; }
  },

  updateChannel: async (id, data) => {
    try {
      const channel = await updateChannelConnect(orgSlug(), id, data);
      svc().update_channel_local(BigInt(id), JSON.stringify(channel));
      bump();
      return channel as unknown as Channel;
    } catch (e: unknown) { set({ error: getErrorMessage(e, "Failed to update channel") }); throw e; }
  },

  archiveChannel: async (id) => {
    try {
      await archiveChannelConnect(orgSlug(), id);
      const current = readChannel(id);
      if (current) svc().update_channel_local(BigInt(id), JSON.stringify({ ...current, is_archived: true }));
      bump();
    }
    catch (e: unknown) { set({ error: getErrorMessage(e, "Failed to archive channel") }); throw e; }
  },

  unarchiveChannel: async (id) => {
    try {
      await unarchiveChannelConnect(orgSlug(), id);
      const current = readChannel(id);
      if (current) svc().update_channel_local(BigInt(id), JSON.stringify({ ...current, is_archived: false }));
      bump();
    }
    catch (e: unknown) { set({ error: getErrorMessage(e, "Failed to unarchive channel") }); throw e; }
  },

  joinChannel: async (channelId, podKey) => {
    try {
      await joinChannelPod(orgSlug(), channelId, podKey);
      const fresh = await getChannelConnect(orgSlug(), channelId);
      svc().update_channel_local(BigInt(channelId), JSON.stringify(fresh));
      bump();
    }
    catch (e: unknown) { set({ error: getErrorMessage(e, "Failed to join channel") }); throw e; }
  },

  leaveChannel: async (channelId, podKey) => {
    try {
      await leaveChannelPod(orgSlug(), channelId, podKey);
      const fresh = await getChannelConnect(orgSlug(), channelId);
      svc().update_channel_local(BigInt(channelId), JSON.stringify(fresh));
      bump();
    }
    catch (e: unknown) { set({ error: getErrorMessage(e, "Failed to leave channel") }); throw e; }
  },

  joinUserChannel: async (channelId) => {
    try {
      await joinChannelConnect(orgSlug(), channelId);
      get().patchChannelMemberCount(channelId, 1);
    } catch (e: unknown) { set({ error: getErrorMessage(e, "Failed to join channel") }); throw e; }
  },

  leaveUserChannel: async (channelId) => {
    try {
      await leaveChannelConnect(orgSlug(), channelId);
      get().patchChannelMemberCount(channelId, -1);
    } catch (e: unknown) { set({ error: getErrorMessage(e, "Failed to leave channel") }); throw e; }
  },

  inviteMembers: async (channelId, userIds) => {
    try {
      await inviteChannelMembers(orgSlug(), channelId, userIds);
      await listChannelMembers(orgSlug(), channelId);
      get().patchChannelMemberCount(channelId, userIds.length);
    } catch (e: unknown) { set({ error: getErrorMessage(e, "Failed to invite members") }); throw e; }
  },

  patchChannelMemberCount: (channelId, delta) => {
    const current = readChannel(channelId);
    if (!current) return;
    const next = { ...current, member_count: Math.max(0, current.member_count + delta) };
    svc().update_channel_local(BigInt(channelId), JSON.stringify(next));
    bump();
  },

  setCurrentChannel: (channel) => {
    svc().set_current_channel(channel ? BigInt(channel.id) : null);
    set({ currentChannel: channel });
    bump();
  },

  clearError: () => set({ error: null }),
}));
