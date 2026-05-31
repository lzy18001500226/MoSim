import type { MessageContent, MessageMentions } from "@/lib/viewModels/channelMessage";
import { getChannelService } from "@/lib/wasm-core";
import { readCurrentOrg } from "@/stores/auth";
import {
  updateChannel as updateChannelConnect,
  archiveChannel as archiveChannelConnect,
  unarchiveChannel as unarchiveChannelConnect,
  searchChannelMessages as searchChannelMessagesConnect,
  listChannelPods as listChannelPodsConnect,
  joinChannelPod as joinChannelPodConnect,
  leaveChannelPod as leaveChannelPodConnect,
  inviteChannelMembers as inviteChannelMembersConnect,
  removeChannelMember as removeChannelMemberConnect,
  listChannelMembers as listChannelMembersConnect,
} from "./channelConnect";

export type { MessageContent, MessageMentions } from "@/lib/viewModels/channelMessage";
export type { InlineElement, Block } from "@/lib/viewModels/channelMessage";

export interface ChannelData {
  id: number;
  organization_id: number;
  name: string;
  description?: string;
  document?: string;
  repository_id?: number;
  ticket_id?: number;
  ticket_slug?: string;
  created_by_pod?: string;
  created_by_user_id?: number;
  visibility: "public" | "private";
  is_archived: boolean;
  is_member: boolean;
  member_count: number;
  agent_count: number;
  created_at: string;
  updated_at: string;
}

export interface ChannelMessage {
  id: number;
  channel_id: number;
  sender_pod?: string;
  sender_user_id?: number;
  message_type: string;
  body: string;
  content?: MessageContent;
  mentions?: MessageMentions;
  reply_to?: number;
  edited_at?: string;
  is_deleted?: boolean;
  created_at: string;
  sender_pod_info?: {
    pod_key: string;
    alias?: string;
    agent?: { name: string };
    ticket?: { slug?: string; title?: string };
    loop?: { name?: string };
    title?: string;
  };
  sender_user?: {
    id: number;
    username: string;
    name?: string;
    avatar_url?: string;
  };
}

function orgSlug(): string {
  return readCurrentOrg()?.slug ?? "";
}

// channelApi: thin wrappers around channelConnect that also patch Rust SSOT so
// hooks reading `channel_*_json` selectors observe fresh data. list/get/create
// + message fetch live directly in stores (channelStore / channelMessageStore).
export const channelApi = {
  update: async (id: number, data: { name?: string; description?: string; document?: string }) => {
    const channel = await updateChannelConnect(orgSlug(), id, data);
    getChannelService().update_channel_local(BigInt(id), JSON.stringify(channel));
    return { channel };
  },

  archive: async (id: number) => {
    await archiveChannelConnect(orgSlug(), id);
    return { message: "ok" };
  },

  unarchive: async (id: number) => {
    await unarchiveChannelConnect(orgSlug(), id);
    return { message: "ok" };
  },

  searchMessages: async (id: number, q: string, limit = 20) => {
    const messages = await searchChannelMessagesConnect(orgSlug(), id, q, limit);
    return { messages };
  },

  getPods: async (id: number) => {
    const { pods, total } = await listChannelPodsConnect(orgSlug(), id);
    // Fan out to Rust SSOT so useChannelPods (reads channel_pods_json) sees it.
    getChannelService().set_channel_pods_local(BigInt(id), JSON.stringify(pods));
    return { pods, total };
  },

  joinPod: async (id: number, podKey: string) => {
    await joinChannelPodConnect(orgSlug(), id, podKey);
    return { message: "ok" };
  },

  leavePod: async (id: number, podKey: string) => {
    await leaveChannelPodConnect(orgSlug(), id, podKey);
    return { message: "ok" };
  },

  inviteMembers: async (id: number, userIds: number[]) => {
    await inviteChannelMembersConnect(orgSlug(), id, userIds);
    return { message: "ok" };
  },

  removeMember: async (id: number, userId: number) => {
    await removeChannelMemberConnect(orgSlug(), id, userId);
    // Mirror Rust wasm path: remove from cached members so selector re-reads it gone.
    getChannelService().remove_channel_member_local(BigInt(id), BigInt(userId));
    return { message: "ok" };
  },

  listMembers: async (id: number) => {
    const { members, total } = await listChannelMembersConnect(orgSlug(), id);
    getChannelService().set_channel_members_local(BigInt(id), JSON.stringify(members));
    return { members, total };
  },
};
