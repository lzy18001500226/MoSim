# CoAgent Meta-Maintenance Checklist

> Purpose: keep MoSim visible-thread registry, CoAgent/native Codex capability
> adoption, workflow/skill/index health, archived gateway-route records, and recurring
> meta-operation records clean without creating extra standing departments.

Status: current operating workflow, 2026-06-06 CST.

2026-06-07 context-compression surface hotfix: if a CoAgentOps or department
thread appears stalled and the Codex App UI shows a context-compression surface
issue, such as `Context Left 100.0%` plus slash-command compression requiring
manual recovery, do not skip directly to replacement or Codex++ restart. Record
`codex_context_compression_surface`, send a sparse Chinese notification, and
let the user perform the confirmed manual workaround: switch to `gpt-5.4` with
`xhigh`, type `/`, run compression, then switch back to `gpt-5.5` with
`xhigh`. After the user reports the UI is fixed, perform the normal bounded
no-op/packet validation before declaring the thread routable.

2026-06-07 email-default notification hotfix: WeChat outbound can lose usable
send context after several hours, so MoSim user notifications now default to
sparse Chinese email. Any planned Codex++ restart for a dead-thread incident
and any MWORKS/Sysplorer/Syslab activation, login, license, authorization,
hidden-login-pane, or GUI-error incident must first write the recovery/blocker
packet, attempt one sparse Chinese email notification, and record the audit.
WeChat is not a routine progress, completion, human-intervention, or
restart-notice channel; use it only for explicit WeChat gateway diagnosis, a
user-requested WeChat retry, or a current task that specifically validates the
WeChat gateway. The notification is a handoff window, not an approval wait: if
the user is online, the user may restart Codex++ manually faster; otherwise,
after the email attempt is recorded, the still-healthy mainline continues the
authorized restart route unless PMO/user explicitly defers the incident.

2026-06-07 WeChat gateway retirement hotfix: the user archived
`MoSim｜微信网关运维部` (`019e9c7d-a8bd-7dd1-ad94-6feef5a07e9c`) and MoSim
notifications are email-only by default. CoAgentOps and PMO no longer perform
periodic WeChat gateway self-checks, no-op probes, canaries, or ret=-2 recovery.
The archived gateway thread and `MoSim｜WechatCodex` are not active-visible
routes. Use them only as historical evidence or after an explicit future user
request to restore WeChat gateway diagnosis.

2026-06-07 MWORKS activation evidence hotfix: CoAgentOps MWORKS activation/
window patrol must use maximized or foreground visual evidence of the target
reusable MWORKS/Sysplorer/Syslab main window for activation, login, license,
authorization, or hidden-login-pane claims. The screenshot content must show
that target window. Sentinel JSON, MCP health, process/window-title scans, and
background `PrintWindow` captures are auxiliary only; a capture that shows
Codex App, another application, a hidden helper/proxy window, or an incomplete
background surface is not valid activation recovery evidence. If target-window
content match is not proven, keep the patrol state unknown/blocked and do not
restore live MWORKS routing.

2026-06-07 model-effort default: future MoSim mainline, visible department,
automation, and disposable sub-agent dispatch should request `gpt-5.5` with
`xhigh` thinking whenever the current native tool/runtime accepts explicit
settings. Do not send health no-ops only to mutate existing thread settings.

2026-06-07 dispatch-surface ownership hotfix: after PMO observes that a visible
department is listable/readable but cannot accept a new turn, CoAgentOps owns
bounded diagnosis/recovery. PMO only writes the initial blocker and routes the
incident here; it must not keep using the broken department as an accident
sample or run further diagnosis there before CoAgentOps classification.

2026-06-07 heartbeat fail-close hotfix: an open P0 dead-thread recovery packet
with pending notifications, pending restart, pending post-restart validation,
or `still_quarantined` status blocks normal heartbeat completion. The heartbeat
must execute the next authorized recovery step. For notification/restart
pending visible-thread death, it must attempt sparse email, record the audit,
allow only a short manual-restart window, and trigger the
authorized Codex++ restart route if no explicit deferral arrives. It may write a
blocker/request and return `NOTIFY` only if a required tool/surface is missing,
the notification/restart action fails, or PMO/user explicitly deferred the
incident; it must not report `DONT_NOTIFY`, must not classify the patrol as
healthy, and must not run P1 meta-optimization until the P0 recovery is closed
or explicitly deferred by PMO/user.

2026-06-07 completed-without-response hotfix: do not classify a visible thread
as healthy from native list/read/send success alone. Recovery validation needs
an agent final reply, exact no-op reply text, or the expected return/blocker
packet. A thread turn that stays `inProgress` past the bounded validation
window, or is marked `completed` with only the user prompt and no agent
response, remains quarantined and must not receive production routing.

## 1. Scope

`MoSim｜CoAgent运维平台`
(`019e9bc1-ea9f-7102-b41a-4ef9b2308992`) owns this checklist. It is a
Codex App native meta-operations owner and a user-approved mainline operations
thread for visible-thread lifecycle and Codex App automation management. It is
not the engineering roadmap owner. The earlier `MoSim｜CoAgent运维平台`
(`019e74d1-72fa-7d33-8783-90584035ae92`) was created through an older
WSL/non-App-native path, was not reliable for native thread or automation
tools, and was deleted by the user on 2026-06-06. It must not be used for
future tasks; recover only from project docs and result/blocker packets.

