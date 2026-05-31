# Coding Agents Round 5

## source_slice

- Local coding-agent runtime references under `References/Agent`: OpenHands,
  OpenClaw, Claw Code, and CowAgent.
- Focused read on app-server/event-store/sandbox separation, task-flow state,
  report/event contracts, doctor checks, path scope, skills, memory, and tool
  safety.
- Current CoAgent target surfaces: transport, result router, hooks, doctor,
  automation guardrails, runtime task queue, and future worker placement.

## read_files_or_urls

- `References/Agent/OpenHands/README.md`
- `References/Agent/OpenHands/openhands/app_server/event/README.md`
- `References/Agent/OpenHands/openhands/app_server/sandbox/README.md`
- `References/Agent/openclaw/docs/automation/taskflow.md`
- `References/Agent/claw-code/README.md`
- `References/Agent/claw-code/docs/g004-events-reports-contract.md`
- `References/Agent/CowAgent/README.md`

## architecture_claims

1. Coding-agent systems separate user-facing surfaces, event stores, sandbox
   execution, settings/secrets, and task-flow state. CoAgent should keep these
   boundaries explicit instead of treating a chat thread as the whole runtime.
2. Secure execution requires a sandbox or at least a declared path/tool scope.
   OpenHands sandbox services and Claw path/doctor/security emphasis support
   CoAgent's current project-local filesystem boundary and preflight hooks.
3. Events and reports should be typed artifacts. Claw Code's lane-event/report
   contract reinforces CoAgent's result packet, review metadata, and knowledge
   summaries as machine-readable state rather than prose-only status.
4. Durable task flow is above individual background tasks. OpenClaw task flow
   validates CoAgent's separation between runtime tasks, visible worker
   conversations, result packets, and automation schedules.
5. Personal assistant memory/skills systems can be useful, but MoSim needs
   project memory, not private user memory. CowAgent-style channels, long-term
   memory, and skill hubs are portable references, not immediate MoSim runtime
   dependencies.

## adopt_now

- Keep CoAgent result packets and review files as typed event/report artifacts
  with evidence, next action, blocker detail, and review state.
- Keep doctor and preflight as first commands before long-running worker
  dispatch or automation.
- Keep task-flow state in project-owned runtime files and ignored `Results/`,
  not inside Codex App private state or a worker transcript.
- Keep sandbox/path scope as a non-negotiable guardrail for any future worker
  loop. Until container sandboxes exist, workers must use declared read/write
  scope and project-local command execution.
- Keep skills as project-local procedural memory tied to explicit tools and
  checks, not as a marketplace import path.

## adapt_later

- Add event-stream style run traces for department tasks, including structured
  event kind, status, timestamp, source, confidence, and provenance.
- Add optional sandbox adapters for high-risk coding tasks if CoAgent is
  reused beyond this project or if unattended execution becomes common.
- Add worker health and capability status similar to coding-agent app servers:
  tool availability, sandbox availability, MCP state, and last result import.
- Add richer task-flow commands for pause, cancel, resume, and mirror external
  worker runs.

## portable_only

- OpenHands cloud/local GUI patterns, CowAgent channel integrations, and
  OpenClaw multi-channel gateways are useful for future products but are not
  needed while Codex App remains MoSim's chosen frontend.
- Personal long-term memory and skill marketplaces are useful for standalone
  assistant products, but MoSim should prioritize project-scoped knowledge and
  source-traceable audits.
- Docker/Kubernetes sandbox infrastructure is portable future work; current
  MoSim execution stays local and path-scoped.

## reject

- Do not store secrets, credentials, browser profiles, channel tokens, or
  external account state inside CoAgent or tracked project files.
- Do not replace CoAgent runtime with OpenHands/OpenClaw/CowAgent runtime.
  Their designs inform boundaries; MoSim keeps its own lightweight runtime.
- Do not let terminal text override structured result packets when both exist.
- Do not auto-run broad coding-agent tasks without path scope, tool scope,
  timeout, review gate, and recovery artifact.

## unknowns

- Whether MoSim needs true container sandboxes depends on how much unattended
  coding-agent work is delegated beyond the current main conversation.
- Whether future Codex App APIs expose enough event/sandbox/thread structure to
  replace the current file/CLI adapter remains unverified.
- The minimum event schema needed for department traces is still open; current
  result packets are enough for first recovery but not rich observability.

## required_patch

- Add this coding-agent audit record to close the `coding_agents` source-family
  coverage gap.
- Keep existing CoAgent path/tool/review guardrails as adopted architecture and
  update status docs after coverage validation.
- No external runtime import is justified by this source slice.

## verification

```bash
python3 CoAgent/learning/learning_indexer.py coverage
python3 CoAgent/learning/learning_indexer.py validate --strict
python3 CoAgent/knowledge/knowledge_indexer.py build
python3 CoAgent/knowledge/knowledge_indexer.py search --query coding_agents --limit 10
python3 CoAgent/doctor/coagent_doctor.py
python3 CoAgent/hooks/preflight.py
```

## next_trigger

- Revisit this audit before adding unattended coding workers, sandbox adapters,
  or richer department event streams.
- Revisit this audit if Codex App exposes a stable app-server/event/sandbox
  interface that can replace file-based transport.
