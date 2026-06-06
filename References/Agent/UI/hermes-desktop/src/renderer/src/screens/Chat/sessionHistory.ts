import type { Attachment } from "../../../../shared/attachments";
import type { ChatMessage, ChatBubbleMessage } from "./types";

/**
 * Shape of one row from the main process's `getSessionMessages` IPC.
 * Mirrors `src/main/sessions.ts:HistoryItem` (kept loose here so the
 * renderer doesn't have to import main-process types).
 */
export interface DbHistoryItem {
  kind: "user" | "assistant" | "reasoning" | "tool_call" | "tool_result";
  id: number;
  content?: string;
  text?: string;
  callId?: string;
  name?: string;
  args?: string;
  timestamp?: number;
  attachments?: Attachment[];
}

/**
 * Convert a stream of `getSessionMessages` rows into renderer-ready
 * `ChatMessage`s. Extracted from `Layout.handleResumeSession` so both
 * "resume a saved session from the Sessions tab" and "refresh the
 * active chat's transcript from state.db at end of stream" can share
 * the same mapping.
 *
 * The end-of-stream refresh is the desktop's user-side mitigation for
 * NousResearch/hermes-agent#30449 ("API server: reasoning_content and
 * reasoning_effort never reach OpenAI-compatible SSE stream"). Until
 * the gateway forwards reasoning chunks during the stream, the agent
 * still writes them to state.db at finalisation — refreshing here
 * makes them appear without the user having to focus-change to
 * trigger a re-sync (issue #352).
 */
export function dbItemsToChatMessages(
  items: ReadonlyArray<DbHistoryItem>,
): ChatMessage[] {
  return items
    .map((it): ChatMessage | null => {
      switch (it.kind) {
        case "user":
          return {
            id: `db-${it.id}`,
            role: "user",
            content: it.content || "",
            ...(it.attachments && it.attachments.length > 0
              ? { attachments: it.attachments }
              : {}),
          };
        case "assistant":
          return {
            id: `db-${it.id}`,
            role: "agent",
            content: it.content || "",
            ...(it.attachments && it.attachments.length > 0
              ? { attachments: it.attachments }
              : {}),
          };
        case "reasoning":
          return {
            id: `db-r-${it.id}`,
            kind: "reasoning",
            role: "agent",
            text: it.text || "",
          };
        case "tool_call":
          return {
            id: `db-tc-${it.id}-${it.callId || "x"}`,
            kind: "tool_call",
            role: "agent",
            callId: it.callId || "",
            name: it.name || "",
            args: it.args || "",
          };
        case "tool_result":
          return {
            id: `db-tr-${it.id}`,
            kind: "tool_result",
            role: "agent",
            callId: it.callId || "",
            name: it.name || "",
            content: it.content || "",
            ...(it.attachments && it.attachments.length > 0
              ? { attachments: it.attachments }
              : {}),
          };
        default:
          return null;
      }
    })
    .filter((m): m is ChatMessage => m !== null);
}

/**
 * Match key for cross-source reconciliation between streamed in-memory
 * messages and DB-loaded equivalents. Returned key matches when two
 * messages represent the same logical row regardless of which side
 * produced them.
 *
 * The strategy:
 *
 *   - For the chat-bubble kinds (user / agent content) we key on
 *     `role:contentSnippet`. Trimming guards against trailing
 *     whitespace drift between the stream-accumulated string and the
 *     DB-finalised one. The snippet length is intentionally short
 *     (first 200 chars) so a very long assistant reply doesn't blow
 *     out the map for no incremental matching benefit — collisions
 *     across two distinct turns at the same prefix are vanishingly
 *     unlikely.
 *   - For `tool_call` / `tool_result` we key on the OpenAI callId,
 *     which the agent generates and is stable across the streamed
 *     callback (when one exists) and the DB row.
 *   - For `reasoning`, key on the trimmed text. Reasoning has no
 *     callId. When streaming concatenates many tiny tokens into one
 *     reasoning message, the result text equals the DB row text
 *     because both sides see the same agent output.
 *
 * `null` opts a message out of matching — there's no equivalent on
 * the other side and the reconciliation should treat it as unique.
 */
function reconciliationKey(m: ChatMessage): string | null {
  if ("kind" in m) {
    switch (m.kind) {
      case "reasoning":
        return `reasoning:${(m.text || "").trim().slice(0, 200)}`;
      case "tool_call":
        return `tool_call:${m.callId || m.id}`;
      case "tool_result":
        return `tool_result:${m.callId || m.id}`;
      default:
        return null;
    }
  }
  const bubble = m as ChatBubbleMessage;
  return `${bubble.role}:${(bubble.content || "").trim().slice(0, 200)}`;
}

/**
 * Merge an in-memory streamed transcript with the canonical state.db
 * transcript at end-of-stream.
 *
 * The desktop streams `user` + `agent content` in real time (and, once
 * `NousResearch/hermes-agent#30449` lands, `reasoning` too). `tool_call`
 * and `tool_result` rows never stream — they only exist in `state.db`
 * after the agent finalises the message. So at end-of-stream we need
 * to surface the DB rows the streaming pass didn't deliver.
 *
 * The naive approach — replace the whole transcript with the DB version
 * — works today but will cause a one-frame re-mount flicker once
 * reasoning streaming starts working: the streamed reasoning bubble
 * (id `reasoning-${ts}`) would be replaced by a DB-loaded one (id
 * `db-r-${row}`) with identical text but a new React key. Solving it
 * properly: walk the DB rows in their canonical order, but when a
 * streamed equivalent already exists in memory, keep the streamed
 * row's React identity. New DB rows that have no streamed counterpart
 * (tool_call / tool_result today, plus any agent-finalised text the
 * stream dropped) appear in the merged result in the DB's order.
 *
 * Issue #352. Pure function, no state — testable in isolation.
 */
export function reconcileStreamedWithDb(
  streamed: ReadonlyArray<ChatMessage>,
  db: ReadonlyArray<ChatMessage>,
): ChatMessage[] {
  // Index streamed messages by their reconciliation key. Duplicate
  // keys (same text in two turns) are tracked as a FIFO queue so the
  // walk below consumes them in the original order rather than
  // collapsing both DB occurrences onto the first streamed one.
  const streamedByKey = new Map<string, ChatMessage[]>();
  for (const m of streamed) {
    const key = reconciliationKey(m);
    if (!key) continue;
    const bucket = streamedByKey.get(key);
    if (bucket) bucket.push(m);
    else streamedByKey.set(key, [m]);
  }

  const result: ChatMessage[] = [];
  for (const dbMsg of db) {
    const key = reconciliationKey(dbMsg);
    const bucket = key ? streamedByKey.get(key) : undefined;
    const streamedMatch = bucket?.shift();
    result.push(streamedMatch ?? dbMsg);
  }

  // Pathological case: the in-memory transcript carried something the
  // DB doesn't have yet (e.g. a renderer-side error bubble inserted by
  // `onChatError`). Preserve those tail-of-stream additions so the
  // reconciliation never silently drops UI-only state.
  const consumedIds = new Set(result.map((m) => m.id));
  for (const m of streamed) {
    if (!consumedIds.has(m.id)) result.push(m);
  }

  return result;
}