Current rule:

```text
dispatchable thread set = current user-confirmed visible registry allowlist
registry source = CoAgent/dispatch/department_threads.json
title source = Docs/Index/codex_app_session_research.md current visible thread registry
ordinary engineering routing owner = MoSim｜主线 PMO
approved mainline operations owner = MoSim｜CoAgent运维平台
```

`MoSim｜CoAgent运维平台` may create, fork, rename, archive, read, and dispatch
visible Codex department threads when the native thread tools are exposed in
its current Codex session. It may also create, update, view, and delete Codex
App automations when the native `automation_update` tool is exposed. It must
not use short-lived sub-agents as a substitute for visible-thread delivery, and
must not click the Codex App GUI or edit private App state when the native
automation/thread tools are unavailable.

Automation cadence rule: after the user deletes or resets App automations,
do not recreate schedules from old assumptions. Ask for or use an explicit
current user/PMO cadence confirmation before creating each recurring task. Once
confirmed, use native `automation_update`; record the automation id, cadence,
owner, and evidence in the relevant result packet or this workflow.

Current CoAgentOps recovery uses a dual-mainline cross-check. The thread
heartbeat is useful only while the CoAgentOps visible thread can accept turns,
so it must stay attached to the CoAgentOps conversation for ordinary
maintenance. It is not self-dead protection. PMO and CoAgentOps each run their
own mainline maintenance heartbeat and monitor the other mainline. If one
mainline cannot start turns, the still-healthy mainline writes a blocker,
attempts sparse email notification before restart, gives the user a short
chance to restart manually, uses the
authorized Codex++ restart route when needed, and validates the affected thread
with one post-restart no-op. If both mainlines or
the whole Codex App are dead, the user
manually restarts Codex++; do not add an external automatic watchdog by default.

Native heartbeat automation `mosim-wechat-gateway-hourly-health` is retained
only as a historical automation id for the 30-minute CoAgentOps-thread
maintenance task; its user-facing name is `MoSim CoAgentOps 30分钟状态自检`
and it points at thread
`019e9bc1-ea9f-7102-b41a-4ef9b2308992`. Detached cron automation
`mosim-coagentops` and Windows scheduled task
`MoSim-CoAgentOps-OuterWatchdog` were removed after user review because they
created a separate automation context, risked project conversation pollution,
and could restart Codex++ from indirect stale-process heuristics. Keep
`Scripts/agent/codex_outer_watchdog.ps1` only as a manually authorized
emergency helper; it is not a scheduled or automatic recovery surface.

The CoAgentOps heartbeat must not only consume already-written recovery
packets. It also performs a light active-visible thread scan from
`CoAgent/dispatch/department_threads.json`: list/read all current
`active_visible` departments, then send at most one minimal no-op only to
threads with current evidence of dispatch-surface risk, such as recent
start-turn blockers, abnormal read status, mismatched long in-progress state,
or explicit PMO/user revalidation need. If this bounded probe confirms
`failed to start turn`, `failed to update thread settings`, or
`agent loop died unexpectedly`, the heartbeat writes a recovery packet, pauses
production routing for that target, sends a sparse email alert, records the
audit, gives the user only a brief manual-restart window, and
triggers the authorized Codex++ restart route if no explicit deferral arrives. The
restart terminates the current conversation, so PMO notification and target
no-op validation occur on the next PMO/CoAgentOps heartbeat: read the recovery
packet, run one no-op, classify `restored` / `partial_recovery` /
`still_quarantined`, and notify the PMO thread whether business routing may
resume.

Heartbeat fail-close rule: this automation is not allowed to record an open
P0 dead-thread recovery as a normal pending item. Before writing a healthy
return packet, returning `DONT_NOTIFY`, or starting P1, it must check latest
dead-thread recovery packets under `Results/agent_packets/returns/` and
`Results/agent_packets/blockers/`. If any relevant packet still requires
notification, Codex++ restart, post-restart validation, or remains
`still_quarantined`, the heartbeat must continue that recovery if authorized:
send the required sparse email alert, record the audit, trigger
the authorized Codex++ restart route after a short manual-restart window, and
leave post-restart validation for the next heartbeat. It may write a blocker/request packet with `NOTIFY` only if the
required native/tool surface is unavailable, notification/restart fails, or an
explicit PMO/user-approved deferral packet suppresses the P0 escalation.

PMO worktree handoff rule: current user decision is to not move PMO/R1/R2 to a
Codex worktree by default. On 2026-06-07, native `handoff_thread` for the PMO
mainline hung twice and partially created detached, unlinked Codex worktrees;
the user then cancelled the worktree route and CoAgentOps removed the clean
residual worktrees. If native `handoff_thread` for an existing mainline thread
hangs or only creates a detached Codex worktree without linking the target
conversation, stop after one bounded retry and write a blocker. Do not keep
retrying the same handoff surface, do not edit Codex App private state, and do
not treat an unlinked worktree directory as proof that the conversation has
moved. Reintroduce a PMO or department worktree only after a new explicit user
approval for a concrete isolated write task, then verify the new thread with
`read_thread` and a no-op before updating routing.

