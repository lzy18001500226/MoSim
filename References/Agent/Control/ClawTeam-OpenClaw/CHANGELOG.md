# Changelog

All notable changes to ClawTeam-OpenClaw are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [PEP 440](https://peps.python.org/pep-0440/) with `+openclaw` local identifier.

## [0.3.0+openclaw1] - 2026-04-04

### Added

- **Per-agent model resolution** with 7-level priority chain: CLI > agent model > agent tier > template strategy > template model > config default > None ([#53](https://github.com/win4r/ClawTeam-OpenClaw/pull/53))
- **Cost Dashboard MVP** — real-time token/cost aggregation by agent, model, and task dimensions with `clawteam board cost` command ([#52](https://github.com/win4r/ClawTeam-OpenClaw/pull/52))
- **Circuit Breaker** — healthy → degraded → open tri-state with half-open probing for agent failure isolation ([#52](https://github.com/win4r/ClawTeam-OpenClaw/pull/52))
- **Retry with exponential backoff** — `RetryConfig` + `spawn_with_retry()` for resilient agent spawning ([#52](https://github.com/win4r/ClawTeam-OpenClaw/pull/52))
- **Idempotency keys** for `create()` and `send()` — deduplication for production reliability ([#52](https://github.com/win4r/ClawTeam-OpenClaw/pull/52))
- **Max 4 workers warning** — backed by Google/MIT empirical research (arXiv:2512.08296) ([#50](https://github.com/win4r/ClawTeam-OpenClaw/pull/50))
- **Intent-based prompts** — military C2 Auftragstaktik-inspired `intent` / `end_state` / `constraints` fields in AgentDef ([#50](https://github.com/win4r/ClawTeam-OpenClaw/pull/50))
- **Boids emergence rules** — Reynolds 1986 flocking rules adapted for LLM agent coordination ([#50](https://github.com/win4r/ClawTeam-OpenClaw/pull/50))
- **Metacognitive self-assessment** — confidence tagging in agent outputs ([#50](https://github.com/win4r/ClawTeam-OpenClaw/pull/50))
- **Runtime live injection** — `runtime inject/state/watch` CLI commands for tmux inbox messaging at runtime (cherry-picked from upstream [#85](https://github.com/HKUDS/ClawTeam/pull/85)) ([#54](https://github.com/win4r/ClawTeam-OpenClaw/pull/54))
- **OpenClaw 4.2 compatibility** — workspace isolation for workers, allowlist path hints, `--agent` flag detection ([#56](https://github.com/win4r/ClawTeam-OpenClaw/pull/56))

### Fixed

- Waiter zero-tasks edge case (cherry-picked from upstream [#101](https://github.com/HKUDS/ClawTeam/pull/101)) ([#54](https://github.com/win4r/ClawTeam-OpenClaw/pull/54))
- Windows `Path.rename()` → `os.replace()` in 5 files (cherry-picked from upstream [#102](https://github.com/HKUDS/ClawTeam/pull/102)) ([#54](https://github.com/win4r/ClawTeam-OpenClaw/pull/54))
- TOCTOU race condition in idempotency check ([#52](https://github.com/win4r/ClawTeam-OpenClaw/pull/52))
- `cost_rate()` timezone fragility ([#52](https://github.com/win4r/ClawTeam-OpenClaw/pull/52))
- Import sorting (ruff I001) ([#45](https://github.com/win4r/ClawTeam-OpenClaw/pull/45))
- Spawn registry cleanup after agent exit ([#41](https://github.com/win4r/ClawTeam-OpenClaw/pull/41))

### Changed

- Project URLs now point to `win4r/ClawTeam-OpenClaw` instead of upstream
- Version bump from 0.2.0 to 0.3.0

## [0.2.0+openclaw1] - 2026-03-29

### Added

- OpenClaw as default agent (first-class support)
- Kimi / Qwen / OpenCode CLI support
- Subproject workspace overlay ([#27](https://github.com/win4r/ClawTeam-OpenClaw/pull/27))
- Zombie agent detection ([#36](https://github.com/win4r/ClawTeam-OpenClaw/pull/36))
- Shared memory scope ([#26](https://github.com/win4r/ClawTeam-OpenClaw/pull/26))
- Agent parameter handling for openclaw_agent ([#6](https://github.com/win4r/ClawTeam-OpenClaw/pull/6))
- 11-language README
- GitHub Actions CI
- PEP 440 versioning

### Fixed

- Trust prompt timeout ([#21](https://github.com/win4r/ClawTeam-OpenClaw/pull/21))
- Spawn registry cleanup after exit ([#41](https://github.com/win4r/ClawTeam-OpenClaw/pull/41))
- Skill context cleanup ([#44](https://github.com/win4r/ClawTeam-OpenClaw/pull/44))
