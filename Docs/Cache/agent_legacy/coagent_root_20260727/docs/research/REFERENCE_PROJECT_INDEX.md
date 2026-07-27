# Reference Project Index

> Stable index for all major external projects stored under `References/`.

## Purpose

Use this file before searching raw external trees. For MCP, browser automation,
tool gateway, docs lookup, or agent-runtime questions, check this index and the
local `References/Agent/Gateway`, `References/Agent/Memory`,
`References/Agent/Security`, and `References/Agent/Skills` mirrors before
opening web search or asking for download links.

The goal is to answer:

- what is in `References/`,
- why it is here,
- where to look first,
- which projects are architecture references,
- which are simulation references,
- which are parameter-identification/data references,
- which are local assets or official materials.

## Family Index

| Family | Path | Purpose |
|---|---|---|
| Agent systems | `References/Agent/` | Multi-agent architecture, runtime, memory, transport, workflow, skill/operator systems, safety/eval, SDK, UI, and orchestration references |
| UE / AirSim / simulator stacks | `References/AirSim/` | UE-based simulator and planner integration references |
| Blender / material references | `References/Blender` | Blender source, ArmorPaint, material/PBR, UV, and asset-preparation references |
| Gazebo source snapshots | `References/Gazebo/` | Gazebo / gazebosim source snapshots for simulator architecture, SDFormat, physics, sensors, rendering, transport, ROS bridge, tools, and docs; update workflow: `Docs/Workflows/reference_snapshot_update.md` |
| Logs / identification | `References/Log/` | PX4 logs, ULog tooling, ESC test, system identification, data-driven dynamics references |
| Planning / mapping labs | `References/Lab/` | EGO-Planner, FAST-LIO, GCOPTER, racing, swarm, mapping references |
| Official MWORKS materials | `References/MWORKS/` | Official competition case, docs, training materials, and reference examples |
| PX4 source | `References/PX4/` | Flight-stack and control/runtime reference |
| RflySim materials | `References/RflySim/` | RflySim packages and scene reference |
| ROS2 source snapshots | `References/ROS2/` | ROS2 organization source snapshots for client libraries, RMW/DDS layers, interfaces, launch, CLI, RViz, rosbag2, bridge, tracing, docs, and selected integration references; update workflow: `Docs/Workflows/reference_snapshot_update.md` |
| Sunray source | `References/Sunray/` | Sunray simulation, scripts, formation, communication, and physical-model references |
| Unreal scene projects | `References/UnrealScenes/` | Local editable UE scene projects for renderer/map work |
| Device/vendor assets | `References/CUAV/` | CUAV images and vendor-side visual/material assets |

## Project List

### Agent

| Project | Path | Primary Use |
|---|---|---|
| Agent family root | `References/Agent` | top-level entry for all agent/runtime references; route through `Docs/Index/agent_project_classification.md` before raw tree search |

| Agent category: Platforms | `References/Agent/Platforms` | complete coding-agent or multi-agent products/runtimes |
| Agent category: Control | `References/Agent/Control` | multi-agent coordination and task-control references |
| Agent category: Gateway | `References/Agent/Gateway` | tool/MCP/browser/sandbox/human gateway references |
| Agent category: Workflow | `References/Agent/Workflow` | durable workflow, observability, eval, and automation references |
| Agent category: Frameworks | `References/Agent/Frameworks` | general agent frameworks |
| Agent category: Skills | `References/Agent/Skills` | skills, hooks, commands, plugins, and operator methods |
| Agent category: Memory | `References/Agent/Memory` | memory, context, repo understanding, graph/RAG references |
| Agent category: Security | `References/Agent/Security` | agent/MCP/security/eval references |
| Agent category: UI | `References/Agent/UI` | desktop/web/editor UI surfaces |
| Agent category: SDK | `References/Agent/SDK` | SDKs and model/API references |
| Agent category: Domain | `References/Agent/Domain` | domain-specific agent examples |
| Agent category: ReviewLater | `References/Agent/ReviewLater` | low-priority or unclear references |