Do not make a specialist department's own heartbeat the only monitor for that
department: if the target thread is half-dead, its heartbeat or start-turn path
may fail too. The safe pattern is priority plus fallback:

```text
1. CoAgentOps 30-minute heartbeat wakes the CoAgentOps visible conversation.
2. It scans only current `active_visible` departments and explicit recovery
   validation targets; archived WeChat gateway routes are excluded.
3. If the specialist thread can receive work, dispatch or record normal owner
   health.
4. If the specialist thread is readable/listable but cannot start turns, write
   a dispatch-surface blocker and let CoAgentOps temporarily own only the
   urgent recovery/notification work.
5. Do not create a replacement by default. After the bounded recovery ladder is
   recorded, notify the user if possible, then use the authorized Codex++
   restart route. Replacement requires explicit PMO/user approval, repeated
   failed restart recovery, or a critical path that cannot wait.
```

Self-dead limitation: a visible thread cannot recover itself after its own
start-turn surface has already failed. If `MoSim｜CoAgent运维平台` cannot start a
turn, it cannot send email, click restart, update packets, or run validation
from inside that same dead turn. A heartbeat targeted at the same CoAgentOps
thread is therefore part of normal maintenance, not the self-rescue mechanism.
The recovery owner must be the other still-healthy mainline thread. Therefore
the two mainline heartbeats should cross-check each other: CoAgentOps checks
Gateway/specialist owners first and checks PMO reachability when needed; PMO
checks CoAgentOps reachability before relying on CoAgentOps for restart or
notification work. A detached cron or Windows scheduled task must not be used as
the default automatic recovery layer. The retained script may be run only after
explicit PMO/user authorization for a concrete incident.

If an old thread ID is absent from the current visible registry and cannot be
found in a current visibility scan, treat it as gone. Do not keep a persistent
blacklist just to remember deleted IDs. Do not resume, restore, archive, or
dispatch to absent old IDs unless the user explicitly asks for a historical
forensics task.

If a visible department is a suspected dead thread, meaning it can be listed or
read but cannot reliably receive messages, run the agent loop, expose native
thread/automation tools, or execute scheduled wakeups, do not keep dispatching
there and do not edit Codex App private state to repair it. Record the observed
failure, treat the root cause as unknown unless current evidence proves it, and
run the bounded recovery ladder before replacement: current title/list/read,
one minimal no-op start-turn probe without model override, one low-risk metadata
sync if the management surface is writable, and one final no-op start-turn
probe. If user-side UI submission evidence is available, record it as a
separate surface. After this ladder fails, the default route is notification
plus Codex++ restart, not replacement. Create/select an App-native replacement
only when PMO/user explicitly approves, restart recovery repeatedly fails, or
the critical path cannot wait; then update the allowlist. The user deletes any
superseded thread after reviewing the replacement packet.

User restart notification rule: after the bounded ladder confirms a persistent
start-turn/agent-loop failure, notify the user directly that a Codex++ restart
is the next preferred recovery action and that the user may manually restart
faster if online. This notification does not create an indefinite approval
wait; after the notification attempts are recorded, continue authorized
restart recovery unless PMO/user explicitly defers. Do not spend repeated turns
probing the same dead thread and do not create a replacement first. Replacement requires
explicit PMO/user approval, repeated failed restart recovery, or a critical path
that cannot wait. After Codex++ restarts, run one no-op recovery validation and
record whether the thread moved to `partial_recovery`, `restored`, or remains
quarantined.

Mandatory email-before-restart rule: every planned Codex++ restart for a
dead-thread incident must attempt one sparse email notification before the
restart action. The body must stay short and Chinese, identify that Codex++ is
about to restart because a visible thread cannot start turns, and must not
include long paths, raw logs, tokens, or private state. Record the email audit
and reference it from the blocker/recovery packet. If email sending itself
fails, record that failure in the packet and continue with the authorized
restart only when waiting would block recovery. A successful email is not an
approval gate; it only gives the user a chance to manually restart faster. Do
not send repeated emails for the same open incident unless a new restart action
will actually be triggered.

Codex++ controlled restart rule: the user explicitly authorized the Codex++
manager entry below as the preferred manual/assisted restart surface for
persistent dead-thread incidents:

```text
D:\Program Files\Codex++\codex-plus-plus-manager.exe
```

This is a narrow exception to the usual "no GUI clicking" rule and only applies
to dead-thread recovery after the bounded ladder has produced a blocker packet.
Before triggering restart, CoAgentOps or the still-healthy mainline recovery
owner must write the blocker/recovery packet and attempt one sparse email
notification.
If the user cannot be notified, or if notification was sent and no explicit
manual deferral or visible intervention is available after a short window,
CoAgentOps may launch the manager and use its restart action. Because this ends the current Codex
conversation, the post-restart validation must be picked up by the native
30-minute PMO/CoAgentOps heartbeat automations: read the latest blocker packet,
run no-op validation for the affected thread, then record `partial_recovery`,
`restored`, or `still_quarantined`. In the expected case, resume production on
the same visible thread id after validation instead of creating another
department conversation. Do not edit Codex App private state or inspect private
session databases as part of this recovery.

