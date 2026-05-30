# Reference Project Index

> Stable index for all major external projects stored under `References/`.

## Purpose

Use this file before searching raw external trees.

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
| Logs / identification | `References/Log/` | PX4 logs, ULog tooling, ESC test, system identification, data-driven dynamics references |
| Planning / mapping labs | `References/Lab/` | EGO-Planner, FAST-LIO, GCOPTER, racing, swarm, mapping references |
| Official MWORKS materials | `References/MWORKS/` | Official competition case, docs, training materials, and reference examples |
| PX4 source | `References/PX4/` | Flight-stack and control/runtime reference |
| RflySim materials | `References/RflySim/` | RflySim packages and scene reference |
| Sunray source | `References/Sunray/` | Sunray simulation, scripts, formation, communication, and physical-model references |
| Unreal scene projects | `References/UnrealScenes/` | Local editable UE scene projects for renderer/map work |
| Device/vendor assets | `References/CUAV/` | CUAV images and vendor-side visual/material assets |

## Project List

### Agent

| Project | Path | Primary Use |
|---|---|---|
| Agent family root | `References/Agent` | top-level entry for all agent/runtime references; route through `Docs/Index/agent_project_classification.md` before raw tree search |

| Agent category: Platforms | `References/Agent/Platforms` | complete agent products, runtimes, and gateway/platform systems |
| Agent category: Control | `References/Agent/Control` | multi-agent coordination, task boards, worktrees, departments, and communication |
| Agent category: Workflow | `References/Agent/Workflow` | durable workflows, state machines, checkpoints, WAL, and spec flows |
| Agent category: Frameworks | `References/Agent/Frameworks` | general multi-agent frameworks and reusable agent app frameworks |
| Agent category: Skills | `References/Agent/Skills` | skills, hooks, commands, plugins, role packs, and operator methods |
| Agent category: Memory | `References/Agent/Memory` | context retrieval, RAG, documentation indexes, knowledge graphs, and repo understanding |
| Agent category: Security | `References/Agent/Security` | evals, red-team, safety, MCP/skill scanning, and governance |
| Agent category: UI | `References/Agent/UI` | desktop/web/mobile UI surfaces and dashboards |
| Agent category: SDK | `References/Agent/SDK` | SDKs, model APIs, tokenizers, and model references |
| Agent category: Domain | `References/Agent/Domain` | domain-specific agent examples |
| Agent category: ReviewLater | `References/Agent/ReviewLater` | unclear or low-priority projects for later review |
| Project | Path | Primary Use |
|---|---|---|
| AFFiNE-canary | `References/Agent/UI/AFFiNE-canary` | agent/product architecture reference |
| CowAgent | `References/Agent/Platforms/CowAgent` | agent orchestration reference |
| MetaGPT | `References/Agent/Frameworks/MetaGPT` | role-based software-company agent reference |
| OpenHands | `References/Agent/Platforms/OpenHands` | coding-agent runtime reference |
| OpenSpec | `References/Agent/Workflow/OpenSpec` | spec-driven workflow reference |
| TaskWeaver | `References/Agent/Workflow/TaskWeaver` | planner/executor workflow reference |
| ag2 | `References/Agent/Frameworks/ag2` | multi-agent framework reference |
| anthropic-sdk-python | `References/Agent/SDK/anthropic-sdk-python` | SDK/client and agent integration reference |
| autogen | `References/Agent/Frameworks/autogen` | multi-agent framework reference |
| camel | `References/Agent/Frameworks/camel` | agent society/workflow reference |
| claw-code | `References/Agent/Platforms/claw-code` | coding-agent reference |
| codex | `References/Agent/Platforms/codex` | Codex source, app-server, thread-store, rollout, skills, execpolicy reference |
| coding-interview-university | `References/Agent/ReviewLater/coding-interview-university` | general CS reference, low priority |
| crewAI | `References/Agent/Frameworks/crewAI` | crew/task orchestration reference |
| haystack | `References/Agent/Frameworks/haystack` | agent/search pipeline reference |
| hermes-agent | `References/Agent/Platforms/hermes-agent` | durable agent runtime, gateway, memory, skills, scheduler reference |
| hermes-desktop | `References/Agent/UI/hermes-desktop` | Hermes desktop/client surface reference |
| langchain | `References/Agent/Frameworks/langchain` | chain/tool abstraction reference |
| langgraph | `References/Agent/Workflow/langgraph` | graph-based agent orchestration reference |
| llama-agents | `References/Agent/Frameworks/llama-agents` | distributed agent architecture reference |
| okwinds | `References/Agent/Workflow/okwinds` | workflow/runtime/WAL ideas reference |
| openclaw | `References/Agent/Platforms/openclaw` | predecessor-style coding-agent/runtime reference |
| sdk-typescript | `References/Agent/Workflow/sdk-typescript` | TS SDK/interface reference |
| temporal | `References/Agent/Workflow/temporal` | durable workflow runtime reference |
| AChat-canary | `References/Agent/Platforms/AChat-canary` | crawled agent/project reference pending detailed classification |
| AI-Infra-Guard | `References/Agent/Security/AI-Infra-Guard` | crawled agent/project reference pending detailed classification |
| Agent-Skills-for-Context-Engineering | `References/Agent/Skills/Agent-Skills-for-Context-Engineering` | context engineering and skill reference |
| AutoSkill | `References/Agent/Skills/AutoSkill` | automatic skill discovery/evolution reference |
| Awesome-Agent-Skills | `References/Agent/Skills/Awesome-Agent-Skills` | agent skill collection reference |
| AgentsMesh | `References/Agent/Control/AgentsMesh` | crawled multi-agent/runtime reference pending detailed classification |
| AiSOC | `References/Agent/Security/AiSOC` | security/agent operations reference pending detailed classification |
| AionUi | `References/Agent/UI/AionUi` | agent UI/product reference pending detailed classification |
| AutoGroq | `References/Agent/Control/AutoGroq` | agent workflow reference pending detailed classification |
| CLIP | `References/Agent/SDK/CLIP` | model/tooling reference pending detailed classification |
| ClawTeam | `References/Agent/Control/ClawTeam` | Claw/OpenClaw ecosystem reference |
| ClawTeam-OpenClaw | `References/Agent/Control/ClawTeam-OpenClaw` | OpenClaw ecosystem reference |
| CodexDesktop-Rebuild | `References/Agent/UI/CodexDesktop-Rebuild` | Codex desktop/UI reference pending detailed classification |
| CodexMonitor | `References/Agent/Control/CodexMonitor` | Codex monitoring/reference tooling pending detailed classification |
| Decepticon | `References/Agent/Security/Decepticon` | crawled agent/project reference pending detailed classification |
| ECC | `References/Agent/Skills/ECC` | crawled agent/project reference pending detailed classification |
| LitterBox | `References/Agent/Security/LitterBox` | crawled agent/project reference pending detailed classification |
| Mysti | `References/Agent/UI/Mysti` | crawled agent/project reference pending detailed classification |
| NeMo-Agent-Toolkit-develop | `References/Agent/Frameworks/NeMo-Agent-Toolkit-develop` | NVIDIA agent toolkit reference |
| OpenMOSS | `References/Agent/Control/OpenMOSS` | multi-agent/open-source agent reference pending detailed classification |
| Pearl | `References/Agent/ReviewLater/Pearl` | crawled agent/project reference pending detailed classification |
| RepoAgent | `References/Agent/Memory/RepoAgent` | repository agent/documentation reference |
| SuperClaude_Framework | `References/Agent/Skills/SuperClaude_Framework` | Claude workflow/command framework reference |
| SurfSense | `References/Agent/Memory/SurfSense` | research/search agent reference pending detailed classification |
| Viper | `References/Agent/Security/Viper` | crawled agent/project reference pending detailed classification |
| YC-Killer | `References/Agent/Domain/YC-Killer` | crawled agent/product reference pending detailed classification |
| agent-skills | `References/Agent/Skills/agent-skills` | agent skills reference |
| agent-teams-ai | `References/Agent/Control/agent-teams-ai` | agent team architecture reference |
| agentic_security | `References/Agent/Security/agentic_security` | agent security reference |
| agor | `References/Agent/Control/agor` | crawled agent/project reference pending detailed classification |
| ai-data-science-team | `References/Agent/Domain/ai-data-science-team` | data-science agent team reference |
| andrej-karpathy-skills | `References/Agent/Skills/andrej-karpathy-skills` | skills/workflow reference |
| antfarm | `References/Agent/Workflow/antfarm` | multi-agent reference pending detailed classification |
| anthropics-skills | `References/Agent/Skills/anthropics-skills` | Anthropic-style skills reference |
| anysearch-mcp-server | `References/Agent/Memory/anysearch-mcp-server` | MCP/search server reference |
| anysearch-skill | `References/Agent/Memory/anysearch-skill` | search skill reference |
| awesome-claude-agents | `References/Agent/Skills/awesome-claude-agents` | Claude agent collection reference |
| awesome-codex-skills | `References/Agent/Skills/awesome-codex-skills` | Codex skills collection reference |
| awesome-codex-subagents | `References/Agent/Skills/awesome-codex-subagents` | Codex subagent collection reference |
| awesome-openclaw-skills | `References/Agent/Skills/awesome-openclaw-skills` | OpenClaw skills collection reference |
| claude-plugins-official | `References/Agent/Skills/claude-plugins-official` | Claude plugin/reference implementation source |
| codex-plugin-cc | `References/Agent/Skills/codex-plugin-cc` | Codex plugin reference |
| context-engineering-kit | `References/Agent/Skills/context-engineering-kit` | context-engineering reference |
| csghub | `References/Agent/Memory/csghub` | crawled agent/project reference pending detailed classification |
| deepwiki-rs | `References/Agent/Memory/deepwiki-rs` | repository knowledge/search reference |
| gelab-zero | `References/Agent/UI/gelab-zero` | crawled agent/project reference pending detailed classification |
| goclaw-dev | `References/Agent/Platforms/goclaw-dev` | Claw ecosystem reference |
| GraphRAG | `References/Agent/Memory/GraphRAG` | graph-based retrieval and memory/reference indexing |
| graphify-8 | `References/Agent/Memory/graphify-8` | graph/indexing reference pending detailed classification |
| harness | `References/Agent/Workflow/harness` | harness/evaluation reference |
| HeavySkill | `References/Agent/Skills/HeavySkill` | skill-heavy agent workflow reference |
| intentkit | `References/Agent/Domain/intentkit` | intent/workflow agent reference |
| lobehub-canary | `References/Agent/UI/lobehub-canary` | agent UI/product reference |
| mastra | `References/Agent/Frameworks/mastra` | agent framework reference |
| mattpocock-skills | `References/Agent/Skills/mattpocock-skills` | skills/workflow reference |
| MMSkills | `References/Agent/Skills/MMSkills` | multimodal skill and task-skill mapping reference |
| mlflow | `References/Agent/Workflow/mlflow` | AI/ML lifecycle and agent evaluation reference |
| moltis | `References/Agent/Platforms/moltis` | crawled agent/project reference pending detailed classification |
| oh-my-agent | `References/Agent/Control/oh-my-agent` | agent workflow collection reference |
| oh-my-claudecode | `References/Agent/Control/oh-my-claudecode` | Claude Code workflow reference |
| oh-my-codex | `References/Agent/Control/oh-my-codex` | Codex workflow reference |
| openai-agents-python | `References/Agent/Frameworks/openai-agents-python` | OpenAI Agents SDK reference |
| openai-cookbook | `References/Agent/SDK/openai-cookbook` | OpenAI examples/reference |
| openai-python | `References/Agent/SDK/openai-python` | OpenAI Python SDK reference |
| openai-skills | `References/Agent/Skills/openai-skills` | OpenAI skills reference |
| openpencil | `References/Agent/Memory/openpencil` | agent/product reference pending detailed classification |
| pentestagent | `References/Agent/Security/pentestagent` | security agent reference |
| plannotator | `References/Agent/UI/plannotator` | planning/annotation agent reference |
| pro-workflow | `References/Agent/Skills/pro-workflow` | professional workflow reference |
| promptfoo | `References/Agent/Security/promptfoo` | prompt/eval harness reference |
| redamon | `References/Agent/Security/redamon` | crawled agent/project reference pending detailed classification |
| relaticle | `References/Agent/UI/relaticle` | crawled agent/project reference pending detailed classification |
| rogue | `References/Agent/Security/rogue` | crawled agent/project reference pending detailed classification |
| sdk-python | `References/Agent/Workflow/sdk-python` | SDK/client reference |
| SkillRouter | `References/Agent/Skills/SkillRouter` | skill routing and evaluation reference |
| SkillX | `References/Agent/Skills/SkillX` | agent skill execution/evaluation reference |
| spacebot | `References/Agent/Platforms/spacebot` | crawled agent/project reference pending detailed classification |
| SR-Agents | `References/Agent/Skills/SR-Agents` | search/research agent reference |
| SSL | `References/Agent/Skills/SSL` | skill/self-supervised learning reference |
| squad-dev | `References/Agent/Control/squad-dev` | agent team/dev workflow reference |
| superpowers | `References/Agent/Skills/superpowers` | skills/workflow reference |
| swarm | `References/Agent/Frameworks/swarm` | multi-agent swarm reference |
| symphony | `References/Agent/Control/symphony` | multi-agent/workflow reference pending detailed classification |
| terminal-velocity | `References/Agent/Domain/terminal-velocity` | terminal/coding-agent reference pending detailed classification |
| tiktoken | `References/Agent/SDK/tiktoken` | tokenization/context-budget reference |
| tinyagi | `References/Agent/Platforms/tinyagi` | small agent framework reference |
| tracecat | `References/Agent/Security/tracecat` | workflow/automation reference |
| vexa | `References/Agent/Memory/vexa` | crawled agent/project reference pending detailed classification |
| whisper | `References/Agent/SDK/whisper` | audio/model reference pending detailed classification |
| zylos-core | `References/Agent/Platforms/zylos-core` | crawled agent/project reference pending detailed classification |
| docs-mcp-server | `References/Agent/Memory/docs-mcp-server` | local documentation indexing and MCP server reference |
| context7 | `References/Agent/Memory/context7` | up-to-date documentation retrieval MCP/skill reference |
| bifrost | `References/Agent/Platforms/bifrost` | AI gateway, provider routing, failover, monitoring, and MCP gateway reference |

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
