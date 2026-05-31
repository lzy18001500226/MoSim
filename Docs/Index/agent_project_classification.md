# Agent Reference Classification

> Status: active routing index. `Docs/Skills/Agent` has been merged into
> `References/Agent`; do not recreate a separate Agent skills tree.

## Principle

Classify by what each upstream project can contribute to CoAgent:

- reusable runtime/control-plane code,
- UI or product surface we can adapt,
- skills/hooks/operator patterns,
- memory/context/indexing ideas,
- security/evaluation gates,
- SDK/model plumbing,
- low-priority or unrelated reference material.

Default to reuse-first engineering. Before hand-writing CoAgent UI,
orchestration, workflow, memory, security, skill, hook, or SDK plumbing, check
the matching P0/P1 upstream category here and record one of these decisions:

- `reuse`: copy or vendor a component after license/security review;
- `port`: reimplement the pattern using our stack and APIs;
- `study`: keep as design reference only;
- `reject`: not compatible with our safety, license, or runtime boundary.

Keep each upstream repository intact. Do not split one repository's `skills`,
MCP examples, plugins, hooks, source, docs, and UI into different MoSim
directories. Many projects mix these concerns by design.

Current safe layout:

```text
References/Agent/
  Platforms/
  Control/
  Gateway/
  Workflow/
  Skills/
  Memory/
  Security/
  UI/
  SDK/
  Domain/
  ReviewLater/
Docs/Index/agent_project_classification.md
  <capability classification, reuse priority, and move plan>
CoAgent/docs/research/REFERENCE_PROJECT_INDEX.md
  <stable master coverage index for all References/>
```

Physical category folders exist. All current Agent reference projects are under
one primary category directory. Keep future additions in the same pattern and
update both indexes after moving.

## Target Categories

Use these category directory names for study queues and migration planning.

| Category | Meaning |
|---|---|
| `Platforms` | Full coding-agent or multi-agent products/runtimes that may contain reusable code |
| `Control` | Team orchestration, task boards, worktrees, inboxes, dispatch, and visible-agent coordination |
| `Gateway` | External communication gateways, IM/chat adapters, notification bridges, and human-intervention channels |
| `Workflow` | Durable state, checkpoints, specs, workflow engines, WAL/replay, task lifecycle |
| `Frameworks` | General multi-agent frameworks to learn from, not import wholesale |
| `Skills` | Skills, hooks, commands, plugins, rules, role packs, and operator methods |
| `Memory` | RAG, repo indexes, graph memory, context assembly, search, knowledge bases |
| `Security` | Red-team, eval, MCP/skill scanning, guardrails, SOC, governance |
| `UI` | Desktop/web/mobile UI surfaces, dashboards, Kanban, Codex App-like shells |
| `SDK` | Official SDKs, model APIs, tokenizers, model references |
| `Domain` | Domain agent products or examples useful only for a specific scenario |
| `ReviewLater` | Low-priority, unclear, or currently unrelated material |

MCP is not a top-level category. Treat MCP as an interface inside the owning
category: search MCP belongs under `Memory`, security MCP under `Security`,
plugin MCP under `Skills`, and MoSim Unreal/Epic MCPs stay under
`Docs/Skills/Unreal/`.

## Reuse Priority

### P0: Migration Candidates

Study first when implementing CoAgent. These are not just reading references;
they are candidates for direct adaptation.

| Project | Category | Reuse Target |
|---|---|---|
| `openclaw` | `Platforms` | Control UI, session/workspace routing, skill/sandbox boundaries, gateway ideas |
| `CodexMonitor` | `Control` | Codex App/server workspace UI, thread state, worktree/clone agent management |
| `agent-teams-ai` | `Control` | Kanban/team UI, agent-to-agent communication concepts, desktop app pattern |
| `OpenHands` | `Platforms` | Coding-agent execution environment, web frontend, runtime/server split |
| `hermes-agent` | `Platforms` | Memory, scheduler, skill evolution, messaging gateway, TUI/web surfaces |
| `hermes-desktop` | `UI` | Desktop wrapper and Hermes management UX ideas |
| `OpenMOSS` | `Control` | AI-company/task/subtask/agent management backend model |
| `ClawTeam` | `Control` | Worktree/tmux/agent inbox/task-board multi-agent CLI |
| `AgentsMesh` | `Control` | Control-plane/data-plane split, AgentPods, distributed runner model |
| `codex` | `Platforms` | Codex runtime, app-server, thread store, session/rollout, exec policy |
| `bifrost` | `Platforms` | AI gateway, provider routing, failover, monitoring, and MCP gateway ideas |
| `cc-connect` | `Gateway` | WeChat/IM gateway, hooks, bridge protocol, management API, and human-intervention notification path |