Codex App restart recovery rule: on 2026-06-06, multiple previously blocked
visible threads recovered their `send_message_to_thread` / start-turn surface
after the Codex App crashed and restarted. The verified samples are Gateway Ops
R2 (`019e9be0-534e-7c22-97ff-98fa7c2af39b`), ROS2 Runtime R2
(`019e9b85-d4d8-7bf3-8afd-a65697cd3889`), and the old MWORKS thread
(`019e9999-b0d3-7682-bccd-faef08fcf1df`). Treat this as strong evidence of a
transient App or agent-loop lifecycle/state problem, not proven permanent
thread data corruption. It does not by itself restore a quarantined department
to production routing. Recovery classification must still record:

```text
pre_restart_failure = exact error and surface
post_restart_read = pass | fail
post_restart_noop_start_turn = pass | fail
settings_override_probe = pass | fail | not_run
user_ui_composer = pass | fail | unknown
automation_wakeup = pass | fail | unknown
production_routing_status = restored | quarantined | replacement_active
```

If post-restart no-op passes but the user-side UI composer or automation
wakeup has not been revalidated, keep the thread in `partial_recovery` and do
not restore production routing yet. If a production route is to be restored, PMO
or CoAgentOps must first run a bounded validation ladder with no business side
effects, update this workflow and
`Docs/Workflows/agent_task_ledger.md`, and notify PMO.

Old-thread replacement is allowed when the user or PMO decides that a visible
department was created through an older WSL/non-App-native path and cannot
reliably use current Codex App thread or automation surfaces. Replacement is
not a backup exercise. Before an old thread is marked safe for user deletion,
`MoSim｜CoAgent运维平台` must extract the reusable decisions, procedures,
boundaries, and recovery routes from the old conversation into canonical
project documents. The replacement packet must include a landing matrix:

```text
old_thread_id
new_thread_id
important_content_landed:
  - topic
  - canonical_doc
  - section_or_anchor
  - status: landed | missing | not_applicable
safe_to_delete_only_if_all_required_items_landed
```

Historical chats, screenshots, packets, or JSONL files are not the long-term
reader path. Future agents should recover from `AGENTS.md`,
`Docs/Workflows/new_conversation_context.md`, the relevant workflow/index docs,
and result/blocker packets. If a useful old-chat claim has no canonical doc
entry yet, route it through `Docs/Workflows/session_memory_migration.md` or the
responsible workflow doc before replacing the thread.

## 2. Recurring Checklist