| Project | Path | Primary Use |
|---|---|---|
| AChat-canary | `References/Agent/Platforms/AChat-canary` | complete coding-agent or multi-agent products/runtimes reference |
| Agent-S | `References/Agent/Platforms/Agent-S` | GUI/OS agent reference |
| aider | `References/Agent/Platforms/aider` | terminal pair-programming agent |
| AutoGPT | `References/Agent/Platforms/AutoGPT` | classic autonomous agent platform |
| babyagi | `References/Agent/Platforms/babyagi` | classic task-loop agent |
| bifrost | `References/Agent/Platforms/bifrost` | complete coding-agent or multi-agent products/runtimes reference |
| claw-code | `References/Agent/Platforms/claw-code` | complete coding-agent or multi-agent products/runtimes reference |
| cline | `References/Agent/Platforms/cline` | VS Code autonomous coding agent |
| codex | `References/Agent/Platforms/codex` | complete coding-agent or multi-agent products/runtimes reference |
| continue | `References/Agent/Platforms/continue` | AI coding assistant/checks platform |
| CowAgent | `References/Agent/Platforms/CowAgent` | complete coding-agent or multi-agent products/runtimes reference |
| gemini-cli | `References/Agent/Platforms/gemini-cli` | Google terminal coding agent |
| goclaw-dev | `References/Agent/Platforms/goclaw-dev` | complete coding-agent or multi-agent products/runtimes reference |
| goose | `References/Agent/Platforms/goose` | extensible local coding/desktop agent |
| hermes-agent | `References/Agent/Platforms/hermes-agent` | complete coding-agent or multi-agent products/runtimes reference |
| moltis | `References/Agent/Platforms/moltis` | complete coding-agent or multi-agent products/runtimes reference |
| oh-my-pi | `References/Agent/Platforms/oh-my-pi` | full coding-agent/IDE/runtime reference with MCP, workflow, and operator-surface examples |
| open-interpreter | `References/Agent/Platforms/open-interpreter` | natural language computer interface; AGPL study only |
| open-swe | `References/Agent/Platforms/open-swe` | asynchronous coding agent |
| OpenAgents | `References/Agent/Platforms/OpenAgents` | language-agent platform research |
| openclaw | `References/Agent/Platforms/openclaw` | complete coding-agent or multi-agent products/runtimes reference |
| opencode-dev | `References/Agent/Platforms/opencode-dev` | current opencode coding-agent source |
| OpenHands | `References/Agent/Platforms/OpenHands` | complete coding-agent or multi-agent products/runtimes reference |
| openwork-dev | `References/Agent/Platforms/openwork-dev` | OpenCode-based desktop/orchestrator UI |
| plandex | `References/Agent/Platforms/plandex` | large-project coding agent |
| qwen-code | `References/Agent/Platforms/qwen-code` | Qwen terminal coding agent |
| Roo-Code | `References/Agent/Platforms/Roo-Code` | IDE coding agent with team modes |
| spacebot | `References/Agent/Platforms/spacebot` | complete coding-agent or multi-agent products/runtimes reference |
| SuperAGI | `References/Agent/Platforms/SuperAGI` | classic autonomous-agent platform |
| SWE-agent | `References/Agent/Platforms/SWE-agent` | issue-to-fix coding agent |
| tabby | `References/Agent/Platforms/tabby` | self-hosted coding assistant |
| tinyagi | `References/Agent/Platforms/tinyagi` | complete coding-agent or multi-agent products/runtimes reference |
| zylos-core | `References/Agent/Platforms/zylos-core` | complete coding-agent or multi-agent products/runtimes reference |
| agency-swarm | `References/Agent/Control/agency-swarm` | agency-style multi-agent orchestration framework |
| agent-teams-ai | `References/Agent/Control/agent-teams-ai` | multi-agent coordination and task-control references reference |
| AgentsMesh | `References/Agent/Control/AgentsMesh` | multi-agent coordination and task-control references reference |
| agor | `References/Agent/Control/agor` | multi-agent coordination and task-control references reference |
| AutoGroq | `References/Agent/Control/AutoGroq` | multi-agent coordination and task-control references reference |
| ClawTeam | `References/Agent/Control/ClawTeam` | multi-agent coordination and task-control references reference |
| ClawTeam-OpenClaw | `References/Agent/Control/ClawTeam-OpenClaw` | multi-agent coordination and task-control references reference |
| CodexMonitor | `References/Agent/Control/CodexMonitor` | multi-agent coordination and task-control references reference |
| oh-my-agent | `References/Agent/Control/oh-my-agent` | multi-agent coordination and task-control references reference |
| oh-my-claudecode | `References/Agent/Control/oh-my-claudecode` | multi-agent coordination and task-control references reference |
| oh-my-codex | `References/Agent/Control/oh-my-codex` | multi-agent coordination and task-control references reference |
| OpenMOSS | `References/Agent/Control/OpenMOSS` | multi-agent coordination and task-control references reference |
| squad-dev | `References/Agent/Control/squad-dev` | multi-agent coordination and task-control references reference |
| symphony | `References/Agent/Control/symphony` | multi-agent coordination and task-control references reference |
| trae-agent | `References/Agent/Control/trae-agent` | software-engineering agent from ByteDance |
| awesome-mcp-servers | `References/Agent/Gateway/awesome-mcp-servers` | MCP server index |
| browser-use | `References/Agent/Gateway/browser-use` | browser automation for AI agents |
| cc-connect | `References/Agent/Gateway/cc-connect` | tool/MCP/browser/sandbox/human gateway references reference |
| composio-next | `References/Agent/Gateway/composio-next` | tool/auth/sandbox integration platform |
| cua | `References/Agent/Gateway/cua` | computer-use automation reference |
| daytona | `References/Agent/Gateway/daytona` | secure dev environment for generated code |
| E2B | `References/Agent/Gateway/E2B` | secure execution environment for agents |
| firecrawl | `References/Agent/Gateway/firecrawl` | web crawl/search API reference; AGPL study only |
| github-mcp-server | `References/Agent/Gateway/github-mcp-server` | official GitHub MCP server reference for GitHub API/toolset design |
| inspector | `References/Agent/Gateway/inspector` | MCP inspector visual testing tool |
| mcp-use | `References/Agent/Gateway/mcp-use` | MCP app/server framework |
| playwright-mcp | `References/Agent/Gateway/playwright-mcp` | browser automation MCP server |
| playwright-mcp-upstream-snapshot-20260606 | `References/Agent/Gateway/playwright-mcp-upstream-snapshot-20260606` | duplicate upstream snapshot retained for dedupe review; primary route remains `playwright-mcp` |
| servers | `References/Agent/Gateway/servers` | official/community MCP servers collection |
| servers-upstream-snapshot-20260606 | `References/Agent/Gateway/servers-upstream-snapshot-20260606` | newer upstream snapshot retained for dedupe review; primary route remains `servers` until reviewed |
| toolhive | `References/Agent/Gateway/toolhive` | MCP server management/security platform |
| agentops | `References/Agent/Workflow/agentops` | agent monitoring/cost/benchmarking |
| antfarm | `References/Agent/Workflow/antfarm` | durable workflow, observability, eval, and automation references reference |
| dify | `References/Agent/Workflow/dify` | agent/app workflow platform |
| Flowise | `References/Agent/Workflow/Flowise` | visual LLM workflow builder |
| harness | `References/Agent/Workflow/harness` | durable workflow, observability, eval, and automation references reference |
| helicone | `References/Agent/Workflow/helicone` | LLM observability platform |
| langflow | `References/Agent/Workflow/langflow` | visual agent/RAG builder |
| langfuse | `References/Agent/Workflow/langfuse` | LLM observability/eval/prompt management |
| langgraph | `References/Agent/Workflow/langgraph` | durable workflow, observability, eval, and automation references reference |
| mlflow | `References/Agent/Workflow/mlflow` | durable workflow, observability, eval, and automation references reference |
| n8n | `References/Agent/Workflow/n8n` | workflow automation platform |
| okwinds | `References/Agent/Workflow/okwinds` | durable workflow, observability, eval, and automation references reference |
| OpenSpec | `References/Agent/Workflow/OpenSpec` | durable workflow, observability, eval, and automation references reference |
| phoenix | `References/Agent/Workflow/phoenix` | AI observability/evaluation platform |
| sdk-python | `References/Agent/Workflow/sdk-python` | durable workflow, observability, eval, and automation references reference |
| sdk-typescript | `References/Agent/Workflow/sdk-typescript` | durable workflow, observability, eval, and automation references reference |
| TaskWeaver | `References/Agent/Workflow/TaskWeaver` | durable workflow, observability, eval, and automation references reference |
| temporal | `References/Agent/Workflow/temporal` | durable workflow, observability, eval, and automation references reference |
| ag2 | `References/Agent/Frameworks/ag2` | general agent frameworks reference |
| agent-framework | `References/Agent/Frameworks/agent-framework` | Microsoft Agent Framework reference |
| agents | `References/Agent/Frameworks/agents` | Cloudflare Agents runtime reference |
| agno | `References/Agent/Frameworks/agno` | agent platform framework |
| autogen | `References/Agent/Frameworks/autogen` | general agent frameworks reference |
| camel | `References/Agent/Frameworks/camel` | general agent frameworks reference |
| crewAI | `References/Agent/Frameworks/crewAI` | general agent frameworks reference |
| haystack | `References/Agent/Frameworks/haystack` | general agent frameworks reference |
| langchain | `References/Agent/Frameworks/langchain` | general agent frameworks reference |
| llama-agents | `References/Agent/Frameworks/llama-agents` | general agent frameworks reference |
| mastra | `References/Agent/Frameworks/mastra` | general agent frameworks reference |
| MetaGPT | `References/Agent/Frameworks/MetaGPT` | general agent frameworks reference |
| NeMo-Agent-Toolkit-develop | `References/Agent/Frameworks/NeMo-Agent-Toolkit-develop` | general agent frameworks reference |
| openai-agents-python | `References/Agent/Frameworks/openai-agents-python` | general agent frameworks reference |
| pydantic-ai | `References/Agent/Frameworks/pydantic-ai` | Pydantic agent framework |
| semantic-kernel | `References/Agent/Frameworks/semantic-kernel` | Microsoft Semantic Kernel agent framework |
| smolagents | `References/Agent/Frameworks/smolagents` | Hugging Face code-agent framework |
| swarm | `References/Agent/Frameworks/swarm` | general agent frameworks reference |
| agent-skills | `References/Agent/Skills/agent-skills` | skills, hooks, commands, plugins, and operator methods reference |
| Agent-Skills-for-Context-Engineering | `References/Agent/Skills/Agent-Skills-for-Context-Engineering` | skills, hooks, commands, plugins, and operator methods reference |
| andrej-karpathy-skills | `References/Agent/Skills/andrej-karpathy-skills` | skills, hooks, commands, plugins, and operator methods reference |
| anthropics-skills | `References/Agent/Skills/anthropics-skills` | skills, hooks, commands, plugins, and operator methods reference |
| AutoSkill | `References/Agent/Skills/AutoSkill` | skills, hooks, commands, plugins, and operator methods reference |
| Awesome-Agent-Skills | `References/Agent/Skills/Awesome-Agent-Skills` | skills, hooks, commands, plugins, and operator methods reference |
| awesome-claude-agents | `References/Agent/Skills/awesome-claude-agents` | skills, hooks, commands, plugins, and operator methods reference |
| awesome-codex-skills | `References/Agent/Skills/awesome-codex-skills` | skills, hooks, commands, plugins, and operator methods reference |
| awesome-codex-subagents | `References/Agent/Skills/awesome-codex-subagents` | skills, hooks, commands, plugins, and operator methods reference |
| awesome-openclaw-skills | `References/Agent/Skills/awesome-openclaw-skills` | skills, hooks, commands, plugins, and operator methods reference |
| awesome-opencode | `References/Agent/Skills/awesome-opencode` | OpenCode plugins/themes/agents index |
| claude-plugins-official | `References/Agent/Skills/claude-plugins-official` | skills, hooks, commands, plugins, and operator methods reference |
| codex-plugin-cc | `References/Agent/Skills/codex-plugin-cc` | skills, hooks, commands, plugins, and operator methods reference |
| context-engineering-kit | `References/Agent/Skills/context-engineering-kit` | skills, hooks, commands, plugins, and operator methods reference |
| ECC | `References/Agent/Skills/ECC` | skills, hooks, commands, plugins, and operator methods reference |
| HeavySkill | `References/Agent/Skills/HeavySkill` | skills, hooks, commands, plugins, and operator methods reference |
| mattpocock-skills | `References/Agent/Skills/mattpocock-skills` | skills, hooks, commands, plugins, and operator methods reference |
| MMSkills | `References/Agent/Skills/MMSkills` | skills, hooks, commands, plugins, and operator methods reference |
| oh-my-openagent-dev | `References/Agent/Skills/oh-my-openagent-dev` | OpenCode/Codex/Pi harness and skill collection |
| openai-skills | `References/Agent/Skills/openai-skills` | skills, hooks, commands, plugins, and operator methods reference |
| pro-workflow | `References/Agent/Skills/pro-workflow` | skills, hooks, commands, plugins, and operator methods reference |
| SkillRouter | `References/Agent/Skills/SkillRouter` | skills, hooks, commands, plugins, and operator methods reference |
| SkillX | `References/Agent/Skills/SkillX` | skills, hooks, commands, plugins, and operator methods reference |
| SR-Agents | `References/Agent/Skills/SR-Agents` | skills, hooks, commands, plugins, and operator methods reference |
| SSL | `References/Agent/Skills/SSL` | skills, hooks, commands, plugins, and operator methods reference |
| SuperClaude_Framework | `References/Agent/Skills/SuperClaude_Framework` | skills, hooks, commands, plugins, and operator methods reference |
| superpowers | `References/Agent/Skills/superpowers` | skills, hooks, commands, plugins, and operator methods reference |
| agentmemory | `References/Agent/Memory/agentmemory` | persistent memory for AI coding agents |
| anysearch-mcp-server | `References/Agent/Memory/anysearch-mcp-server` | memory, context, repo understanding, graph/RAG references reference |
| anysearch-skill | `References/Agent/Memory/anysearch-skill` | memory, context, repo understanding, graph/RAG references reference |
| cognee | `References/Agent/Memory/cognee` | memory control plane/graph memory |
| context7 | `References/Agent/Memory/context7` | memory, context, repo understanding, graph/RAG references reference |
| csghub | `References/Agent/Memory/csghub` | memory, context, repo understanding, graph/RAG references reference |
| deepwiki-rs | `References/Agent/Memory/deepwiki-rs` | memory, context, repo understanding, graph/RAG references reference |
| docs-mcp-server | `References/Agent/Memory/docs-mcp-server` | memory, context, repo understanding, graph/RAG references reference |
| git-mcp | `References/Agent/Memory/git-mcp` | GitHub repository context MCP |
| graphify-8 | `References/Agent/Memory/graphify-8` | memory, context, repo understanding, graph/RAG references reference |
| graphiti | `References/Agent/Memory/graphiti` | real-time knowledge graph memory |
| GraphRAG | `References/Agent/Memory/GraphRAG` | memory, context, repo understanding, graph/RAG references reference |
| khoj | `References/Agent/Memory/khoj` | personal/team knowledge base and agent automation |
| letta | `References/Agent/Memory/letta` | stateful agents with memory |
| llama_index | `References/Agent/Memory/llama_index` | document agent and indexing framework |
| mem0 | `References/Agent/Memory/mem0` | universal memory layer |
| onyx | `References/Agent/Memory/onyx` | enterprise search/RAG platform |
| openpencil | `References/Agent/Memory/openpencil` | memory, context, repo understanding, graph/RAG references reference |
| OpenViking | `References/Agent/Memory/OpenViking` | agent context database; AGPL study only |
| quivr | `References/Agent/Memory/quivr` | RAG product reference |
| RepoAgent | `References/Agent/Memory/RepoAgent` | memory, context, repo understanding, graph/RAG references reference |
| repomix | `References/Agent/Memory/repomix` | repo packing for LLM context |
| supermemory | `References/Agent/Memory/supermemory` | memory API/product reference |
| SurfSense | `References/Agent/Memory/SurfSense` | memory, context, repo understanding, graph/RAG references reference |
| vexa | `References/Agent/Memory/vexa` | memory, context, repo understanding, graph/RAG references reference |
| zep | `References/Agent/Memory/zep` | agent memory examples/integrations |
| agent-scan | `References/Agent/Security/agent-scan` | agent/MCP/skill security scanner |
| agentic_security | `References/Agent/Security/agentic_security` | agent/MCP/security/eval references reference |
| AI-Infra-Guard | `References/Agent/Security/AI-Infra-Guard` | agent/MCP/security/eval references reference |
| AiSOC | `References/Agent/Security/AiSOC` | agent/MCP/security/eval references reference |
| Decepticon | `References/Agent/Security/Decepticon` | agent/MCP/security/eval references reference |
| LitterBox | `References/Agent/Security/LitterBox` | agent/MCP/security/eval references reference |
| pentestagent | `References/Agent/Security/pentestagent` | agent/MCP/security/eval references reference |
| promptfoo | `References/Agent/Security/promptfoo` | agent/MCP/security/eval references reference |
| redamon | `References/Agent/Security/redamon` | agent/MCP/security/eval references reference |
| rogue | `References/Agent/Security/rogue` | agent/MCP/security/eval references reference |
| tracecat | `References/Agent/Security/tracecat` | agent/MCP/security/eval references reference |
| Viper | `References/Agent/Security/Viper` | agent/MCP/security/eval references reference |
| AFFiNE-canary | `References/Agent/UI/AFFiNE-canary` | desktop/web/editor UI surfaces reference |
| AionUi | `References/Agent/UI/AionUi` | desktop/web/editor UI surfaces reference |
| CodexDesktop-Rebuild | `References/Agent/UI/CodexDesktop-Rebuild` | desktop/web/editor UI surfaces reference |
| gelab-zero | `References/Agent/UI/gelab-zero` | desktop/web/editor UI surfaces reference |
| hermes-desktop | `References/Agent/UI/hermes-desktop` | desktop/web/editor UI surfaces reference |
| lobehub-canary | `References/Agent/UI/lobehub-canary` | desktop/web/editor UI surfaces reference |
| Mysti | `References/Agent/UI/Mysti` | desktop/web/editor UI surfaces reference |
| open-webui | `References/Agent/UI/open-webui` | web chat/agent UI product |
| openchamber | `References/Agent/UI/openchamber` | OpenCode ecosystem UI/reference |
| opencode.nvim | `References/Agent/UI/opencode.nvim` | Neovim client for opencode |
| plannotator | `References/Agent/UI/plannotator` | desktop/web/editor UI surfaces reference |
| relaticle | `References/Agent/UI/relaticle` | desktop/web/editor UI surfaces reference |
| superset | `References/Agent/UI/superset` | multi-agent workspace/control UI reference |
| anthropic-sdk-python | `References/Agent/SDK/anthropic-sdk-python` | SDKs and model/API references reference |
| CLIP | `References/Agent/SDK/CLIP` | SDKs and model/API references reference |
| openai-cookbook | `References/Agent/SDK/openai-cookbook` | SDKs and model/API references reference |
| openai-python | `References/Agent/SDK/openai-python` | SDKs and model/API references reference |
| tiktoken | `References/Agent/SDK/tiktoken` | SDKs and model/API references reference |
| whisper | `References/Agent/SDK/whisper` | SDKs and model/API references reference |
| ai-data-science-team | `References/Agent/Domain/ai-data-science-team` | domain-specific agent examples reference |
| fara | `References/Agent/Domain/fara` | domain agent/reference project |
| intentkit | `References/Agent/Domain/intentkit` | domain-specific agent examples reference |
| OpenCodeInterpreter | `References/Agent/Domain/OpenCodeInterpreter` | code generation/execution/refinement research model |
| terminal-velocity | `References/Agent/Domain/terminal-velocity` | domain-specific agent examples reference |
| UFO | `References/Agent/Domain/UFO` | Microsoft OS-level desktop automation agent |
| YC-Killer | `References/Agent/Domain/YC-Killer` | domain-specific agent examples reference |
| ChatGPT-Exporter-main | `References/Agent/ReviewLater/ChatGPT-Exporter-main` | chat export utility; low-priority and not first-line CoAgent/MCP infrastructure |
| coding-interview-university | `References/Agent/ReviewLater/coding-interview-university` | low-priority or unclear references reference |
| Pearl | `References/Agent/ReviewLater/Pearl` | low-priority or unclear references reference |

