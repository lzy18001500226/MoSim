# Multi-Agent Learning URL Index

Last updated: 2026-05-27

## Purpose

This file is the durable URL seed list for CoAgent self-learning.

It is not an architecture decision record. Each agent that studies one of these
sources should write a bounded audit under `CoAgent/learning/audits/` using the
contract in `CoAgent/docs/research/LEARNING_STRATEGY.md`.

## Reading Rules

- Prefer official docs, official engineering posts, and first-party source
  repositories.
- Do not import a framework pattern directly into CoAgent until it has been
  compared against MoSim's requirements.
- Separate these concepts explicitly:
  - skills: selectively loaded procedural capability packages,
  - hooks: hard lifecycle constraints or guardrails,
  - tools and MCP: callable external capabilities,
  - subagents: bounded workers with isolated context,
  - agent teams: durable, stateful collaboration surfaces.
- Treat context as a limited resource. A good source should explain how it
  limits, routes, summarizes, stores, or discards context.

## Priority 0: Core Multi-Agent Architecture

| Source | URL | Why to study |
|---|---|---|
| Anthropic: multi-agent research system | https://www.anthropic.com/engineering/built-multi-agent-research-system | Production lessons for orchestrator-worker systems, parallel subagents, cost, reliability, and evaluation. |
| Anthropic: effective context engineering | https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents | Context curation, context packs, compaction, retrieval, and long-context degradation. |
| Anthropic: effective harnesses for long-running agents | https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents | Long-horizon harness design, interruption recovery, evidence, and progress across context windows. |
| Anthropic: managed agents | https://www.anthropic.com/engineering/managed-agents | Separation of brain, session, harness, sandbox, and execution environment. |
| Anthropic: building effective agents | https://www.anthropic.com/engineering/building-effective-agents | Agent versus workflow distinction and practical workflow/agent patterns. |
| Anthropic: writing tools for agents | https://www.anthropic.com/engineering/writing-tools-for-agents | Tool design, tool descriptions, tool ergonomics, and tool evaluation. |
| OpenAI Agents SDK: multi-agent orchestration | https://openai.github.io/openai-agents-python/multi_agent/ | Handoffs, agents-as-tools, manager pattern, decentralized pattern. |
| OpenAI Agents SDK: handoffs | https://openai.github.io/openai-agents-python/handoffs/ | Explicit task transfer and routing contracts between agents. |
| OpenAI Agents SDK: lifecycle hooks | https://openai.github.io/openai-agents-python/ref/lifecycle/ | Runtime lifecycle hooks and instrumentation boundaries. |
| Google ADK: multi-agent systems | https://adk.dev/agents/multi-agents/ | Hierarchical, sequential, parallel, loop, and custom multi-agent composition. The old `google.github.io/adk-docs` URL redirects here. |
| Agent2Agent Protocol specification | https://a2a-protocol.org/latest/specification/ | Inter-agent protocol concepts: agent cards, tasks, messages, artifacts, streaming, auth. |
| Agent2Agent Protocol repository | https://github.com/a2aproject/A2A/blob/main/docs/specification.md | Stable source copy of the A2A specification and version history. |

## Priority 1: Coding-Agent Runtime, Skills, Hooks, and Workflows

| Source | URL | Why to study |
|---|---|---|
| Anthropic Claude Code subagents | https://docs.anthropic.com/en/docs/claude-code/sub-agents | Subagent context isolation, tool scoping, and task delegation. |
| Anthropic Claude Code hooks | https://docs.anthropic.com/en/docs/claude-code/hooks | Deterministic lifecycle commands and policy enforcement. |
| Anthropic Claude Code skills | https://docs.anthropic.com/en/docs/claude-code/skills | Progressive-disclosure skill loading and skill packaging. |
| Anthropic Agent Skills article | https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills | Skill design motivation and real-world agent capability packaging. |
| Anthropic Claude Code best practices | https://www.anthropic.com/engineering/claude-code-best-practices | Coding-agent operating practices and repository interaction patterns. |
| Anthropic: beyond permission prompts | https://www.anthropic.com/engineering/beyond-permission-prompts | Safer autonomy and security boundaries for coding agents. |
| OpenAI Codex developer docs | https://developers.openai.com/codex | Codex app, workflows, coding-agent surface, and official feature entry point. |
| OpenAI Codex use cases | https://developers.openai.com/codex/explore | Repeatable workflow, skill, automation, and review patterns. |
| OpenAI Agents guide | https://platform.openai.com/docs/guides/agents | OpenAI platform-level agent concepts, tools, tracing, and deployment. |
| OpenAI tools guide | https://platform.openai.com/docs/guides/tools | Function/tool calling and hosted tool boundaries. |
| OpenAI prompt caching | https://platform.openai.com/docs/guides/prompt-caching | Context cost control and reusable prefix implications. |

Access note: some OpenAI documentation pages may return HTTP 403 to plain
`curl` while remaining accessible from a browser or official docs surfaces.

## Priority 2: Multi-Agent Frameworks and Orchestration Libraries

