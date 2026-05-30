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
  <upstream projects kept flat for now>
Docs/Index/agent_project_classification.md
  <capability classification, reuse priority, and future move plan>
CoAgent/docs/research/REFERENCE_PROJECT_INDEX.md
  <stable master coverage index for all References/>
```

Physical category folders are not created yet. Moving 114 upstream trees should
be a separate Git-batched task, because many existing docs and scripts still
refer to `References/Agent/<project>` paths.

## Target Categories

Use these short category names for study queues, future folders, and migration
planning.

| Category | Meaning |
|---|---|
| `platforms` | Full coding-agent or multi-agent products/runtimes that may contain reusable code |
| `control` | Team orchestration, task boards, worktrees, inboxes, dispatch, and visible-agent coordination |
| `workflow` | Durable state, checkpoints, specs, workflow engines, WAL/replay, task lifecycle |
| `frameworks` | General multi-agent frameworks to learn from, not import wholesale |
| `skills` | Skills, hooks, commands, plugins, rules, role packs, and operator methods |
| `memory` | RAG, repo indexes, graph memory, context assembly, search, knowledge bases |
| `security` | Red-team, eval, MCP/skill scanning, guardrails, SOC, governance |
| `ui` | Desktop/web/mobile UI surfaces, dashboards, Kanban, Codex App-like shells |
| `sdk` | Official SDKs, model APIs, tokenizers, model references |
| `domain` | Domain agent products or examples useful only for a specific scenario |
| `misc` | Low-priority, unclear, or currently unrelated material |

MCP is not a top-level category. Treat MCP as an interface inside the owning
category: search MCP belongs under `memory`, security MCP under `security`,
plugin MCP under `skills`, and MoSim Unreal/Epic MCPs stay under
`Docs/Skills/Unreal/`.

## Reuse Priority

### P0: Migration Candidates

Study first when implementing CoAgent. These are not just reading references;
they are candidates for direct adaptation.

| Project | Category | Reuse Target |
|---|---|---|
| `openclaw` | `platforms` | Control UI, session/workspace routing, skill/sandbox boundaries, gateway ideas |
| `CodexMonitor` | `ui` | Codex App/server workspace UI, thread state, worktree/clone agent management |
| `agent-teams-ai` | `control` | Kanban/team UI, agent-to-agent communication concepts, desktop app pattern |
| `OpenHands` | `platforms` | Coding-agent execution environment, web frontend, runtime/server split |
| `hermes-agent` | `platforms` | Memory, scheduler, skill evolution, messaging gateway, TUI/web surfaces |
| `hermes-desktop` | `ui` | Desktop wrapper and Hermes management UX ideas |
| `OpenMOSS` | `control` | AI-company/task/subtask/agent management backend model |
| `ClawTeam` | `control` | Worktree/tmux/agent inbox/task-board multi-agent CLI |
| `AgentsMesh` | `control` | Control-plane/data-plane split, AgentPods, distributed runner model |
| `codex` | `platforms` | Codex runtime, app-server, thread store, session/rollout, exec policy |

### P0: Architecture Foundations

Study first for design constraints and implementation contracts.

| Project | Category | Reuse Target |
|---|---|---|
| `langgraph` | `workflow` | State graph, checkpointing, HITL and durable execution patterns |
| `temporal` | `workflow` | Long-running workflow semantics and failure recovery |
| `sdk-python` | `workflow` | Temporal Python SDK usage patterns |
| `sdk-typescript` | `workflow` | Temporal TypeScript SDK usage patterns |
| `OpenSpec` | `workflow` | Spec/proposal/tasks workflow for controlled AI coding |
| `TaskWeaver` | `workflow` | Planner/executor state and data-analysis workflow separation |
| `antfarm` | `workflow` | Deterministic local team workflow, YAML/SQLite/fresh context |
| `ECC` | `skills` | Cross-client operator system, hooks, rules, skills, MCP config patterns |
| `context-engineering-kit` | `skills` | Context engineering, review/TDD/reflexion plugin patterns |
| `AutoSkill` | `skills` | Skill extraction, skill evolution, OpenClaw trajectory-to-skill ideas |
| `AI-Infra-Guard` | `security` | MCP/skill/agent security scanning and AI red-team controls |
| `promptfoo` | `security` | LLM eval/red-team baseline and CI-style checks |
| `rogue` | `security` | Agent/MCP/A2A behavior evaluation |
| `openai-agents-python` | `frameworks` | Official tool/handoff/guardrail/tracing primitives |
| `anthropic-sdk-python` | `sdk` | Anthropic beta resources, sessions, memory stores |
| `openai-skills` | `skills` | OpenAI/Codex skill format |
| `anthropics-skills` | `skills` | Anthropic skill templates and packaging |

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
| `lobehub-canary` | 7x24 agent operation/product surface |
| `AionUi` | Desktop/mobile UI over command-line agents |

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
| `antfarm` | Also workflow; useful for local team/task dispatch |

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
| `Pearl` | RL agent library; low relevance for CoAgent control plane |

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
| `openpencil` | Design product with agent team ideas |
| `terminal-velocity` | Creative multi-agent case study |
| `YC-Killer` | Industry agent scenario collection |
| `relaticle` | CRM domain example |

### Misc / Review Later

Do not start with these unless a task directly touches them.

| Project | Reason |
|---|---|
| `coding-interview-university` | General CS material, not CoAgent-specific |
| `Pearl` | RL library; not central to coding/department CoAgent |
| `CLIP` | Model reference only |
| `whisper` | Model reference only |
| `harness` | Needs deeper review before classification is trusted |
| `intentkit` | Product scope needs more review |

## Optional Physical Folder Plan

If physical sorting is approved later, use short folders and move in Git-safe
batches:

```text
References/Agent/
  platforms/
  control/
  workflow/
  frameworks/
  skills/
  memory/
  security/
  ui/
  sdk/
  domain/
  misc/
```

Do not move all 114 projects in one commit. Recommended batch order:

1. `ui`: `openclaw`, `CodexMonitor`, `agent-teams-ai`, `hermes-desktop`,
   `OpenHands`.
2. `platforms`: `codex`, `hermes-agent`, `openclaw`, `OpenHands`,
   `tinyagi`, `CowAgent`.
3. `skills`: `ECC`, `AutoSkill`, `Agent-Skills-for-Context-Engineering`,
   `openai-skills`, `anthropics-skills`, `SuperClaude_Framework`.
4. `security`: `AI-Infra-Guard`, `promptfoo`, `rogue`, `agentic_security`.
5. Remaining projects after updating every path reference.

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

## Current Recommendation

Keep `References/Agent` flat for now and use this document as the routing map.
The next implementation step should reuse existing projects selectively:

1. inspect `openclaw/ui`, `CodexMonitor`, and `agent-teams-ai` for frontend reuse;
2. inspect `ClawTeam`, `AgentsMesh`, and `OpenMOSS` for multi-agent control
   plane/task-board patterns;
3. inspect `AutoSkill`, `ECC`, and `Agent-Skills-for-Context-Engineering` for
   skill lifecycle and context-management migration;
4. inspect `AI-Infra-Guard`, `promptfoo`, and `rogue` before enabling any
   unattended automation or MCP/tool expansion.
