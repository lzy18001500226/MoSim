# cc-connect Weixin Smoke Test

Date: 2026-05-31

Status: smoke_passed

Scope: personal WeChat / Weixin ilink gateway smoke test for CoAgent human-intervention notification research. This is not a production gateway rollout.

## Local Paths

- Reference project: `References/Agent/Gateway/cc-connect`
- Temporary binary: `Results/tmp/cc-connect-node/node_modules/cc-connect/bin/cc-connect`
- Temporary config/state: `Results/tmp/cc-connect-weixin-smoke/`
- WSL runtime state for Unix socket send tests:
  `/home/linux/.cache/mosim/coagent/cc-connect-weixin/data`
- These paths are ignored by Git through `Results/tmp/`.

## Commands That Worked

Install fallback used for this smoke test: the npm install path timed out, so the release binary was downloaded from the Gitee release mirror and placed under the temporary node package bin path.

QR setup:

```bash
Results/tmp/cc-connect-node/node_modules/cc-connect/bin/cc-connect weixin setup \
  --config Results/tmp/cc-connect-weixin-smoke/config.toml \
  --project mosim-weixin-smoke \
  --timeout 60 \
  --qr-image Results/tmp/cc-connect-weixin-smoke/qr.png \
  --set-allow-from-empty
```

Run a bounded listener smoke window:

```bash
timeout 60s Results/tmp/cc-connect-node/node_modules/cc-connect/bin/cc-connect \
  --config Results/tmp/cc-connect-weixin-smoke/config.toml \
  --force
```

Run with WSL-local runtime state when `cc-connect send` / internal API is
needed:

```bash
Results/tmp/cc-connect-node/node_modules/cc-connect/bin/cc-connect \
  --config Results/tmp/cc-connect-weixin-smoke/config-wsl-runtime.toml \
  --force
```

Send an approved notification packet through the CoAgent adapter:

```bash
python3 CoAgent/gateway/cc_connect_weixin.py notify \
  --packet Results/coagent_gateway/smoke/longrun_review_notification.json \
  --session '<weixin session key>' \
  --send \
  --omit-message-in-audit
```

Import a result packet and create a gated Weixin notification dry-run when
the review gate requires human action:

```bash
python3 CoAgent/result_router/result_router.py import \
  --packet Results/agent_packets/<task_id>.json \
  --notify-weixin
```

Real sending remains explicit and requires an approved session:

```bash
python3 CoAgent/result_router/result_router.py import \
  --packet Results/agent_packets/<task_id>.json \
  --notify-weixin \
  --send-weixin \
  --weixin-session '<weixin session key>' \
  --omit-weixin-message-in-audit
```

## Result

- QR login succeeded after the user scanned with phone WeChat.
- cc-connect wrote Weixin platform fields into the project-local temporary config.
- A WeChat `你好` message was received by the listener.
- cc-connect spawned/resumed a Codex session and completed one turn.
- Weixin context state was written under `Results/tmp/cc-connect-weixin-smoke/data/weixin/.../context_tokens.json`.
- WSL-local runtime state allowed `api.sock` creation.
- `cc-connect send` returned `Message sent successfully` for a CoAgent
  manual-review smoke packet.
- `CoAgent/gateway/cc_connect_weixin.py` now provides a narrow adapter for
  blocker/review/result packets with dry-run default, redaction, dedupe, and
  JSONL audit.
- `CoAgent/result_router/result_router.py --notify-weixin` now connects the
  result review gate to the adapter. Accepted packets skip notification;
  packets needing review produce `Results/agent_packets/notifications/*.json`
  and dry-run by default.

## Observed Limitation

When `data_dir` is on the Windows-mounted project path, cc-connect logged:

```text
api server unavailable: listen unix .../data/run/api.sock: bind: operation not supported
```

The Weixin receive/send path still worked. The limitation affects the internal Unix-socket API used by commands such as `cc-connect send` and should be handled before relying on the Management/Internal API. A future production adapter should keep secret/runtime state in an approved WSL-local runtime directory or patch/configure cc-connect to use a supported socket path while keeping project docs and non-secret manifests in the repository.

The tested workaround is to keep the cc-connect runtime `data_dir` on WSL local
storage under `/home/linux/.cache/mosim/coagent/cc-connect-weixin/data`, while
keeping project-side setup evidence and non-secret adapter code under MoSim.
The runtime directory may contain local session/cache material and must not be
committed.

## Operating Rules Learned

- Always pass `--config` explicitly. Running `cc-connect` without it can create a default config under the WSL home directory.
- Do not print or commit `token`, `base_url`, `context_token`, or account identifiers.
- Keep real gateway sending gated. Use `CoAgent/gateway/cc_connect_weixin.py`
  and pass `--send` only for approved blocker/review classes.
- Default adapter mode is dry-run; sent messages are deduped and recorded under
  ignored `Results/coagent_gateway/`.
- For CoAgent, cc-connect should remain an optional human-intervention gateway candidate, not the task source of truth.

## 2026-06-01 Progress Notification Issue

The long ROS2/FAST-LIO task did not send periodic progress reports after the
initial smoke message. Root causes:

- The current gateway is packet-triggered only. It sends explicit blocker or
  review packets; it does not provide a periodic heartbeat/progress reporter.
- The active goal was observed in `paused` state, so no long-running task loop
  was continuing to emit progress packets.
- A manual progress packet send attempt failed with `no active session found`.
  The cc-connect history file still listed a previous `s1` session, but the
  runtime internal API did not consider it active. Treat this as Weixin gateway
  runtime/session loss until the session is refreshed.