| Check | Owner | Cadence | Evidence Path | Failure Notify |
|---|---|---|---|---|
| Visible thread registry and title drift | `MoSim｜CoAgent运维平台` | Every 30 minutes through the CoAgentOps heartbeat, after user reports a title change, or before cross-thread dispatch | `Results/agent_packets/returns/<request_id>.json`; optional scan under `Results/codex_history_audit/` | `MoSim｜主线 PMO`; archived gateway rows are recorded but not notified through a gateway owner |
| Deleted/absent thread cleanup | `MoSim｜CoAgent运维平台` | Every 4 hours or after a visibility scan | Result packet noting absent IDs removed from dispatchable registry; no long-lived blacklist required | `MoSim｜主线 PMO` if a requested target is absent |
| Codex native hooks and preflight health | `MoSim｜CoAgent运维平台` | Every 4 hours, after Codex upgrade, or after hook/preflight edit | `CoAgent/hooks/README.md` plus hook smoke output path in the task result packet | `MoSim｜主线 PMO`; `MoSim｜Codex 环境迁移部` if Windows-native Codex config or bridge residue is implicated |
| Codex native capability adoption | `MoSim｜CoAgent运维平台` with PMO decision authority | Every 4 hours or before adding CoAgent runtime/transport/schema machinery | Updated `Docs/Workflows/tooling_assets_governance.md`, `Docs/Index/codex_app_session_research.md`, or no-change result packet | `MoSim｜主线 PMO` for adoption decision; blocker packet if a native surface is unavailable |
| Workflow/skill/index duplicate or stale entry check | `MoSim｜CoAgent运维平台` | Every 6 hours through the CoAgentOps heartbeat due gate, or after a repeated workflow failure | `Docs/Index/workflow_index.md`, relevant workflow/skill docs, and return packet | Responsible task thread for local fixes; `MoSim｜主线 PMO` for cross-cutting routing conflicts |
| Archived WeChat gateway route | `MoSim｜CoAgent运维平台` records history only | No periodic self-check. Revisit only after an explicit user/PMO request to restore WeChat gateway diagnosis | Registry row in `CoAgent/dispatch/department_threads.json`; historical evidence under `Results/coagent_gateway/` | Sparse email remains the user notification path; do not notify or dispatch to the archived gateway owner |
| MWORKS activation/window patrol | `MoSim｜CoAgent运维平台` | Every 30 minutes through the CoAgentOps heartbeat, and after PMO/user reports an MWORKS login/license/GUI issue | Patrol result or blocker packet under `Results/agent_packets/returns/` or `Results/agent_packets/blockers/`; screenshot evidence under `Results/mworks_background_capture/` when captured | Sparse Chinese email alert to the user and PMO notification when login/license/authorization/demo/GUI-error or foreground inspection is needed |
| WeChat restoration blocker | `MoSim｜CoAgent运维平台` | Only if the user explicitly asks to restore WeChat gateway diagnosis and the archived route/tooling cannot be used | Request/blocker packet under `Results/agent_packets/blockers/`; optional evidence under `Results/coagent_gateway/` | Send sparse email blocker notification; do not dispatch to archived WeChat threads without explicit restoration approval |
| External source access blocker notification | Task owner; `MoSim｜CoAgent运维平台` audits recurring misses | Whenever a required external doc/page cannot be read after ordinary fetch plus local MCP/browser attempt, or needs auth/manual permission | Blocker packet under `Results/agent_packets/blockers/`; email audit under `Results/coagent_gateway/email/` when sent | Send sparse email blocker notification to the user; do not wait on WeChat |
| Background webpage read/screenshot | Task owner; `MoSim｜CoAgent运维平台` audits reusable capability | When a page must be read or visually captured while the user needs the foreground desktop | Prefer `windows_mcp.Scrape` for text; if visual evidence is needed, use Chrome headless with a project-local temporary profile and save screenshots under `Results/browser_captures/<request_id>/` | Notify the user through sparse email only if the page needs login/manual permission, Chrome/Edge is missing, or headless capture fails and foreground desktop interaction is unavoidable |
| Open-source probe and learning split | `MoSim｜开源项目探针` checks local reference inventory/upstream freshness; scoped sub-agents crawl requested new sources; `MoSim｜开源项目学习部` evaluates adoption | After each crawl/update batch or every 4 hours if scheduled | Manifests/index updates under `Docs/Index/external_learning_index.md`, `CoAgent/docs/research/REFERENCE_PROJECT_INDEX.md`, and return packets | `MoSim｜CoAgent运维平台` if split is unclear; `MoSim｜主线 PMO` if adoption changes engineering direction |
| DevOps/Git large-worktree need | `MoSim｜DevOps 发布` | Every 4 hours, before broad Git work, or when Git status/hooks are slow | `Docs/Workflows/agent_task_ledger.md`, DevOps result packet, and Git evidence paths | `MoSim｜主线 PMO`; blocker packet if auth, lock, hook, LFS, or size risk blocks commit/push |
| Subagent vs visible-thread surface sanity | Sending department; `MoSim｜CoAgent运维平台` audits recurring mistakes | Every non-trivial task graph and every cross-thread packet | Task graph or packet field naming selected surface, owner, return path, and why alternatives were not used | Origin thread if an internal subagent is described as a department, or if a visible-thread task lacks a real target thread ID |
| Result/blocker packet semantic sanity check | Sending department; `MoSim｜CoAgent运维平台` audits recurring mistakes | Every cross-thread packet before dispatch | Packet itself under `Results/agent_packets/returns/` or `Results/agent_packets/blockers/` | Origin thread if text has old titles, wrong direction, ambiguous pronouns, or inverted native-capability wording |

## 2.0 Background Webpage Capture

Use the least intrusive route for external pages:

```text
1. Try `windows_mcp.Scrape` with the URL and a focused query.
2. If text is enough, do not open a visible browser or take a desktop screenshot.
3. If layout/visual evidence is needed, use installed Chrome/Edge headless mode
   with a project-local temporary profile, never the user's default browser
   profile.
4. Save artifacts under `Results/browser_captures/<request_id>/`.
5. Use `windows_mcp.Snapshot` / `Screenshot` / visible desktop control only
   when the page must be interacted with and no headless or scrape route works.
   These tools observe the user's current foreground desktop and are not
   background capture. Before using them, state that foreground content may be
   captured unless the user has already approved that specific interaction.
6. If login, CAPTCHA, missing browser, or manual permission blocks the task,
   send one sparse email notification asking the user for that specific action.
```

Verified local command shape on 2026-06-06:

```powershell
$chrome = 'C:\Program Files\Google\Chrome\Application\chrome.exe'
$outDir = 'C:\Users\HP\Desktop\MoSim\Results\browser_captures\<request_id>'
$profile = Join-Path $outDir 'chrome-profile'
New-Item -ItemType Directory -Force -Path $outDir, $profile | Out-Null
& $chrome --headless=new --disable-gpu --no-first-run --no-default-browser-check `
  --user-data-dir=$profile --window-size=1280,2000 `
  --screenshot=(Join-Path $outDir 'page.png') '<url>'
```

Do not treat desktop screenshot tools as background capture: Windows MCP
`Snapshot` / `Screenshot` observe the current desktop and can interfere with
the user's foreground work. For non-web app controls, prefer UI Automation
Invoke, PowerShell, process/window queries, or a tool-specific API before any
foreground screenshot. The Codex++ restart route should use UI Automation or
PowerShell to invoke the `重启 Codex++` button when possible; foreground
screenshots are only a last-resort locator after warning the user.

