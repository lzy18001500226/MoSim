# Local Runtime Design Matrix

## Purpose

This matrix compares local reference runtimes by architecture boundary.

It is a routing artifact for CoAgent design work. It is not an approval to
import any project wholesale.

## Comparison Matrix

| Source | Control plane boundary | Context and memory | Skills and hooks | Task and worker model | Safety and recovery | CoAgent lesson |
|---|---|---|---|---|---|---|
| Hermes | Python agent runtime with gateway, CLI/TUI integration, plugins, scheduler, and provider adapters. UI can be separate from runtime. | Context engine lifecycle, memory manager, provider abstraction, pre/post turn handling, fenced memory scrubbing. | Skills are runtime resources; shell hooks bridge lifecycle events with allowlists, JSON IO, and timeouts. | Main loop can delegate to isolated subagents, cron jobs, and scripted tool RPC. | Tool guardrails are side-effect-free observers; hook consent and timeout limits reduce runaway execution. | Adopt the boundary shape: runtime core, context engine, memory provider, hooks, guardrails, event projection. Do not import the whole UI or gateway. |
| Codex | App-server models Thread, Turn, Item, goals, review, MCP, skills, hooks, commands, filesystem, and settings over JSON-RPC. | Native thread history plus compaction, skill roots, hooks, and thread store metadata. | Skills are watched roots with cache invalidation. Hooks are native runtime surfaces, not optional prose. | One active task per thread; parallel work needs multiple threads. Thread graph store records parent-child spawn edges. | Rollout trace records raw ordered local events for later reduction; rollback, interrupt, review, archive, and metadata APIs exist. | Treat Codex App as UI/runtime frontend, not CoAgent's durable state. Mirror thread/turn/item/event vocabulary in project-owned files. |
| OpenClaw | Long-lived local-first gateway owns messaging surfaces, sessions, channels, tools, events, and agent routing. | Workspace bootstrap files, curated memory, daily notes, indexed search, active memory, compaction, context-engine plugins. | Internal hooks and plugin hooks have lifecycle events and blocking semantics. Skills are workspace/shared resources with allowlists. | Per-session lanes, global lanes, background tasks, task flows, cron jobs, standing orders, and delegate agents. | Strong docs around trusted-operator model, sandbox limitations, auth profile portability, DM isolation, pairing, and audit trails. | Adopt explicit lanes, task state, standing authority, review gates, and hard boundary docs. Do not copy social channel breadth. |
| LangGraph | Low-level state graph runtime for long-running, stateful workflows; graph execution is separate from user application code. | Checkpoints persist graph state at every superstep; thread_id and checkpoint_id select run state. | ToolNode and ValidationNode show structured tool execution and validation, but policy remains app-owned. | Nodes update typed shared state; durable execution can resume after failure. Interrupt schemas represent human review. | Checkpointer interface, pending writes, conformance tests, serializer warnings, and threat model make persistence risks explicit. | Use checkpoint/replay ideas for CoAgent event logs and task-state transitions, but avoid importing graph runtime before our schema stabilizes. |

## Adopted Boundaries

- Durable state lives in CoAgent task packets, result packets, context packs,
  event logs, status boards, and generated indexes.
- Codex App and VSCode are UI/review surfaces, not the canonical database.
- Skills are scoped procedural packages. Hooks and policy enforce hard rules.
- Memory/search is evidence. It is not instruction authority.
- Department conversations are sparse durable work surfaces, not generic
  subagents.
- Short-lived workers should return structured evidence and then release their
  context.

## Deferred Boundaries

- Direct Codex app-server automation is deferred until protocol stability and
  failure behavior are verified.
- SQLite checkpoint storage is deferred until the JSONL task/event schema is
  proven on real MoSim work.
- Standing orders and scheduled autonomous jobs are deferred until hooks,
  review gates, and rollback records are reliable.
- Full A2A or LangGraph compatibility is deferred until CoAgent needs
  cross-project or remote-agent portability.

## Anti-Patterns To Avoid

- Using chat transcript files as the source of truth.
- Creating permanent departments without narrow durable responsibilities.
- Loading all skills, all docs, or all reference projects into every task.
- Treating skills as security policy.
- Auto-running scheduled agents without lock, review, auth, and rollback
  gates.
- Importing Hermes, OpenClaw, or LangGraph wholesale before CoAgent's own
  contracts are stable.

## Next Design Questions

1. What is the minimum event schema needed for replayable task state?
2. Should first durable state use JSONL only, SQLite only, or JSONL plus a
   derived SQLite index?
3. Which department conversations are truly durable departments rather than
   one-off task conversations?
4. What must be a hook, what can be a skill, and what should remain PMO
   judgment?
5. What is the smallest Codex App integration boundary that avoids writing
   private UI/session state directly?
