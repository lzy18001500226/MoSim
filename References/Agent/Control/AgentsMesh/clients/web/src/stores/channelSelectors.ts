import { useMemo } from "react";
import { getChannelService } from "@/lib/wasm-core";
import { useChannelStore } from "./channelStore";
import type { Channel, ChannelLastMessage, ChannelMember } from "./channelTypes";

const svc = () => getChannelService();

export function useChannels(): Channel[] {
  const tick = useChannelStore((s) => s._tick);
  return useMemo(() => JSON.parse(svc().channels_json()) as Channel[], [tick]);
}

/** Read the cached last-message preview for a channel (from WASM `last_messages` map). */
export function getLastMessage(channelId: number): ChannelLastMessage | null {
  const raw = svc().get_last_message_json(BigInt(channelId));
  if (!raw) return null;
  try {
    return typeof raw === "string" ? (JSON.parse(raw) as ChannelLastMessage) : (raw as ChannelLastMessage);
  } catch {
    return null;
  }
}

export function useCurrentChannel(): Channel | null {
  const tick = useChannelStore((s) => s._tick);
  return useMemo(() => {
    const v = svc().current_channel_json();
    return v ? (typeof v === "string" ? JSON.parse(v) : v) : null;
  }, [tick]);
}

/** Members of a given channel. Rust ChannelService caches the list per channel
 *  in state; the hook re-reads whenever `_tick` bumps (fetch / invite / remove). */
export function useChannelMembers(channelId: number | null | undefined): ChannelMember[] {
  const tick = useChannelStore((s) => s._tick);
  return useMemo(() => {
    if (channelId == null) return [];
    try {
      return JSON.parse(svc().channel_members_json(BigInt(channelId))) as ChannelMember[];
    } catch {
      return [];
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tick, channelId]);
}

export function readChannel(id: number): Channel | null {
  const raw = svc().get_channel_json(BigInt(id));
  if (!raw) return null;
  try {
    return typeof raw === "string" ? (JSON.parse(raw) as Channel) : (raw as Channel);
  } catch {
    return null;
  }
}