Background click/operation boundary: a minimized window generally cannot be
reliably operated by ordinary mouse-coordinate clicks, because Windows does not
lay out or repaint many controls while minimized. Treat true background
operation as one of these routes: application CLI/API/MCP, process/window
messages for a known safe command, or UI Automation `InvokePattern` /
`ValuePattern` against a named control. If the target only supports pointer
input, use a bounded restore-without-activation flow where possible, perform
one precise operation, then re-minimize; record that it may briefly make the
window visible even if it should not steal focus. Do not call this "background"
if it relies on foreground screenshots or active desktop coordinate clicking.

## 2.0.1 MWORKS Background Evidence And Bounded Click

MWORKS/Sysplorer session reuse is mandatory by default. The current logged-in
window is the review surface and should be reused through MCP/session health
checks instead of opening a fresh MWORKS/Sysplorer GUI. Startup/loading splash
screens disrupt the user's desktop and duplicate windows make manual audit
unclear. Background screenshot/click tooling is for evidence and bounded
recovery on the existing window; it is not a reason to start another window.
Create or restart a MWORKS/Sysplorer window only after a blocker when PMO/user
approves, or when the current process is clearly frozen/duplicating windows and
cannot be recovered through the normal session route.

CoAgentOps owns routine MWORKS activation and window-health patrol through the
30-minute maintenance automation. Each patrol should inspect the existing
MWORKS/Sysplorer/Syslab windows with `check_mworks_gui_sentinel.py`,
`capture_window_background.ps1 -RestoreMinimized`, and any available
license/session/API evidence, then write a compact result or blocker packet
with the observed `license_state`. Engineering departments should reference
the latest patrol and continue their model/check/simulation/layout work unless
their current task observes demo/login/authorization/error evidence. They
should not spend each task turn repeatedly proving activation or return only
sentinel JSON as engineering progress.

If the patrol finds demo edition, login/activation prompt, authorization
failure, GUI-error/report dialog, mixed education/demo windows, or a state that
needs foreground inspection, keep the incident open, send one sparse Chinese
email alert, and notify PMO. CoAgentOps or PMO may bring the existing MWORKS
window foreground/maximized to expose a hidden login/license pane or to capture
full layout/review screenshots. Login/license patrol screenshots should be
maximized-window evidence because minimized/background captures can miss the
visible login pane. Use the existing maximized foreground window first. If the
official login action does not return or cannot complete on the existing
window, PMO/CoAgentOps may reopen MWORKS and log in through the official UI as
a bounded recovery. Delegated engineering departments still must not click
login/save/close/restart/send-report controls.

Use these project-local scripts before falling back to foreground desktop
screenshots when a MWORKS/Sysplorer window must be inspected while the user is
using another app:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File Scripts/tools/capture_window_background.ps1 `
  -TitleRegex 'Sysplorer|MWORKS|Quadrotor|AWFF' `
  -OutDir Results/mworks_background_capture/<request_id> `
  -RestoreMinimized -Maximize
```

For a single approved low-risk UI action, such as opening the MWORKS AI helper
panel for manual review, use a bounded background click and save JSON evidence:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File Scripts/tools/invoke_window_background_click.ps1 `
  -TitleRegex 'QuadrotorExperiments - Sysplorer' `
  -XRatio 0.546 -YRatio 0.081 `
  -OutDir Results/mworks_background_operation/<request_id> `
  -RestoreMinimized -KeepRestored
```

Validated boundary on 2026-06-06: `capture_window_background.ps1` can capture
useful Sysplorer PNGs by restore-without-activation plus `PrintWindow`; pure
minimized capture only produced a small shell image. A bounded `PostMessage`
click against the Sysplorer MWORKS AI toolbar location did not steal focus from
Codex and opened the window for manual inspection; whether a specific internal
Qt control accepts background messages must still be verified per control.

Incident ownership rule: specialist departments may collect extra background
screenshots for MWORKS activation, login, authorization, crash, and
error-report incidents, but they must stop model/MCP retries and return a
blocker to `MoSim｜主线 PMO`. PMO or `MoSim｜CoAgent运维平台` owns any follow-up
background recovery, user-facing intervention, or authorized click-through.
Do not use the bounded-click script for login credentials, activation, save,
close, restart, send-report, or crash-dialog recovery controls.

## 2.1 Native Automation Target

`MoSim｜CoAgent运维平台` should run this checklist through Codex App native
automation or thread wakeup when the current Codex surface exposes a reviewed
automation tool. Do not implement a replacement unattended scheduler inside
CoAgent just to compensate for a missing App automation surface.

Automation prompt size rule: recurring prompts should stay compact. Keep the
cadence, owner, entry docs, P0 gate, and result/blocker expectation in the
automation; keep detailed policy in `AGENTS.md`, workflow docs, skills,
templates, and checkers. If an automation still runs correctly, do not churn it
just to mirror every new rule in the prompt text.

Recommended initial automation:

```text
title: MoSim｜CoAgentOps状态自检
owner_thread: MoSim｜CoAgent运维平台
cadence: every 30 minutes
objective: Run the meta-maintenance checklist, verify current visible-thread
  registry/title drift, absent-thread cleanup, native hook/preflight health,
  native capability adoption, workflow/skill/index freshness, gateway owner
  routing, MWORKS activation/window patrol, open-source probe/learning split,
  DevOps/Git large-worktree need, and subagent-vs-visible-thread wording.