Operational correction: do not assume a successful old smoke test means future
messages are deliverable. Before relying on Weixin for unattended work, run a
fresh send smoke and require `send_result.ok=true`. If cc-connect reports no
active session, restart/rebind the gateway or ask the user to rescan/reconnect.
The adapter now returns a process failure when the underlying send fails, so
automation cannot silently treat a failed notification as delivered.

## 2026-06-01 Recovery

Recovery used a 10 minute QR login:

```bash
Results/tmp/cc-connect-node/node_modules/cc-connect/bin/cc-connect weixin setup \
  --config Results/tmp/cc-connect-weixin-smoke/config-wsl-runtime.toml \
  --project "MoSim｜微信通知网关" \
  --qr-image Results/tmp/cc-connect-weixin-smoke/qr-restore-20260601-10min.png \
  --timeout 600 \
  --set-allow-from-empty
```

The project name was standardized to:

```text
MoSim｜微信通知网关
```

After QR login, the user must send one message in the Weixin conversation to
finish cc-connect context/session binding. The restored session state file is:

```text
/home/linux/.cache/mosim/coagent/cc-connect-weixin/data/sessions/MoSim｜微信通知网关_b075d247.json
```

The successful send smoke used project `MoSim｜微信通知网关` and the platform
session key from that state file. Result: `Message sent successfully.`

Do not use the old project key `mosim-weixin-smoke` for future user-visible
notifications unless intentionally auditing old smoke history.

## 2026-06-02 `s1` Send Failure Root Cause

The QR login had not necessarily expired. The failed notification used:

```text
--session s1
```

`s1` is cc-connect's internal conversation id in the session JSON. The
`cc-connect send --session` argument expects the platform session key from the
`active_session` map, for example a redacted key shaped like:

```text
weixin:dm:<redacted>@im.wechat
```

Passing the internal id directly returns:

```text
Error: no active session found (key="s1")
```

even when the Weixin QR login state is still valid. The direct send check with
the platform key returned `Message sent successfully`.

`CoAgent/gateway/cc_connect_weixin.py` now resolves internal ids such as `s1`
to the platform session key by reading the project runtime session file before
calling `cc-connect send`. Future automation may still pass `--session s1`, but
the adapter must translate it first. If sending fails after this fix, then
check whether the cc-connect runtime is running and whether the Weixin QR login
state has actually expired.

## 2026-06-02 `ret=-2` Send Recovery

Observed failure:

```text
Error: weixin: send chunk 1/1: weixin: sendMessage: ret=-2 errcode=0 errmsg=
```

This happened after earlier sends had succeeded with the same project
`MoSim｜微信通知网关` and the same resolved platform session key. It was not a
packet-format problem, project-name problem, or `s1` session-resolution problem.

Recovery test:

1. User sent a normal message, `你好`, in the Weixin gateway conversation.
2. The same notification packet was resent through
   `CoAgent/gateway/cc_connect_weixin.py notify --project 'MoSim｜微信通知网关' --session s1`.
3. Result: `Message sent successfully.`

Practical conclusion:

```text
ret=-2 can mean the Weixin/iLink send context is stale even when the QR login
state and session file still exist. Ask the user to send one message to the
gateway conversation first, then retry the notification once.
```

Do not immediately assume QR login expiry. If one user message refreshes the
context and the retry succeeds, record the recovery and continue. If the retry
still fails, then proceed to QR setup/rebind.

## 2026-06-02 Project-Name Session Alias Regression

Observed failure:

```text
Error: no active session found (key="MoSim｜微信通知网关")
```

Root cause: some notification calls passed the project name as `--session`.
`cc-connect send --session` expects the platform key from `active_session`, not
the project name. The previous adapter only resolved empty platform keys and
internal ids such as `s1`; it did not treat the project name or session JSON
path as aliases for the active platform key.

Fix:

- `CoAgent/gateway/cc_connect_weixin.py` now defaults to project
  `MoSim｜微信通知网关`.
- `resolve_session_key()` now accepts these forms:
  - empty session: first active session for the project;
  - `s1`: internal session id;
  - `MoSim｜微信通知网关`: project-name alias;
  - `.../sessions/MoSim｜微信通知网关_*.json`: session JSON file path;
  - `weixin:dm:...`: already-resolved platform key.
- `CoAgent/result_router/result_router.py` and
  `CoAgent/review_queue/review_queue.py` now use the same default project.

Verification:

```bash
python3 CoAgent/tests/test_gateway_weixin.py
python3 CoAgent/gateway/cc_connect_weixin.py notify \
  --packet Results/coagent_gateway/progress/weixin_gateway_diagnosis_20260602.json \
  --send --force --omit-message-in-audit --timeout 60
```

Result: `Message sent successfully.`

Current recovery order for future failures:

1. Run a bounded adapter send with empty `--session` or `--session s1`.
2. If the error is `no active session found`, inspect
   `/home/linux/.cache/mosim/coagent/cc-connect-weixin/data/sessions/` and
   confirm `active_session` exists.
3. If the error is `ret=-2`, ask the user to send one normal message to the
   Weixin gateway conversation, then retry once.
4. If retry still fails, rerun the 10 minute QR setup and then require the user
   to send one normal message to bind/refresh `context_token`.

Operational warning: do not use the Weixin gateway conversation as a high-volume
Codex transcript mirror. Logs showed cc-connect trying to send tool output and
long assistant responses back through Weixin before repeated `ret=-2` errors.
For MoSim, Weixin should be a sparse human-intervention/progress channel.
