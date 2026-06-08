# [Codex Desktop Windows] Long-lived multi-thread workspace develops dead-thread and submit failures

**Date:** 2026-06-08
**Severity:** High
**Reproducibility:** Intermittent but frequent in one long-lived Windows workspace

## Summary

In a long-lived Windows-native Codex Desktop workspace with many visible project threads, large transcripts, frequent cross-thread dispatches, and recurring automations, individual threads can remain listable/readable while new turns fail to start or settings updates fail with `agent loop died unexpectedly`.

This is not reproduced by creating an empty thread and sending `hello`. Empty/new threads can submit simple messages. The issue appears after the project accumulates long conversation history, many visible threads, context compaction events, interrupted turns, and app-server / renderer state.

Observed workaround: restarting Codex Desktop or Codex++ often temporarily restores the affected visible thread, but failures recur.

## Expected Behavior

1. A visible, listable, readable thread should either accept a new turn or expose a clear non-routable state such as approval pending, compaction pending, stale runtime, or agent-loop failure.
2. Composer submit and native thread dispatch should not fail because stale thread/runtime state survived after earlier turns completed.
3. Completed turns should not resume as streaming or keep queued follow-ups blocked.
4. Context compaction progress/failure should not leave future `turn/start` or `turn/steer` unreliable.
5. App-server / renderer / helper processes should be cleaned up or reused predictably when switching many threads in one workspace.

## Actual Behavior

The affected workspace intermittently shows:

- `Error submitting message`
- `failed to start turn: internal error; agent loop died unexpectedly`
- `failed to update thread settings: internal error; agent loop died unexpectedly`
- visible threads that are readable but cannot reliably start a new turn
- threads classified by the app/tool surface as `notLoaded` while historical turns are readable
- permission/review states such as `waitingOnApproval` that can be confused with dead-thread stalls unless separately inspected
- restart/reopen temporarily restoring the same thread
- large transcript and diagnostic history, with compaction and `markedStreaming=true` evidence in logs

## Environment

| Detail | Value |
|---|---|
| App | Codex Desktop, Windows-native |
| App package observed | `OpenAI.Codex_26.602.4764.0_x64` |
| Desktop executable product version | `149.0.7827.54` |
| OS | Windows 11 Pro Workstation, version `10.0.26200`, x64 |
| Workspace | Windows-native project, not WSL |
| Model profile commonly used | `gpt-5.5`, `xhigh` / high reasoning |
| Negative control | Empty/new threads can submit a simple message; the issue appears in the long-lived multi-thread workspace |

## Reproduction Pattern

1. Use Codex Desktop on Windows in one project workspace for multiple days.
2. Keep a long main orchestration thread and many visible department threads in the same workspace.
3. Accumulate large transcripts, compaction events, interrupted turns, and cross-thread dispatches.
4. Use native thread surfaces to inspect and dispatch: list/read a target visible thread, then send a follow-up prompt, sometimes with model/settings override.
5. Observe that some target threads remain readable/listable, but the follow-up fails at settings update or turn start:

```text
failed to update thread settings: internal error; agent loop died unexpectedly
failed to start turn: internal error; agent loop died unexpectedly
Error submitting message
```

6. Restart Codex Desktop/Codex++.
7. Observe that the same visible thread often becomes able to receive a no-op or expected packet again, implying this is not a permanent business-task error.

## Evidence Summary

Read-only diagnostics found the following scale indicators:

| Metric | Value |
|---|---:|
| Total thread records | 144 |
| Main project thread records | 120 |
| Unarchived main project thread records | 117 |
| Thread spawn edges | 120 |
| Persisted agent jobs | 0 |
| Largest orchestration transcript | about 532 MB |
| Operations/patrol transcript | about 173 MB |
| Diagnostic event rows | 219,140 |
| Diagnostic history size | about 701 MB |
| Codex Desktop Electron processes | 8 |
| Stdio app-server processes | 6 |
| Node helper / MCP / REPL process groups | multiple |

The heaviest orchestration threads contain many occurrences of `contextCompaction`, `agent loop died unexpectedly`, `Error submitting message`, and `waitingOnApproval`. These are string occurrences, not deduplicated incident counts.

Representative state/log patterns:

```text
maybe_resume_success conversationId=<redacted> latestTurnStatus=completed markedStreaming=true
Item not found in turn state itemId=<redacted>
Conversation state not found
responses/compact
contextCompaction
waitingOnApproval
```

## Similar Public Issues