### P0: Architecture Foundations

Study first for design constraints and implementation contracts.

| Project | Category | Reuse Target |
|---|---|---|
| `langgraph` | `Workflow` | State graph, checkpointing, HITL and durable execution patterns |
| `temporal` | `Workflow` | Long-running workflow semantics and failure recovery |
| `sdk-python` | `Workflow` | Temporal Python SDK usage patterns |
| `sdk-typescript` | `Workflow` | Temporal TypeScript SDK usage patterns |
| `OpenSpec` | `Workflow` | Spec/proposal/tasks workflow for controlled AI coding |
| `TaskWeaver` | `Workflow` | Planner/executor state and data-analysis workflow separation |
| `antfarm` | `Workflow` | Deterministic local team workflow, YAML/SQLite/fresh context |
| `ECC` | `Skills` | Cross-client operator system, hooks, rules, skills, MCP config patterns |
| `context-engineering-kit` | `Skills` | Context engineering, review/TDD/reflexion plugin patterns |
| `AutoSkill` | `Skills` | Skill extraction, skill evolution, OpenClaw trajectory-to-skill ideas |
| `AI-Infra-Guard` | `Security` | MCP/skill/agent security scanning and AI red-team controls |
| `promptfoo` | `Security` | LLM eval/red-team baseline and CI-style checks |
| `rogue` | `Security` | Agent/MCP/A2A behavior evaluation |
| `openai-agents-python` | `Frameworks` | Official tool/handoff/guardrail/tracing primitives |
| `anthropic-sdk-python` | `SDK` | Anthropic beta resources, sessions, memory stores |
| `openai-skills` | `Skills` | OpenAI/Codex skill format |
| `anthropics-skills` | `Skills` | Anthropic skill templates and packaging |

## Full Classification

### Platforms

Full products/runtimes. These may have source that can be adapted, but only
after license and integration review.

| Project | Notes |
|---|---|
| `codex` | Primary Codex source and app-server/runtime reference |
| `openclaw` | Local-first agent shell, control UI, channel gateway, skills, sandbox/session routing |
| `hermes-agent` | Self-improving runtime, memory, scheduler, gateway, skills, TUI/web |
| `OpenHands` | Full coding-agent platform with frontend and execution environment |
| `CowAgent` | Personal assistant with skills, memory, bridge/channel/plugin layers |
| `claw-code` | Coding-agent harness reference |
| `moltis` | Secure persistent personal agent server |
| `spacebot` | Long-running agent harness with channels and graph memory |
| `tinyagi` | Local multi-team, 24/7 agent daemon and web portal |
| `goclaw-dev` | Multi-tenant agent gateway platform |
| `zylos-core` | Autonomous agent infrastructure with scheduler/message channels |
| `AChat-canary` | Enterprise/local-first AI chat platform |
| `bifrost` | AI gateway, provider routing, failover, monitoring, and MCP gateway reference |

### Control

Team orchestration, task routing, worktrees, visible-agent departments, and
communication surfaces.

| Project | Notes |
|---|---|
| `ClawTeam` | Framework-independent multi-agent collaboration CLI, inbox, board, worktrees |
| `ClawTeam-OpenClaw` | OpenClaw-oriented ClawTeam integration |
| `agent-teams-ai` | Desktop control plane for Claude/Codex/OpenCode agent teams |
| `AgentsMesh` | Control-plane/data-plane split and distributed AgentPods |
| `OpenMOSS` | AI company OS with tasks, subtasks, agents, and WebUI static release |
| `CodexMonitor` | Tauri multi-Codex workspace/thread controller |
| `oh-my-codex` | Codex workflow and orchestration layer |
| `oh-my-agent` | Portable multi-agent harness and team/skill system |
| `oh-my-claudecode` | Claude Code multi-agent plugin/workflow layer |
| `agor` | Team coding-agent command center |
| `squad-dev` | Human-led AI agent team workflow |
| `symphony` | Work item to autonomous implementation/PR/CI/evidence automation |
| `AutoGroq` | Dynamic expert-agent/team generator |

