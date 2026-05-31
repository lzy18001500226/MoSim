# Knowledge and Search Round 7

## source_slice

- Local knowledge/search references under `References/Agent`: Haystack and
  LangChain.
- Focused read on modular components, pipelines, retrievers, document stores,
  tools, memory, evaluation, observability, vendor-neutral abstractions, and
  production RAG control.
- Current CoAgent target surfaces: knowledge index, memory context, context
  packs, source-family audits, and future structured memory.

## read_files_or_urls

- `References/Agent/haystack/README.md`
- `References/Agent/haystack/docs-website/docs/intro.mdx`
- `References/Agent/langchain/README.md`
- `References/Agent/langchain/libs/core/README.md`

## architecture_claims

1. Knowledge systems should be modular pipelines, not hidden prompt stuffing.
   Haystack's explicit retrieval/ranking/filtering/routing and LangChain's
   interoperable abstractions support CoAgent's separate knowledge index,
   memory context, and context-pack layers.
2. Retrieval has to preserve provenance. CoAgent search results should keep
   source path, category, excerpt, matched terms, and whether the match is
   exact enough to justify loading a file.
3. Vendor-neutral abstractions are useful, but only after local project
   semantics are clear. CoAgent currently needs a small deterministic local
   index more than a large vector/RAG dependency.
4. Memory and knowledge are different. Memory can summarize prior task evidence;
   knowledge should route to source files and audits. Both must be fenced when
   inserted into a task context.
5. Production RAG claims require evaluation and observability. CoAgent should
   not claim "memory solved" until retrieval quality, freshness, and failure
   modes are measured on real long-running tasks.

## adopt_now

- Keep `CoAgent/knowledge/knowledge_indexer.py` as a deterministic local
  keyword/source-category index for project recovery.
- Keep `CoAgent/memory/memory_context.py` fenced and budgeted; recalled memory
  remains background evidence, not user instruction.
- Keep source-family audits as high-level retrieval targets so workers can
  inspect a bounded decision artifact before raw external trees.
- Keep provenance fields in knowledge search output: path, category, excerpt,
  matched terms, and exact-match marker.
- Keep knowledge build/search as required validation for CoAgent changes.

## adapt_later

- Add structured facts/decisions/evidence records on top of the current keyword
  index.
- Add freshness metadata and stale-source warnings for fast-moving external
  projects and official articles.
- Add embedding or hybrid retrieval only after keyword/category search fails on
  real recovery tasks.
- Add retrieval-quality tests: expected source hit, forbidden source hit,
  stale-source handling, and context-pack budget impact.

## portable_only

- Full Haystack/LangChain RAG stacks are useful if CoAgent becomes a larger
  product or needs complex document ingestion, but they are unnecessary for the
  current project-local recovery layer.
- Exposing CoAgent knowledge as an MCP or HTTP service may be useful for future
  reuse, but local scripts are enough for MoSim now.

## reject

- Do not import Haystack/LangChain as CoAgent core dependencies until a measured
  retrieval gap justifies them.
- Do not treat retrieved snippets as authoritative without source path and
  audit/review context.
- Do not put broad external reference trees directly into every context pack.
- Do not let memory recall override current task packets, user instructions, or
  locked project rules.

## unknowns

- The minimum structured-memory schema is still open.
- The point where keyword search becomes insufficient is unknown until more
  real department tasks rely on recovery from knowledge.
- Whether CoAgent needs vector search depends on future query failures, not on
  external framework availability.

## required_patch

- Add this knowledge/search audit record to close the `knowledge_search`
  source-family coverage gap.
- Keep current deterministic knowledge/memory layers as adopted architecture
  and document vector/RAG dependencies as later-phase only.
- No external RAG framework import is justified by this source slice.

## verification

```bash
python3 CoAgent/learning/learning_indexer.py coverage --strict
python3 CoAgent/learning/learning_indexer.py validate --strict
python3 CoAgent/knowledge/knowledge_indexer.py build
python3 CoAgent/knowledge/knowledge_indexer.py search --query knowledge_search --limit 10
python3 CoAgent/doctor/coagent_doctor.py
python3 CoAgent/hooks/preflight.py
```

## next_trigger

- Revisit this audit when adding structured memory facts, freshness metadata,
  hybrid retrieval, or knowledge-as-MCP service.
- Revisit this audit if a real worker fails to recover required context from
  the current local keyword/source-category index.
