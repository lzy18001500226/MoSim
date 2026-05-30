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
| Project | Path | Primary Use |
|---|---|---|
| AFFiNE-canary | `References/Agent/AFFiNE-canary` | agent/product architecture reference |
| CowAgent | `References/Agent/CowAgent` | agent orchestration reference |
| MetaGPT | `References/Agent/MetaGPT` | role-based software-company agent reference |
| OpenHands | `References/Agent/OpenHands` | coding-agent runtime reference |
| OpenSpec | `References/Agent/OpenSpec` | spec-driven workflow reference |
| TaskWeaver | `References/Agent/TaskWeaver` | planner/executor workflow reference |
| ag2 | `References/Agent/ag2` | multi-agent framework reference |
| anthropic-sdk-python | `References/Agent/anthropic-sdk-python` | SDK/client and agent integration reference |
| autogen | `References/Agent/autogen` | multi-agent framework reference |
| camel | `References/Agent/camel` | agent society/workflow reference |
| claw-code | `References/Agent/claw-code` | coding-agent reference |
| codex | `References/Agent/codex` | Codex source, app-server, thread-store, rollout, skills, execpolicy reference |
| coding-interview-university | `References/Agent/coding-interview-university` | general CS reference, low priority |
| crewAI | `References/Agent/crewAI` | crew/task orchestration reference |
| haystack | `References/Agent/haystack` | agent/search pipeline reference |
| hermes-agent | `References/Agent/hermes-agent` | durable agent runtime, gateway, memory, skills, scheduler reference |
| hermes-desktop | `References/Agent/hermes-desktop` | Hermes desktop/client surface reference |
| langchain | `References/Agent/langchain` | chain/tool abstraction reference |
| langgraph | `References/Agent/langgraph` | graph-based agent orchestration reference |
| llama-agents | `References/Agent/llama-agents` | distributed agent architecture reference |
| okwinds | `References/Agent/okwinds` | workflow/runtime/WAL ideas reference |
| openclaw | `References/Agent/openclaw` | predecessor-style coding-agent/runtime reference |
| sdk-typescript | `References/Agent/sdk-typescript` | TS SDK/interface reference |
| temporal | `References/Agent/temporal` | durable workflow runtime reference |
| AChat-canary | `References/Agent/AChat-canary` | crawled agent/project reference pending detailed classification |
| AI-Infra-Guard | `References/Agent/AI-Infra-Guard` | crawled agent/project reference pending detailed classification |
| Agent-Skills-for-Context-Engineering | `References/Agent/Agent-Skills-for-Context-Engineering` | context engineering and skill reference |
| AutoSkill | `References/Agent/AutoSkill` | automatic skill discovery/evolution reference |
| Awesome-Agent-Skills | `References/Agent/Awesome-Agent-Skills` | agent skill collection reference |
| AgentsMesh | `References/Agent/AgentsMesh` | crawled multi-agent/runtime reference pending detailed classification |
| AiSOC | `References/Agent/AiSOC` | security/agent operations reference pending detailed classification |
| AionUi | `References/Agent/AionUi` | agent UI/product reference pending detailed classification |
| AutoGroq | `References/Agent/AutoGroq` | agent workflow reference pending detailed classification |
| CLIP | `References/Agent/CLIP` | model/tooling reference pending detailed classification |
| ClawTeam | `References/Agent/ClawTeam` | Claw/OpenClaw ecosystem reference |
| ClawTeam-OpenClaw | `References/Agent/ClawTeam-OpenClaw` | OpenClaw ecosystem reference |
| CodexDesktop-Rebuild | `References/Agent/CodexDesktop-Rebuild` | Codex desktop/UI reference pending detailed classification |
| CodexMonitor | `References/Agent/CodexMonitor` | Codex monitoring/reference tooling pending detailed classification |
| Decepticon | `References/Agent/Decepticon` | crawled agent/project reference pending detailed classification |
| ECC | `References/Agent/ECC` | crawled agent/project reference pending detailed classification |
| LitterBox | `References/Agent/LitterBox` | crawled agent/project reference pending detailed classification |
| Mysti | `References/Agent/Mysti` | crawled agent/project reference pending detailed classification |
| NeMo-Agent-Toolkit-develop | `References/Agent/NeMo-Agent-Toolkit-develop` | NVIDIA agent toolkit reference |
| OpenMOSS | `References/Agent/OpenMOSS` | multi-agent/open-source agent reference pending detailed classification |
| Pearl | `References/Agent/Pearl` | crawled agent/project reference pending detailed classification |
| RepoAgent | `References/Agent/RepoAgent` | repository agent/documentation reference |
| SuperClaude_Framework | `References/Agent/SuperClaude_Framework` | Claude workflow/command framework reference |
| SurfSense | `References/Agent/SurfSense` | research/search agent reference pending detailed classification |
| Viper | `References/Agent/Viper` | crawled agent/project reference pending detailed classification |
| YC-Killer | `References/Agent/YC-Killer` | crawled agent/product reference pending detailed classification |
| agent-skills | `References/Agent/agent-skills` | agent skills reference |
| agent-teams-ai | `References/Agent/agent-teams-ai` | agent team architecture reference |
| agentic_security | `References/Agent/agentic_security` | agent security reference |
| agor | `References/Agent/agor` | crawled agent/project reference pending detailed classification |
| ai-data-science-team | `References/Agent/ai-data-science-team` | data-science agent team reference |
| andrej-karpathy-skills | `References/Agent/andrej-karpathy-skills` | skills/workflow reference |
| antfarm | `References/Agent/antfarm` | multi-agent reference pending detailed classification |
| anthropics-skills | `References/Agent/anthropics-skills` | Anthropic-style skills reference |
| anysearch-mcp-server | `References/Agent/anysearch-mcp-server` | MCP/search server reference |
| anysearch-skill | `References/Agent/anysearch-skill` | search skill reference |
| awesome-claude-agents | `References/Agent/awesome-claude-agents` | Claude agent collection reference |
| awesome-codex-skills | `References/Agent/awesome-codex-skills` | Codex skills collection reference |
| awesome-codex-subagents | `References/Agent/awesome-codex-subagents` | Codex subagent collection reference |
| awesome-openclaw-skills | `References/Agent/awesome-openclaw-skills` | OpenClaw skills collection reference |
| claude-plugins-official | `References/Agent/claude-plugins-official` | Claude plugin/reference implementation source |
| codex-plugin-cc | `References/Agent/codex-plugin-cc` | Codex plugin reference |
| context-engineering-kit | `References/Agent/context-engineering-kit` | context-engineering reference |
| csghub | `References/Agent/csghub` | crawled agent/project reference pending detailed classification |
| deepwiki-rs | `References/Agent/deepwiki-rs` | repository knowledge/search reference |
| gelab-zero | `References/Agent/gelab-zero` | crawled agent/project reference pending detailed classification |
| goclaw-dev | `References/Agent/goclaw-dev` | Claw ecosystem reference |
| GraphRAG | `References/Agent/GraphRAG` | graph-based retrieval and memory/reference indexing |
| graphify-8 | `References/Agent/graphify-8` | graph/indexing reference pending detailed classification |
| harness | `References/Agent/harness` | harness/evaluation reference |
| HeavySkill | `References/Agent/HeavySkill` | skill-heavy agent workflow reference |
| intentkit | `References/Agent/intentkit` | intent/workflow agent reference |
| lobehub-canary | `References/Agent/lobehub-canary` | agent UI/product reference |
| mastra | `References/Agent/mastra` | agent framework reference |
| mattpocock-skills | `References/Agent/mattpocock-skills` | skills/workflow reference |
| MMSkills | `References/Agent/MMSkills` | multimodal skill and task-skill mapping reference |
| mlflow | `References/Agent/mlflow` | AI/ML lifecycle and agent evaluation reference |
| moltis | `References/Agent/moltis` | crawled agent/project reference pending detailed classification |
| oh-my-agent | `References/Agent/oh-my-agent` | agent workflow collection reference |
| oh-my-claudecode | `References/Agent/oh-my-claudecode` | Claude Code workflow reference |
| oh-my-codex | `References/Agent/oh-my-codex` | Codex workflow reference |
| openai-agents-python | `References/Agent/openai-agents-python` | OpenAI Agents SDK reference |
| openai-cookbook | `References/Agent/openai-cookbook` | OpenAI examples/reference |
| openai-python | `References/Agent/openai-python` | OpenAI Python SDK reference |
| openai-skills | `References/Agent/openai-skills` | OpenAI skills reference |
| openpencil | `References/Agent/openpencil` | agent/product reference pending detailed classification |
| pentestagent | `References/Agent/pentestagent` | security agent reference |
| plannotator | `References/Agent/plannotator` | planning/annotation agent reference |
| pro-workflow | `References/Agent/pro-workflow` | professional workflow reference |
| promptfoo | `References/Agent/promptfoo` | prompt/eval harness reference |
| redamon | `References/Agent/redamon` | crawled agent/project reference pending detailed classification |
| relaticle | `References/Agent/relaticle` | crawled agent/project reference pending detailed classification |
| rogue | `References/Agent/rogue` | crawled agent/project reference pending detailed classification |
| sdk-python | `References/Agent/sdk-python` | SDK/client reference |
| SkillRouter | `References/Agent/SkillRouter` | skill routing and evaluation reference |
| SkillX | `References/Agent/SkillX` | agent skill execution/evaluation reference |
| spacebot | `References/Agent/spacebot` | crawled agent/project reference pending detailed classification |
| SR-Agents | `References/Agent/SR-Agents` | search/research agent reference |
| SSL | `References/Agent/SSL` | skill/self-supervised learning reference |
| squad-dev | `References/Agent/squad-dev` | agent team/dev workflow reference |
| superpowers | `References/Agent/superpowers` | skills/workflow reference |
| swarm | `References/Agent/swarm` | multi-agent swarm reference |
| symphony | `References/Agent/symphony` | multi-agent/workflow reference pending detailed classification |
| terminal-velocity | `References/Agent/terminal-velocity` | terminal/coding-agent reference pending detailed classification |
| tiktoken | `References/Agent/tiktoken` | tokenization/context-budget reference |
| tinyagi | `References/Agent/tinyagi` | small agent framework reference |
| tracecat | `References/Agent/tracecat` | workflow/automation reference |
| vexa | `References/Agent/vexa` | crawled agent/project reference pending detailed classification |
| whisper | `References/Agent/whisper` | audio/model reference pending detailed classification |
| zylos-core | `References/Agent/zylos-core` | crawled agent/project reference pending detailed classification |

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
2. `References/Agent/codex`
3. `References/Agent/hermes-agent`
4. `References/Agent/hermes-desktop`
5. `References/Agent/anthropic-sdk-python/src/anthropic/resources/beta`
6. `References/Agent/openclaw`
7. `References/Agent/okwinds`
8. `Docs/Index/agent_project_classification.md`

If the task is about long-context degradation, context packs, or durable agent
memory:

1. `CoAgent/docs/research/LEARNING_STRATEGY.md`
2. `References/Agent/anthropic-sdk-python/src/anthropic/resources/beta/memory_stores`
3. `References/Agent/anthropic-sdk-python/src/anthropic/resources/beta/sessions`
4. `References/Agent/codex`
5. `References/Agent/hermes-agent`
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