### Workflow

Durable task state, checkpoints, replay, specification, and long-running
execution semantics.

| Project | Notes |
|---|---|
| `langgraph` | Durable graph execution, checkpoints, memory, HITL |
| `temporal` | Durable workflow engine |
| `sdk-python` | Temporal Python SDK |
| `sdk-typescript` | Temporal TypeScript SDK |
| `OpenSpec` | Spec/proposal/tasks governance |
| `TaskWeaver` | Code-first planner/executor with data state |
| `harness` | Harness/runtime reference; needs deeper review |
| `okwinds` | WAL, task graph, runtime and review patterns |
| `mlflow` | AI/ML lifecycle, tracing, eval, prompt management |

### Gateway

External communication gateways, IM/chat adapters, notification bridges, and
human-intervention channels. Gateway projects are not the task source of truth.
They receive CoAgent blocker, review, and result packets and deliver concise
messages to the user or operators.

| Project | Notes |
|---|---|
| `cc-connect` | Multi-channel bridge for WeChat personal account, WeCom, Feishu, DingTalk, Telegram, Slack, Discord, QQ, hooks, Web UI, Management API, and Bridge WebSocket protocol. First candidate for CoAgent human-intervention notification experiments. |

### Frameworks

General agent frameworks. Prefer learning patterns over importing them as the
core CoAgent runtime.

| Project | Notes |
|---|---|
| `openai-agents-python` | Official agent/tool/handoff/guardrail/tracing SDK |
| `ag2` | AutoGen-derived Python multi-agent framework |
| `autogen` | Event-driven Microsoft multi-agent framework |
| `crewAI` | Crew/Flow enterprise automation |
| `camel` | AI society and agent scaling research |
| `MetaGPT` | Software-company SOP role model |
| `llama-agents` | LlamaIndex event workflow and service deployment |
| `mastra` | TypeScript production agent app/workflow framework |
| `langchain` | LLM tool/chain/agent ecosystem |
| `haystack` | RAG/search/agent pipeline framework |
| `NeMo-Agent-Toolkit-develop` | NVIDIA agent ops, evaluation, profiling, MCP/A2A |
| `swarm` | Minimal handoff model; historical OpenAI reference |

### Skills

Reusable operating methods, skills, hooks, commands, plugins, role packs, and
verification practices.

| Project | Notes |
|---|---|
| `ECC` | Cross-client operator system; hooks, rules, skills, MCP configs |
| `AutoSkill` | Skill extraction/evolution, SkillBank, OpenClaw trajectory extraction |
| `Awesome-Agent-Skills` | Agent-skill lifecycle survey and resource hub |
| `Agent-Skills-for-Context-Engineering` | Context/harness/evaluation skills |
| `agent-skills` | Production engineering skills |
| `SuperClaude_Framework` | Claude structured commands, agents, modes |
| `context-engineering-kit` | Context engineering plugin patterns |
| `pro-workflow` | Memory/workflow/hook/agent toolkit |
| `superpowers` | Coding-agent methodology skills |
| `andrej-karpathy-skills` | Coding-agent behavior rules |
| `anthropics-skills` | Anthropic skill spec/examples |
| `openai-skills` | OpenAI/Codex skill examples |
| `awesome-codex-skills` | Broad Codex skill examples |
| `awesome-codex-subagents` | Codex subagent role examples |
| `awesome-claude-agents` | Claude agent role examples |
| `awesome-openclaw-skills` | OpenClaw skill ecosystem |
| `claude-plugins-official` | Official Claude plugin/skill packaging |
| `mattpocock-skills` | Engineering feedback, TDD, diagnostic skills |
| `codex-plugin-cc` | Codex plugin/reference integration |
| `HeavySkill` | Test-time heavy-thinking skill/harness reference |
| `MMSkills` | Multimodal skills and task-skill mappings |
| `SR-Agents` | Skill retrieval augmentation for agentic AI |
| `SSL` | Scheduling-Structural-Logical skill representation assets |
| `SkillRouter` | Large-scale skill routing and evaluation |
| `SkillX` | Skill knowledge-base construction |

### Memory

Context retrieval, knowledge indexing, repo understanding, graph/RAG systems,
and search tools.