### AirSim

| Project | Path | Primary Use |
|---|---|---|
| AirSim family root | `References/AirSim` | top-level entry for UE-based simulator references |
| Project | Path | Primary Use |
|---|---|---|
| AirSim | `References/AirSim/AirSim` | baseline Microsoft AirSim reference |
| AirSim360 | `References/AirSim/AirSim360` | 360 / panoramic related reference |
| Cosys-AirSim | `References/AirSim/Cosys-AirSim` | commercial AirSim derivative reference |
| IsaacSim | `References/AirSim/IsaacSim` | NVIDIA simulator reference |
| PEDRA | `References/AirSim/PEDRA` | RL/planning simulator reference |
| PegasusSimulator | `References/AirSim/PegasusSimulator` | simulator/runtime reference |
| ProjectAirSim | `References/AirSim/ProjectAirSim` | new AirSim branch reference |
| UESVONavigation-develop | `References/AirSim/UESVONavigation-develop` | UE navigation/planning reference |
| carla-ue5-dev | `References/AirSim/carla-ue5-dev` | UE5 CARLA source/map reference |
| spear | `References/AirSim/spear` | simulation/runtime reference |
| unrealcv-5.2 | `References/AirSim/unrealcv-5.2` | UE CV/rendering interface reference |

### Log

