# Adapter Layer Audit — Unsafe Casts & Method Mismatches

**Auditor:** Fenster (Core Dev)
**Requested by:** Brady
**Date:** 2026-02-22
**Scope:** `packages/squad-sdk/src/adapter/`, `packages/squad-cli/src/cli/shell/`, `packages/squad-sdk/src/client/`
**Related:** Issue #315 (CopilotSessionAdapter fix)

---

## Summary

**7 findings total: 2 P0, 3 P1, 2 P2**

The #315 fix (`CopilotSessionAdapter`) correctly maps `sendMessage()` → `send()`, `off()` → unsubscribe tracking, and `close()` → `destroy()`. However, the adapter passes event type strings straight through without mapping them, and all consumer code uses Squad-internal event names (`message_delta`, `usage`) that do not match the SDK's actual event type names (`assistant.message_delta`, `assistant.usage`). This means **streaming event handlers will silently never fire** when connected to a real `CopilotSession`.

---

## P0 — Will Crash or Silently Fail

### F1. Event type names do not match SDK event types

| | |
|---|---|
| **Files** | `adapter/client.ts:54,643-644` / `shell/index.ts:130,168` / `shell/spawn.ts:115` |
| **What code assumes** | Event type `'message_delta'` and `'usage'` are valid `CopilotSession` event types |
| **What SDK provides** | `SessionEventType` uses namespaced names: `'assistant.message_delta'`, `'assistant.usage'`, `'session.idle'`, etc. |
| **Impact** | `session.on('message_delta', handler)` registers for a type that never fires. All streaming listeners are dead. |
| **Suggested fix** | Add an event name mapping in `CopilotSessionAdapter.on()` that translates Squad event names to SDK event names (e.g. `'message_delta'` → `'assistant.message_delta'`, `'usage'` → `'assistant.usage'`). |

**Affected call sites:**

- `adapter/client.ts:643` — `origOn('message_delta', streamListener)`
- `adapter/client.ts:644` — `origOn('usage', streamListener)`
- `shell/index.ts:130` — `session.on('message_delta', onDelta)`
- `shell/index.ts:168` — `coordinatorSession.on('message_delta', onDelta)`
- `shell/spawn.ts:115` — `session.on('message_delta', onDelta)`

### F2. Event data property access does not match SDK event shape

| | |
|---|---|
| **Files** | `adapter/client.ts:633-639` / `shell/index.ts:94-97` / `shell/spawn.ts:110-113` |
| **What code assumes** | `event.type === 'message_delta'`, `event.delta`, `event.content`, `event.inputTokens`, `event.outputTokens` |
| **What SDK provides** | SDK events have structure `{ type: 'assistant.message_delta', data: { messageId, deltaContent } }` and `{ type: 'assistant.usage', data: { model, inputTokens, outputTokens } }`. Data is nested under `.data`, not top-level. |
| **Impact** | Even if F1 is fixed, handlers read wrong properties. `extractDelta()` returns `''`, token counts always `0`. |
| **Suggested fix** | Update `CopilotSessionAdapter.on()` to unwrap the SDK event shape into the Squad event shape before calling the handler, mapping `event.data.deltaContent` → `event.delta` and `event.data.inputTokens` → `event.inputTokens`. |

**Specific mismatches in `adapter/client.ts:633-639`:**

```
// Code reads:
event.type === 'message_delta'       // SDK sends: 'assistant.message_delta'
(event as any).inputTokens           // SDK nests: event.data.inputTokens
(event as any).outputTokens          // SDK nests: event.data.outputTokens
```

**Specific mismatches in `shell/index.ts:94-97` (`extractDelta`):**

```
// Code reads:
event['delta'] ?? event['content']   // SDK sends: event.data.deltaContent
```

---

## P1 — Will Malfunction

### F3. `listSessions()` uses `as unknown as SquadSessionMetadata[]` — no runtime validation

| | |
|---|---|
| **File** | `adapter/client.ts:458` |
| **What code assumes** | `CopilotClient.listSessions()` returns objects matching `SquadSessionMetadata` shape |
| **What SDK provides** | `SessionMetadata` with `context?: SessionContext` (structured type with `cwd`, `gitRoot`, `repository`, `branch`) |
| **Risk** | Squad types `context` as `Record<string, unknown>`, losing access to structured fields. If the SDK ever adds/removes fields, the cast silently breaks. |
| **Suggested fix** | Map through results and construct `SquadSessionMetadata` objects explicitly, similar to how `CopilotSessionAdapter` wraps sessions. |