| Project | Notes |
|---|---|
| `GraphRAG` | Graph-based retrieval and memory/reference indexing |
| `context7` | Up-to-date documentation retrieval MCP/skill reference |
| `docs-mcp-server` | Local documentation indexing and MCP server reference |
| `graphify-8` | Code/document/media knowledge graph for coding assistants |
| `RepoAgent` | Repository documentation and chat-with-repo |
| `deepwiki-rs` | C4/wiki generation for repositories |
| `SurfSense` | Personal knowledge base and desktop assistant |
| `anysearch-mcp-server` | Search MCP server |
| `anysearch-skill` | Search skill wrapper |
| `csghub` | Self-hosted model/data/code asset hub |
| `openpencil` | Design-as-code and agent design workflow |
| `vexa` | Meeting bot/transcription with MCP, useful for context capture ideas |

### Security

Safety, red-team, eval, MCP/skill scanning, SOC, and governance.

| Project | Notes |
|---|---|
| `AI-Infra-Guard` | AI infra/MCP/Agent Skill security scanner |
| `AiSOC` | SOC automation and auditable investigation |
| `Decepticon` | Autonomous red-team agent; high-risk reference only |
| `LitterBox` | Payload analysis sandbox |
| `agentic_security` | LLM/agent jailbreak and fuzzing scanner |
| `pentestagent` | Authorized pentest agent; high-risk reference only |
| `promptfoo` | LLM eval and red-team baseline |
| `redamon` | End-to-end security pipeline; high-risk reference only |
| `rogue` | Agent/MCP/A2A behavior evaluation |
| `tracecat` | SOAR/agent security automation |
| `Viper` | Security product reference |

### UI

Desktop/web/mobile UI surfaces. These are likely more useful than hand-building
our own frontend.

UI reuse order:

1. `openclaw`: first candidate when we need an agent control UI or web surface.
2. `CodexMonitor`: first candidate for Codex workspace/thread/worktree views.
3. `agent-teams-ai`: first candidate for Kanban/team dashboard interaction.
4. `OpenHands`: first candidate for coding-agent runtime/server UI patterns.
5. `hermes-desktop` / `hermes-agent`: first candidate for desktop/TUI/web
   management patterns.

| Project | Notes |
|---|---|
| `openclaw` | Control UI and web surfaces are first UI reuse candidate |
| `CodexMonitor` | Codex workspace/thread/worktree UI is first Codex-native candidate |
| `agent-teams-ai` | Kanban/team desktop app and multi-agent dashboard |
| `hermes-desktop` | Hermes desktop installer/config/chat shell |
| `hermes-agent` | TUI/web/website surfaces |
| `OpenHands` | React local GUI and agent server UI |
| `OpenMOSS` | Static WebUI release and management model |
| `AionUi` | Desktop/mobile UI over command-line agents |
| `AFFiNE-canary` | Local-first document/whiteboard product |
| `CodexDesktop-Rebuild` | Codex Desktop packaging/reference |
| `gelab-zero` | GUI agent execution layer |
| `Mysti` | VS Code multi-agent coding assistant |
| `lobehub-canary` | Agent workspace/product surface |
| `plannotator` | Plan/diff review UI |
| `relaticle` | Agent-native CRM/MCP SaaS example |

### SDK

Official SDKs, model APIs, tokenizers, and model/tool references.

| Project | Notes |
|---|---|
| `openai-python` | Official OpenAI Python SDK |
| `anthropic-sdk-python` | Official Anthropic SDK and beta resources |
| `openai-cookbook` | Official OpenAI examples |
| `tiktoken` | Tokenizer/context budget reference |
| `CLIP` | OpenAI CLIP model reference |
| `whisper` | OpenAI Whisper model reference |

### Domain

Useful product/domain examples, but not first-line CoAgent infrastructure.

| Project | Notes |
|---|---|
| `ai-data-science-team` | Data-science agent team/product |
| `intentkit` | Cloud-native agent team/product reference |
| `terminal-velocity` | Creative multi-agent case study |
| `YC-Killer` | Industry agent scenario collection |

### Misc / Review Later

Do not start with these unless a task directly touches them.

| Project | Reason |
|---|---|
| `coding-interview-university` | General CS material, not CoAgent-specific |
| `Pearl` | RL library; not central to coding/department CoAgent |

## Physical Folder Plan

