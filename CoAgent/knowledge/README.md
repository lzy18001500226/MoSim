# CoAgent Knowledge

## Purpose

This directory contains project-owned knowledge-source definitions and local
search/index helpers.

The goal is not to replace full-text search for every file in the repository.
The goal is to make the most important CoAgent, project-recovery, and compact
external-learning sources explicit, searchable, and refreshable.

## Current Components

| File | Purpose |
|---|---|
| `knowledge_sources.json` | authoritative source list for CoAgent knowledge |
| `knowledge_indexer.py` | builds and searches a local knowledge index with exact and multi-term keyword matching |

## Current Scope

Current knowledge indexing covers:

- `AGENTS.md`
- `PROGRESS.md`
- `Docs/Workflows/agent_task_ledger.md`
- `CoAgent/**`
- `CoAgent/learning/audits/**`
- `Results/coagent_learning/learning_index.json`
- `Docs/Workflows/**`
- `Docs/Index/**`
- selected entry files under `References/Agent/**`
- `Results/coagent_transport/runs/*.summary.md`
- `Results/agent_packets/summaries/*.summary.md`

Large external source trees such as `References/Agent/` are intentionally not
indexed wholesale. Agent references are indexed only through bounded entry files
such as `README.md`, `SKILL.md`, `AGENTS.md`, `CLAUDE.md`, and project index
files. Full source slices are routed through `Docs/Index/agent_project_classification.md`,
`CoAgent/docs/research/REFERENCE_PROJECT_INDEX.md`, and `CoAgent/docs/research/LEARNING_STRATEGY.md`, then
audited explicitly. This keeps daily knowledge rebuilds fast enough to be useful.

It does not yet:

- summarize documents with an LLM,
- build embeddings,
- deduplicate semantically similar content,
- search arbitrary large reference repos by default.

## Current Commands

```bash
python CoAgent/knowledge/knowledge_indexer.py list-sources
python CoAgent/knowledge/knowledge_indexer.py build
python CoAgent/knowledge/knowledge_indexer.py search --query dispatch
python CoAgent/knowledge/knowledge_indexer.py search --query "worker policy stale lock concurrency"
```