| Public Issue | Similarity | Difference / Notes |
|---|---|---|
| [#23971: subagent close request triggers `agent loop died unexpectedly` and repeated submit failures](https://github.com/openai/codex/issues/23971) | Same key error string and repeated `Error submitting message`; involves subagent/visible-thread lifecycle. | Reported on macOS and triggered by subagent close; this report is Windows and long-lived multi-thread dispatch. |
| [#23644: composer submit times out after stale conversation state accumulates; restart clears it](https://github.com/openai/codex/issues/23644) | Very similar stale state + restart clears pattern; points at app-server / MCP route rather than upstream model failure. | Reported on macOS; this report has Windows-native desktop, many visible threads, and very large transcripts. |
| [#19951: stuck after Error submitting prompt/message; delayed duplicate prompts became steered and Stop did not work](https://github.com/openai/codex/issues/19951) | Related composer submit / queued or steered prompt inconsistency. | Their surface includes duplicate prompts and Stop failure; here the recurring issue is visible thread dispatch/start-turn failure. |
| [#14070: Codex App for Windows crash, lags, error for new tasks in running threads after restart](https://github.com/openai/codex/issues/14070) | Same Windows Desktop class: thread switching lag and errors creating new tasks in existing threads. | This report adds thread counts, session sizes, and diagnostic counters. |
| [#11090: UI freezes, worker crashes, orphaned app-server processes](https://github.com/openai/codex/issues/11090) | Related app-server/worker crash and orphaned process pattern; same `agent loop died unexpectedly` class. | Reported on macOS and includes git/worktree errors; here evidence points more at thread/conversation state, compaction, and dispatch surface. |
| [#13659: compaction progress state not clearing in Windows app](https://github.com/openai/codex/issues/13659) | Same platform family and compaction lifecycle state risk. | This report does not prove compaction is the sole cause, but large transcripts and compaction markers are present. |
| [#24467: long gpt-5.5/xhigh threads remain spinning after compaction/interruption](https://github.com/openai/codex/issues/24467) | Very similar long-thread lifecycle symptom: older threads are less reliable than fresh threads, compaction markers appear nearby, and `completed` / `interrupted` turns can resume with `markedStreaming=true`. | Reported on macOS and focused on visible spinner/no-output; this report focuses on Windows visible-thread dispatch/start-turn failure. |
| [#19563: Desktop resume/unsubscribe loop with more than four target-thread heartbeat automations](https://github.com/openai/codex/issues/19563) | Highly relevant to recurring automation plus visible-thread orchestration: target-thread automations can trigger repeated resume/unsubscribe cycles and `completed markedStreaming=true` state. | The clean repro there used five tiny heartbeat targets; this report has fewer active automations now but much larger long-lived threads and many historical department threads. |
| [#20517: Windows heartbeat automation resume path mismatch with extended-length paths](https://github.com/openai/codex/issues/20517) | Relevant Windows automation/session-management issue; this workspace also has both normal and extended-length path records for the same project root. | This report has not proven path normalization is the main trigger; it is listed as a related Windows resume/heartbeat failure mode. |
| [#22996: completed Windows Desktop threads become inaccessible after update](https://github.com/openai/codex/issues/22996) | Related Windows session/resume-state issue; includes normal Windows path vs extended-length path mismatch and completed local threads becoming inaccessible. | This report still has readable historical turns; the failure is mainly new-turn routing/settings/start, not only sidebar access. |
| [#26413: queued follow-ups stop processing after completed turn resumes as `markedStreaming=true`](https://github.com/openai/codex/issues/26413) | Highly relevant state inconsistency: completed turn restored as streaming, queued follow-ups stall. | Reported in VS Code extension; this report is Codex Desktop, but `markedStreaming=true` appears in local logs. |
| [#19249: Windows Desktop slash/local skill submission hangs, errors, duplicates after GPT-5.5 update](https://github.com/openai/codex/issues/19249) | Same Windows + `Error submitting message` / GPT-5.5 era submission instability. | The current report is not focused on slash/local skills; plain/cross-thread dispatch can fail after state buildup. |

## Current Assessment

Most likely category: **thread/conversation state and app-server/renderer lifecycle degradation in long-lived multi-thread Windows workspaces**, possibly involving compaction and completed-turn streaming state.

This does not look primarily like:

- global network outage, because new/empty threads can submit simple messages
- login/account failure, because some threads continue to run and restart restores affected threads
- project business-code error, because failures happen before the business task starts
- a persisted agent job backlog, because persisted agent job counts are zero
- only a permission prompt issue, because permission states such as `waitingOnApproval` exist separately and must be classified before dead-thread recovery

Likely involved layers:

1. App-server `turn/start` / `turn/steer` lifecycle
2. Thread/conversation state recovery after many turns and compactions
3. Completed turn restored as streaming (`markedStreaming=true`)
4. Renderer/UI composer submit queue or stale request routing
5. Multiple visible threads / subagent spawn edges in one project
6. Windows Desktop app reopen / thread switch lifecycle

## Open Questions for Maintainers

1. Is there a known threshold where session size, `contextCompaction` history, or visible-thread count degrades turn start in Codex Desktop?
2. Can a thread be readable but internally unroutable for `turn/start`? If so, can the thread API expose this as a state distinct from readable/listable?
3. What does `latestTurnStatus=completed markedStreaming=true` imply in Desktop? Can it block queued follow-ups or new starts?
4. Are multiple stdio app-server instances expected in a long-running Desktop workspace with plugins/MCP/node_repl, or can they become stale/orphaned?
5. Can compaction failures or `responses/compact` leave conversation state inconsistent, causing later `Conversation state not found` or `Item not found in turn state`?
6. Should approval/review states such as `waitingOnApproval` be surfaced in a way that automation can distinguish them from dead-thread / agent-loop failure?
7. Are there recommended diagnostics to export a sanitized thread/runtime state bundle without manually reading private state/log files?

## Workarounds Tried

- Restarting Codex Desktop/Codex++: usually restores the same visible thread temporarily.
- Bounded no-op validation after restart: can confirm thread execution surface restored.
- Avoiding empty-thread `hello` tests: those pass and do not reproduce the long-lived workspace failure.
- Separating `waitingOnApproval` / approval UI from true dead-thread recovery: reduces false restarts but does not solve real `agent loop died unexpectedly` failures.

## Data Collection Limitations

- The current investigation did not run a controlled 3-pass latency test in the active long orchestration thread because that would require injecting additional turns into the already affected thread while this investigation was running.
- Keyword counts are not unique incidents; they include logs/transcripts that may mention earlier failures.
- No private state was reset, cleaned, or modified during evidence collection.
- Sensitive local paths/usernames are redacted before public posting.