| Project | Path | Primary Use |
|---|---|---|
| Log family root | `References/Log` | top-level entry for logs and identification references |
| airo_control_interface | `References/Log/airo_control_interface` | control interface reference |
| data-driven-dynamics | `References/Log/data-driven-dynamics` | model/dynamics identification reference |
| data-driven-system-identification | `References/Log/data-driven-system-identification` | system identification reference |
| esc_test | `References/Log/esc_test` | ESC/motor measurement reference |
| px4_pid_tuner | `References/Log/px4_pid_tuner` | PX4 log-based tuning reference |
| px4tools | `References/Log/px4tools` | PX4 log parsing/reference |
| pyulog | `References/Log/pyulog` | ULog parsing/reference |

### Lab

| Project | Path | Primary Use |
|---|---|---|
| Lab family root | `References/Lab` | top-level entry for planning, mapping, and swarm lab references |
| Project | Path | Primary Use |
|---|---|---|
| EGO-Planner-v2 | `References/Lab/EGO-Planner-v2` | local replanning reference |
| FAST-LIVO2 | `References/Lab/FAST-LIVO2` | lidar-visual inertial odometry reference |
| FAST_LIO | `References/Lab/FAST_LIO` | lidar odometry/mapping reference |
| Fast-Racing | `References/Lab/Fast-Racing` | high-speed planning/control reference |
| GCOPTER | `References/Lab/GCOPTER` | trajectory optimization reference |
| Point-LIO-point-lio-with-grid-map | `References/Lab/Point-LIO-point-lio-with-grid-map` | point-lio and grid map reference |
| SUPER | `References/Lab/SUPER` | swarm/perception/planning reference |
| ego-planner | `References/Lab/ego-planner` | local replanning reference |
| ego-planner-swarm | `References/Lab/ego-planner-swarm` | multi-UAV planning reference |

