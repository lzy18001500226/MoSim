# CoAgent Transport

## Purpose

This directory owns visible-conversation transport adapters.

Dispatch code should decide what task/result packet to send. Transport code
should decide how the packet reaches a visible conversation and where the raw
adapter logs live.

## Current Adapter

| Adapter | File | Purpose |
|---|---|---|
| `codex_exec_resume` | `codex_exec.py` | Uses project-local shadow Codex state and `codex exec resume` to send a packet to an existing visible Codex thread. |

## Boundary

Adapters must not treat Codex App private storage as the durable source of
truth. CoAgent durable state remains in runtime tasks, result packets,
conversation edges, run summaries, and ignored `Results/` evidence.

The `codex_exec_resume` adapter prepares a temporary shadow Codex home under
ignored `Results/coagent_transport/`. It must copy only the target rollout file
whose `session_meta.payload.id` matches the requested `thread_id`. Do not scan
all historical rollouts for text mentions of the target id; main project
conversations often mention department ids in logs and would otherwise be
mistaken for the target conversation.

If no matching rollout exists, transport must fail before starting `codex exec
resume`. That means the visible registry and the local Codex session store are
out of sync, and the department thread needs repair before a real lifecycle can
be claimed.

Future adapters should implement the interface in `adapter.py` instead of
adding more process/session code to `CoAgent/dispatch/codex_transport.py`.
