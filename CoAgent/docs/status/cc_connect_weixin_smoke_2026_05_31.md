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