### MWORKS

| Project | Path | Primary Use |
|---|---|---|
| MWORKS family root | `References/MWORKS` | top-level entry for official MWORKS materials |
| Project | Path | Primary Use |
|---|---|---|
| 2025中国大学生软件设计大赛 | `References/MWORKS/2025中国大学生软件设计大赛` | competition background materials |
| MWORKS高校星火计划资料包 | `References/MWORKS/MWORKS高校星火计划资料包` | official docs/material package |
| QuadrotorModel | `References/MWORKS/QuadrotorModel` | official quadrotor case |
| 具身智能无人船平台部署资料 | `References/MWORKS/具身智能无人船平台部署资料` | communication/ROS/MWORKS reference |
| 智能无人系统应用挑战赛培训配套文档及案例 | `References/MWORKS/智能无人系统应用挑战赛培训配套文档及案例` | official challenge training reference |
| 用于远程巡逻及异常检测的智能无人机 | `References/MWORKS/用于远程巡逻及异常检测的智能无人机` | auxiliary reference |

### Other Families

| Project | Path | Primary Use |
|---|---|---|
| PX4 | `References/PX4` | flight-stack reference |
| Blender / material family | `References/Blender` | Blender source, material/PBR, UV, and asset-preparation references |
| Log family already listed above | `References/Log` | identification/log-tool root |
| RflySimAdv3Full | `References/RflySim/RflySimAdv3Full` | scene/runtime reference |
| RflySimAdvFree | `References/RflySim/RflySimAdvFree` | free package reference |
| Sunray simulation tree | `References/Sunray` | Sunray source and simulation reference |
| Unreal scene root | `References/UnrealScenes` | local UE scene source pool root |
| ABoyandHisKite | `References/UnrealScenes/ABoyandHisKite` | large outdoor UE scene source |
| CityParkEnvironmentCollec | `References/UnrealScenes/CityParkEnvironmentCollec` | park/open scene source |
| CitySample | `References/UnrealScenes/CitySample` | large-scale city scene source |
| DarkRuinsMegascansSample | `References/UnrealScenes/DarkRuinsMegascansSample` | ruins/cave scene source |
| DerelictCorridorMegascans | `References/UnrealScenes/DerelictCorridorMegascans` | industrial corridor scene source |
| ElectricDreamsEnv | `References/UnrealScenes/ElectricDreamsEnv` | high-quality forest/PCG scene source |
| FPS-Shooter-Unreal | `References/UnrealScenes/FPS-Shooter-Unreal` | shooter/factory reference project |
| FactoryEnvironmentCollect | `References/UnrealScenes/FactoryEnvironmentCollect` | factory scene source |
| MedievalVillageMegascansS | `References/UnrealScenes/MedievalVillageMegascansS` | village scene source |
| ProceduralDungeon | `References/UnrealScenes/ProceduralDungeon` | procedural indoor scene source |
| UE5-MazeGenerator-Plugin | `References/UnrealScenes/UE5-MazeGenerator-Plugin` | maze/dungeon generation reference |
| mine_raw | `References/UnrealScenes/mine_raw` | mine/raw scene source |
| CUAV assets | `References/CUAV` | vendor image/material references |

