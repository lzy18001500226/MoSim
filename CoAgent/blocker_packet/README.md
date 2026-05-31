# CoAgent Blocker Packet

## Purpose

This directory owns blocker-notification packet generation from task-health
decisions.

`blocker_packet.py` is read-only with respect to runtime state. It reads the
current task-health snapshot, decides whether autonomous continuation must
stop, and writes one standard `blocker_notification` JSON/Markdown packet when
human, review, safety, or rework intervention is required.

It does not dispatch conversations, send Weixin messages, stage Git, commit,
or push.

By default it does not mutate runtime metadata. Use `--record-metadata` only
when the caller holds the current task claim token and wants the generated
blocker packet path to become recoverable from status/review/resume surfaces.

## Command

```bash
python3 CoAgent/blocker_packet/blocker_packet.py \
  --task-id COAGENT-IMPL-LONGRUN-20260531 \
  --output Results/agent_packets/blockers/COAGENT-IMPL-LONGRUN-20260531.blocker.json \
  --markdown-output Results/agent_packets/blockers/COAGENT-IMPL-LONGRUN-20260531.blocker.md
```

If no blocker exists, the command reports `needed=false` and does not write a
packet unless `--write-when-clear` is used.

To record the latest blocker check and generated packet paths into runtime
metadata:

```bash
python3 CoAgent/blocker_packet/blocker_packet.py \
  --task-id COAGENT-IMPL-LONGRUN-20260531 \
  --output Results/agent_packets/blockers/COAGENT-IMPL-LONGRUN-20260531.blocker.json \
  --markdown-output Results/agent_packets/blockers/COAGENT-IMPL-LONGRUN-20260531.blocker.md \
  --record-metadata \
  --claim-token <claim-token>
```

Do not paste claim tokens into tracked files, chat summaries, or review
packets.

To dry-run a generated packet through the approved Weixin adapter:

```bash
python3 CoAgent/gateway/cc_connect_weixin.py notify \
  --packet Results/agent_packets/blockers/COAGENT-IMPL-LONGRUN-20260531.blocker.json
```

Real sending still requires the adapter's explicit `--send` and session
parameters.