Use these folders and move in Git-safe batches:

```text
References/Agent/
  Platforms/
  Control/
  Gateway/
  Workflow/
  Skills/
  Memory/
  Security/
  UI/
  SDK/
  Domain/
  ReviewLater/
```

Current count by primary category:

- `Platforms`: 32
- `Control`: 15
- `Gateway`: 13
- `Workflow`: 18
- `Frameworks`: 18
- `Skills`: 27
- `Memory`: 26
- `Security`: 12
- `UI`: 13
- `SDK`: 6
- `Domain`: 7
- `ReviewLater`: 2

Before any physical move:

```bash
python3 Scripts/reference/check_reference_index.py --json --strict
rg "References/Agent/<project>" Docs CoAgent Scripts AGENTS.md PROGRESS.md
```

After each move, update:

- `CoAgent/docs/research/REFERENCE_PROJECT_INDEX.md`,
- this file,
- any `CoAgent/learning/audits/*` path references,
- scripts or docs discovered by `rg`.

## 2026-05-31 High-Star Import Batch

This batch was imported from `C:\Users\HP\Desktop\新建文件夹` after checking that the high-value crawl list had no obvious remaining gaps. Directory suffixes `-main` and `-master` were removed before moving. `lobehub-canary` was skipped because `References/Agent/UI/lobehub-canary` already existed.

| Category | Newly Added Projects | Why This Category |
|---|---|---|
| `Platforms` | `Agent-S`, `aider`, `AutoGPT`, `babyagi`, `cline`, `continue`, `gemini-cli`, `goose`, `open-interpreter`, `open-swe`, `OpenAgents`, `opencode-dev`, `openwork-dev`, `plandex`, `qwen-code`, `Roo-Code`, `SuperAGI`, `SWE-agent`, `tabby` | complete coding-agent or multi-agent products/runtimes |
| `Control` | `agency-swarm`, `trae-agent` | multi-agent coordination and task-control references |
| `Frameworks` | `agent-framework`, `agents`, `agno`, `pydantic-ai`, `semantic-kernel`, `smolagents` | general agent frameworks |
| `Memory` | `agentmemory`, `cognee`, `git-mcp`, `graphiti`, `khoj`, `letta`, `llama_index`, `mem0`, `onyx`, `OpenViking`, `quivr`, `repomix`, `supermemory`, `zep` | memory, context, repo understanding, graph/RAG references |
| `Gateway` | `awesome-mcp-servers`, `browser-use`, `composio-next`, `cua`, `daytona`, `E2B`, `firecrawl`, `inspector`, `mcp-use`, `playwright-mcp`, `servers`, `toolhive` | tool/MCP/browser/sandbox/human gateway references |
| `Workflow` | `agentops`, `dify`, `Flowise`, `helicone`, `langflow`, `langfuse`, `n8n`, `phoenix` | durable workflow, observability, eval, and automation references |
| `Security` | `agent-scan` | agent/MCP/security/eval references |
| `Skills` | `awesome-opencode`, `oh-my-openagent-dev` | skills, hooks, commands, plugins, and operator methods |
| `UI` | `open-webui`, `openchamber`, `opencode.nvim`, `superset` | desktop/web/editor UI surfaces |
| `Domain` | `fara`, `OpenCodeInterpreter`, `UFO` | domain-specific agent examples |

## Current Recommendation

Use this document as the routing map. The next implementation step should reuse
existing projects selectively:

1. inspect `Control/CodexMonitor`, `Control/OpenMOSS`, and
   `Control/agent-teams-ai` for frontend/control-plane and task-board reuse;
2. inspect `Control/ClawTeam`, `Control/AgentsMesh`, and `Control/OpenMOSS`
   for multi-agent control plane/task-board patterns;
3. inspect `Gateway/cc-connect` before hand-building notification, WeChat,
   or human-intervention gateway code;
4. inspect `Platforms/openclaw` and `Platforms/hermes-agent` for gateway,
   memory, scheduler, skill, hook, and operator-experience patterns;
5. inspect `Skills/AutoSkill`, `Skills/ECC`, and
   `Agent-Skills-for-Context-Engineering` for skill lifecycle and
   context-management migration;
6. inspect `Security/AI-Infra-Guard`, `Security/promptfoo`, and
   `Security/rogue` before enabling any
   unattended automation or MCP/tool expansion.