## First-Read Priority

If the task is about agent architecture:

1. `CoAgent/docs/research/LEARNING_STRATEGY.md`
2. `References/Agent/Platforms/codex`
3. `References/Agent/Platforms/hermes-agent`
4. `References/Agent/UI/hermes-desktop`
5. `References/Agent/SDK/anthropic-sdk-python/src/anthropic/resources/beta`
6. `References/Agent/Platforms/openclaw`
7. `References/Agent/Workflow/okwinds`
8. `Docs/Index/agent_project_classification.md`

If the task is about long-context degradation, context packs, or durable agent
memory:

1. `CoAgent/docs/research/LEARNING_STRATEGY.md`
2. `References/Agent/SDK/anthropic-sdk-python/src/anthropic/resources/beta/memory_stores`
3. `References/Agent/SDK/anthropic-sdk-python/src/anthropic/resources/beta/sessions`
4. `References/Agent/Platforms/codex`
5. `References/Agent/Platforms/hermes-agent`
6. `Docs/Index/agent_project_classification.md`

If the task is about simulator/UE scene architecture:

1. `References/AirSim/Cosys-AirSim`
2. `References/AirSim/AirSim`
3. `References/AirSim/PegasusSimulator`
4. `References/AirSim/ProjectAirSim`
5. `References/UnrealScenes`
6. `References/RflySim`

If the task is about parameter identification:

1. `References/Log/pyulog`
2. `References/Log/px4tools`
3. `References/Log/px4_pid_tuner`
4. `References/Log/data-driven-dynamics`
5. `References/Log/data-driven-system-identification`

If the task is about planning/mapping:

1. `References/Lab/ego-planner`
2. `References/Lab/EGO-Planner-v2`
3. `References/Lab/Fast-Racing`
4. `References/Lab/FAST_LIO`
5. `References/Lab/FAST-LIVO2`
6. `References/Lab/GCOPTER`

## Maintenance Rule

When new reference projects are added:

1. add them to this index,
2. classify them by family,
3. state why they are here,
4. mark the first-read priority if relevant.

Do not rely on ad-hoc `find`/`rg` over the raw `References/` tree as the normal
entry point once this index exists.