### F4. `SquadClient.on()` casts event types and handlers to `any`

| | |
|---|---|
| **File** | `adapter/client.ts:703-705` |
| **What code assumes** | `SquadSessionEventType` (string) maps to `CopilotClient.on()` event types |
| **What SDK provides** | `CopilotClient.on()` accepts `SessionLifecycleEventType` which is `'session.created' | 'session.deleted' | 'session.updated' | 'session.foreground' | 'session.background'` |
| **Impact** | Passing Squad event types that aren't lifecycle events silently registers handlers that never fire. Handler signature also mismatches. |
| **Suggested fix** | Restrict `SquadClient.on()` to accept only lifecycle event types, or add a mapping layer like the session adapter. |

### F5. `SquadClient.sendMessage()` subscribes to adapter events using wrong names

| | |
|---|---|
| **File** | `adapter/client.ts:628-644` |
| **What code assumes** | Can call `session.on('message_delta', ...)` and `session.on('usage', ...)` to track stream telemetry |
| **What actually happens** | Goes through `CopilotSessionAdapter.on()` which passes `'message_delta'` to the SDK — handler never fires (see F1) |
| **Impact** | OTel stream spans never record `first_token`, `last_token`, or token counts. Telemetry shows 0 input/output tokens for all messages. |
| **Suggested fix** | Same root cause as F1 — fix the event name mapping in the adapter. |

---

## P2 — Code Smell

### F6. Dead reference to `_squadOnMessage`

| | |
|---|---|
| **File** | `adapter/client.ts:628` |
| **Code** | `const prevOnMessage = (session as any)._squadOnMessage;` |
| **Issue** | `_squadOnMessage` does not exist on `SquadSession` or `CopilotSessionAdapter`. The variable is assigned but never used. |
| **Suggested fix** | Delete the dead line. |

### F7. `SquadClientWithPool.on()` is fully untyped

| | |
|---|---|
| **File** | `client/index.ts:209` |
| **Code** | `on(eventType: any, handler: any)` |
| **Issue** | Accepts any event type and any handler with no type checking. Bypasses the type safety that `SquadClient.on()` provides. |
| **Suggested fix** | Match the overload signatures from `SquadClient.on()`. |

---

## Items Verified as Correct

| Item | Status |
|---|---|
| `resumeSession()` wraps result in `CopilotSessionAdapter` | Correct (`client.ts:429`) |
| `createSession()` wraps result in `CopilotSessionAdapter` | Correct (`client.ts:385`) |
| `CopilotSessionAdapter.sendMessage()` maps to `send()` | Correct (`client.ts:49-51`) |
| `CopilotSessionAdapter.close()` maps to `destroy()` | Correct (`client.ts:66-69`) |
| `CopilotSessionAdapter.off()` calls stored unsubscribe function | Correct (`client.ts:58-64`) |
| `session.sessionId` property exists on `CopilotSession` | Correct (`session.d.ts:38`) |
| `SquadSessionConfig` structurally matches SDK `SessionConfig` | Correct (compatible field names and types) |
| Shell cleanup calls `session.close()` through adapter | Correct (`shell/index.ts:246-254`) |

---

## Root Cause Analysis

The #315 fix addressed the **method** mapping (`send`/`sendMessage`, `destroy`/`close`) but did not address **event type** or **event shape** mapping. The adapter currently does:

```
// What the adapter does now (client.ts:54):
on(eventType, handler) {
    const unsubscribe = this.inner.on(eventType, handler);  // passes through as-is
}
```

It needs to:
1. Map event type names: `'message_delta'` → `'assistant.message_delta'`
2. Unwrap event data: `{ type, data: { deltaContent } }` → `{ type: 'message_delta', delta: deltaContent }`

This is the same class of bug as #315 — the adapter provides a type-level facade without runtime behavior adaptation.

---

## Recommended Fix Priority

1. **F1 + F2 + F5** — Single fix: Add event name mapping + event shape unwrapping in `CopilotSessionAdapter.on()`. This restores streaming and telemetry.
2. **F3** — Replace `as unknown as` cast with explicit mapping function.
3. **F4** — Restrict `SquadClient.on()` types or add lifecycle event mapping.
4. **F6 + F7** — Cleanup (can batch with any PR).