| Source | URL | Why to study |
|---|---|---|
| LangGraph workflow/agent concepts | https://docs.langchain.com/oss/python/langgraph/workflows-agents | Graph/state-machine framing, supervisors, handoffs, shared state, and workflow patterns. |
| LangGraph persistence | https://docs.langchain.com/oss/python/langgraph/persistence | Threads, checkpoints, human-in-the-loop, memory, time travel, fault tolerance, and pending writes. |
| LangGraph legacy multi-agent concepts | https://langchain-ai.github.io/langgraph/concepts/multi_agent/ | Legacy URL retained because many cloned references still link here; prefer the current LangChain docs above. |
| LangGraph multi-agent collaboration tutorial | https://langchain-ai.github.io/langgraph/tutorials/multi_agent/multi-agent-collaboration/ | Concrete collaboration graph examples. |
| Microsoft Semantic Kernel agent orchestration | https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/agent-orchestration/ | Sequential, concurrent, group-chat, handoff, and Magentic-style orchestration. |
| Microsoft Agent Framework overview | https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview | Enterprise agent framework concepts and orchestration surfaces. |
| AG2 documentation | https://docs.ag2.ai/ | AutoGen-derived multi-agent framework overview. |
| AG2 GroupChat | https://docs.ag2.ai/latest/docs/user-guide/advanced-concepts/groupchat/groupchat/ | Group chat manager, speaker selection, and transition constraints. |
| AG2 orchestrations | https://docs.ag2.ai/latest/docs/user-guide/advanced-concepts/orchestrations/ | Orchestration and Swarm/GroupChat evolution. |
| CrewAI docs | https://docs.crewai.com/introduction | Crew/flow split, role-based task execution, and production deployment concepts. |
| LlamaIndex multi-agent workflows | https://docs.llamaindex.ai/en/stable/understanding/agent/multi_agent/ | Multi-agent workflow patterns with retrieval and data tooling. |
| NVIDIA NeMo Agent Toolkit | https://docs.nvidia.com/nemo/agent-toolkit/latest/ | Enterprise agent toolkit, workflows, tool use, and deployment patterns. |
| AWS Strands Agents docs | https://docs.strandsagents.com/latest/ | Agent SDK design, tools, model providers, and production packaging. |
| AgentScope docs | https://doc.agentscope.io/ | Multi-agent application framework and agent simulation patterns. |

## Priority 3: Model/Vendor Agent APIs and Chinese Ecosystem

| Source | URL | Why to study |
|---|---|---|
| Kimi platform overview | https://platform.kimi.com/docs/overview | Kimi API entry point and model/tool ecosystem. |
| Kimi agent support | https://platform.kimi.com/docs/guide/agent-support.md | Kimi guidance for agent-style usage. |
| Kimi tool calls | https://platform.kimi.com/docs/guide/use-kimi-api-to-complete-tool-calls.md | Tool-calling interface and agent action loop implications. |
| Kimi + Hermes Agent | https://platform.kimi.ai/docs/guide/use-kimi-in-hermes-agent.md | How Kimi integrates with Hermes-style agents. |
| Kimi + OpenClaw | https://platform.kimi.ai/docs/guide/use-kimi-in-openclaw.md | How Kimi integrates with OpenClaw-style agents. |
| Qwen-Agent docs | https://qwenlm.github.io/Qwen-Agent/en/guide/core_moduls/agent/ | Agent abstractions in Qwen-Agent. |
| Mistral agents docs | https://docs.mistral.ai/agents/agents | Agents and conversations API concepts. |
| Mistral Studio agents introduction | https://docs.mistral.ai/studio-api/agents/introduction | Multiple agents, conversations, connector tools, and hosted agent builder concepts. |

## Priority 4: Interoperability, Memory, Evaluation, and Safety

| Source | URL | Why to study |
|---|---|---|
| Model Context Protocol documentation | https://modelcontextprotocol.io/docs | Tool/context interoperability boundary. |
| MCP specification | https://modelcontextprotocol.io/specification | Protocol-level tool and context integration. |
| OpenAI Evals | https://github.com/openai/evals | Evaluation design for agent behaviors. |
| Promptfoo docs | https://www.promptfoo.dev/docs/intro/ | Evals, red-team tests, and regression gates for prompts/agents. |
| LangSmith docs | https://docs.smith.langchain.com/ | Tracing, debugging, evaluation, and observability for agent runs. |
| Haystack docs | https://docs.haystack.deepset.ai/docs | Retrieval and pipeline design relevant to memory/context systems. |
| Temporal docs | https://docs.temporal.io/ | Durable workflow, replay, recovery, and long-running task state. |

## Local Source Mapping

These URLs should be studied together with the local source corpus:

| Local source | Related URL group |
|---|---|
| `References/Agent/hermes-agent` | Kimi + Hermes, Anthropic harness/context articles, Temporal workflow docs. |
| `References/Agent/hermes-desktop` | Codex app docs, desktop UI/runtime separation, OpenClaw references. |
| `References/Agent/codex` | OpenAI Codex docs, OpenAI Agents SDK, Anthropic managed-agents/session-harness-sandbox concepts. |
| `References/Agent/openclaw` | Kimi + OpenClaw, coding-agent safety/autonomy articles. |
| `References/Agent/langgraph` | LangGraph multi-agent docs and persistence/checkpoint patterns. |
| `References/Agent/ag2` or `autogen` | AG2 GroupChat/orchestration docs. |
| `References/Agent/crewAI` | CrewAI crew/flow docs. |
| `References/Agent/anthropic-sdk-python` | Anthropic Claude Code, SDK beta resources, and managed-agent concepts. |

## Suggested Study Rounds

1. Read Priority 0 and produce one audit focused on communication topology,
   context isolation, durable state, and recovery.
2. Read Priority 1 and produce one audit focused on skills versus hooks versus
   tools versus subagents.
3. Read Priority 2 and produce one audit focused on reusable orchestration
   patterns and patterns to reject for MoSim.
4. Read Priority 3 and produce one audit focused on portability across model
   vendors and Chinese ecosystem constraints.
5. Read Priority 4 and produce one audit focused on state, memory, evaluation,
   safety, and long-running task evidence.
