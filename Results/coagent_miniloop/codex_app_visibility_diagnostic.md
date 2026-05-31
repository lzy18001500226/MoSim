# Codex App Visibility Diagnostic

Date: 2026-05-29

Status: warning

## Finding

Codex App and VSCode/WSL Codex do not currently share a complete session index.

Observed files:

```text
/home/linux/.codex/session_index.jsonl
  lines: 200
  role: WSL / VSCode-side Codex index

C:\Users\HP\.codex\session_index.jsonl
  WSL path: /mnt/c/Users/HP/.codex/session_index.jsonl
  lines: 1
  role: Windows local Codex App index
```

Recent session files exist in both locations, but the indexes are asymmetric.
This explains why some conversations can appear in one surface while missing or
unstable in the other.

## Current Operating Decision

Do not treat Codex App / VSCode live UI sync as the durable coordination layer.

Use project-owned durable state instead:

```text
CoAgent runtime DB/events
CoAgent dispatch registry
Results/agent_packets/
Results/coagent_miniloop/
CoAgent/docs/decisions/
PROGRESS.md
CoAgent/STATUS.md
```

Codex App remains a review/front-end surface. It is useful, but not the source
of truth.

## Risk

If a new department conversation is created only in Codex App, VSCode/WSL may
not see it. If a new department conversation is created only in VSCode/WSL,
Codex App may not list it until local session files and index state line up.

## Next Proof Needed

Run a controlled UI visibility proof:

```text
1. Create one small VSCode/WSL-backed conversation.
2. Confirm whether Codex App lists it.
3. Create one small Codex App-backed conversation.
4. Confirm whether VSCode/WSL lists it.
5. Compare rollout files and session_index.jsonl deltas.
6. Decide whether to mirror indexes, avoid App-created department threads, or
   build a project-owned conversation registry independent of both UIs.
```

Do not run this proof during core implementation unless the user explicitly
wants UI debugging.