allowed_actions: read project docs/configs, run lightweight project-local
  syntax/preflight checks, write one result or blocker packet.
forbidden_actions: create/archive/rename threads, edit Codex App private DB,
  expand CoAgent runtime/transport/schema, perform broad Git staging, dispatch
  engineering work, or send high-volume notifications.
evidence: Results/agent_packets/returns/ or Results/agent_packets/blockers/
notify: email sparse blocker notification only when user action is needed or
  a blocker changes the plan.
```

Current created native automations:

| Automation ID | Owner | Cadence | Purpose |
|---|---|---|---|
| `mosim-pmo-p0-long-run-followup` | `MoSim｜主线 PMO` thread `019e9868-83ea-70f0-92c5-a3a408bd78c6` | 10-minute heartbeat | PMO P0 mainline follow-up and department patrol. Its first gate is an explicit CoAgentOps reachability check for `019e9bc1-ea9f-7102-b41a-4ef9b2308992`; if CoAgentOps itself cannot start turns, PMO directly owns the recovery packet, sparse email alert, a short manual-restart window, authorized Codex++ restart if no explicit deferral arrives, and next-heartbeat no-op validation. For ordinary department dispatch-surface failures, PMO writes the initial blocker and routes bounded diagnosis/recovery to CoAgentOps. |
| `mosim-wechat-gateway-hourly-health` | `MoSim｜CoAgent运维平台` thread `019e9bc1-ea9f-7102-b41a-4ef9b2308992` | 30-minute heartbeat with 6-hour P1 due gate | Historical id for the current CoAgentOps maintenance heartbeat. It excludes archived WeChat gateway routes, then checks CoAgentOps self-recovery, dead-thread restart recovery, MWORKS activation/window patrol, and visible-thread/automation health. For dead-thread or MWORKS license/GUI fail-close it records a sparse email audit, gives the user only a short manual-restart window when restart is planned, then continues authorized recovery if no explicit deferral arrives. Every 6 hours, after P0 health checks, it may run a bounded P1 workflow/skill/MCP/native-capability optimization audit with strict no-install, no-runtime, no-business-code, no-Git, and max-3-proposals constraints. |

Removed recovery automations:

| ID | Former Owner | Former Cadence | Current Status |
|---|---|---|---|
| `mosim-coagentops` | Detached workspace cron for `C:\Users\HP\Desktop\MoSim` | 30-minute cron | Deleted after user correction; do not recreate as default self-dead protection because detached cron creates a separate automation context and can pollute the project. |
| `MoSim-CoAgentOps-OuterWatchdog` | Windows Task Scheduler | 30 minutes | Deleted after user correction; do not reinstall as automatic restart logic. Use `Scripts/agent/codex_outer_watchdog.ps1` only as a manually authorized emergency helper. |

If the App automation creation tool is unavailable in the active Codex surface,
write a blocker packet with the proposed automation definition and notify the
PMO/user instead of editing private App state.

If `automation_update` is visible but the current task cannot confirm whether
an equivalent automation already exists without reading Codex private state,
do not create a possible duplicate. Return the proposed automation definitions
and the missing dedupe evidence in a result or blocker packet. A later PMO task
may authorize the documented `$CODEX_HOME/automations/*/automation.toml`
inspection route or provide resolved automation ids for update/view/delete.

Preferred existing-thread automation targets:

| Existing Thread | ID | Automation Need | Owner For Configuration |
|---|---|---|---|
| `MoSim｜Codex 上下文维护部` | `019e9be0-f6ac-7762-b80c-b1dd18b0d013` | New-conversation context, project memory/index drift, compact recovery updates | `MoSim｜CoAgent运维平台` configures the native automation; context thread owns doc updates |
| `MoSim｜开源项目探针` | `019e9be3-94de-7dc3-b067-92a78b678287` | Local reference-project inventory, upstream freshness checks, and manifest/update-candidate queues. New broad crawling belongs to scoped sub-agents or explicit task packets, not the standing probe thread. | `MoSim｜CoAgent运维平台` configures the native automation; probe thread owns manifests |
| `MoSim｜开源项目学习部` | `019e9be4-56d0-7981-b71c-a5ded1c7ec76` | Adopt/adapt/reference-only/reject review for probe candidates | `MoSim｜CoAgent运维平台` configures the native automation; learning thread owns evaluation output |

Creation procedure for CoAgent operations:

```text
1. Search native tools:
   tool_search query "automation_update create update view delete heartbeat cron"
2. If `automation_update` is available and the user approved a thread-attached
   mainline maintenance task, create or update it as:
   mode="create" or mode="update"
   kind="heartbeat"
   destination="thread"
   targetThreadId=<approved mainline thread id>
   name="MoSim｜CoAgentOps状态自检"
   rrule="FREQ=MINUTELY;INTERVAL=30"
   prompt=<self-contained checklist prompt that writes a result/blocker packet>
3. Do not create a detached cron for CoAgentOps self-dead protection unless
   PMO/user explicitly approves that exception for a concrete incident.
4. Before creating, confirm no equivalent active automation already exists.
   If the only dedupe route would read Codex private state and the task forbids
   that read, return a no-create result with the candidate definition instead
   of creating a duplicate.
5. If updating, first resolve the existing automation id and preserve fields
   that the user did not ask to change.
6. If tool access is missing, write a blocker packet and notify PMO/user through
   the normal sparse email route; do not use GUI clicking as the workaround.
```

Manual emergency helper commands:

```powershell
# Optional manual health marker for a written incident. Not scheduled.
powershell -NoProfile -ExecutionPolicy Bypass `
  -File Scripts\agent\codex_outer_watchdog.ps1 `
  -Mode MarkAlive -Source manual_incident

# Manual check only after PMO/user authorization. Do not run as a scheduled
# automatic restart loop.
powershell -NoProfile -ExecutionPolicy Bypass `
  -File Scripts\agent\codex_outer_watchdog.ps1 `
  -Mode Check -Source manual_incident -MaxStaleMinutes 90

# Manual forced recovery after a written dead-thread blocker.
powershell -NoProfile -ExecutionPolicy Bypass `
  -File Scripts\agent\codex_outer_watchdog.ps1 `
  -Mode RestartNow -Source manual_incident -IncidentKind coagentops_self_dead
```

The helper writes evidence under `Results/codex_watchdog/`. Email audit
records, when a restart notification is attempted, stay under
`Results/coagent_gateway/email/`. Historical watchdog evidence remains
historical only and is not proof of an active automatic recovery layer.

## 3. Packet Rules

Every meta-maintenance run must write one result or blocker packet:

```text
Results/agent_packets/returns/<request_id>.json
Results/agent_packets/blockers/<request_id>.json
```

Required packet content:

```text
request_id
origin_thread and origin_thread_id
target_thread and target_thread_id
status
registry_policy_checked
current_visible_registry_checked
deleted_absent_threads_policy
native_surface_gate
checks_performed
changed_files
evidence_paths
semantic_sanity_check
blockers
next_action
```

Before writing or dispatching a packet, run a semantic sanity check:

```text
no old standing department title used as an active owner
no absent thread ID used as a target
no archived WeChat gateway thread used as a target unless user explicitly restores it
no internal subagent described as a visible department thread
no visible-thread task dispatched through a hidden subagent only
if required external material cannot be read after local MCP/browser route, a blocker packet and email notification exist
no gateway incident sent to MoSim｜WechatCodex
no WeChat refresh instruction sent to gateway ops as if it were the message path
no "CoAgent replaces PMO" wording
no "CoAgent reimplements Codex native capability" wording
no inverted sentence such as "CoAgent 已由 Codex 原生支持"
all pronouns have a concrete owner/thread
```

## 4. Current Owner Boundaries

| Topic | Current Owner | Boundary |
|---|---|---|
| Main routing and engineering priority | `MoSim｜主线 PMO` | CoAgent ops can return blocker/proposal packets, but does not decide the MoSim technical roadmap. |
| Thread registry hygiene | `MoSim｜CoAgent运维平台` | Only current visible allowlist entries are dispatchable. |
| Context memory and startup recovery | `MoSim｜Codex 上下文维护部` | Not the same as Windows-native environment migration. |
| Windows-native Codex migration/history | `MoSim｜Codex 环境迁移部` | One-time environment repair and bridge residue audits, not routine context maintenance. |
| WeChat gateway implementation/health | Archived; no active owner | `MoSim｜微信网关运维部` and `MoSim｜WechatCodex` are historical/inactive routes. Restore only after explicit user/PMO approval for a scoped WeChat diagnosis task. |
| External doc/manual-access blocker | Task owner writes blocker; sparse email sends user notification | Do not silently wait or only leave the blocker in chat when the user needs to provide permission/content. |
| Validation/testing | Task-local gate, bounded subagent, `codex review`, or PMO-created scoped test thread | No standing validation department by default. |
| Toolchain/MCP upkeep | Task owner, or `MoSim｜CoAgent运维平台` for recurring meta-maintenance | No standing `MoSim｜工具链 MCP` department. |
| Security/compliance | `AGENTS.md`, hooks, prompts, preflight, and review gates | No standing security department by default. |

## 5. Completion Criteria

A meta-maintenance run is complete only when:

```text
current registry allowlist was checked or explicitly scoped out
deleted/absent thread handling follows allowlist-only policy
Codex native surface gate was considered before any CoAgent expansion proposal
workflow/skill/index owner or no-change status is recorded
gateway/probe/learning/DevOps owner boundaries are verified when relevant
result or blocker packet exists
changed docs, if any, pass semantic sanity review
```
