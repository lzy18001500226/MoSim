// channelMessageWasmProjection — boundary projection between the Web view-model
// `ChannelMessage` (parsed `content: MessageContent` AST) and the wasm Rust
// core's cache row shape `proto_channel_state_v1::ChannelMessage` (opaque
// `content_json: Option<String>`).
//
// This is **not** a Phase 5-era REST DTO adapter. The Phase 5 deletion swept
// the `*-types.ts` files that re-shaped REST JSON envelopes into business
// types — those went away when Connect started returning proto-derived types
// directly. This projection lives on by design: Rust core stores channel
// messages in the SSOT cache with opaque rich-AST blobs so the wire/cache
// contract stays stable across renderer revisions of the BlockNote AST. The
// renderer parses them at the boundary; wasm never sees `MessageContent`.
//
// Naming history: previously `channelMessageWasmAdapter.ts` / `toWasmMessage`
// — renamed to "Projection" so a casual reader doesn't conflate this with the
// deleted REST adapters (see ADR 2026-05-24-phase5-adapter-removal.md).

import type { ChannelMessage } from "@/lib/api/facade/channel";
import type { MessageContent, MessageMentions } from "@/lib/viewModels/channelMessage";

export type WasmChannelMessage = Omit<ChannelMessage, "content" | "mentions"> & {
  content_json?: string;
  mentions_json?: string;
};

type WithRichAst = {
  content?: MessageContent;
  mentions?: MessageMentions;
};

// Generic over the input — full ChannelMessage from server flows, or a
// partial diff payload from local-state updates both project the same way.
export function toWasmProjection<T extends WithRichAst>(
  m: T,
): Omit<T, "content" | "mentions"> & { content_json?: string; mentions_json?: string } {
  const { content, mentions, ...rest } = m;
  const out = { ...rest } as Omit<T, "content" | "mentions"> & {
    content_json?: string;
    mentions_json?: string;
  };
  if (content) out.content_json = JSON.stringify(content);
  if (mentions) out.mentions_json = JSON.stringify(mentions);
  return out;
}

export function fromWasmProjection(m: WasmChannelMessage): ChannelMessage {
  const { content_json, mentions_json, ...rest } = m;
  const out: ChannelMessage = { ...rest } as ChannelMessage;
  if (content_json) {
    try { out.content = JSON.parse(content_json) as MessageContent; } catch { /* ignore */ }
  }
  if (mentions_json) {
    try { out.mentions = JSON.parse(mentions_json) as MessageMentions; } catch { /* ignore */ }
  }
  return out;
}
