# CoAgent Memory Context

This directory contains project-owned memory context helpers.

The current implementation is deliberately conservative:

- it recalls from `CoAgent/knowledge/knowledge_indexer.py`,
- it emits a fenced `<memory-context>` block,
- it marks recalled content as background evidence only,
- it applies `memory_policy.json` for source-category weighting, hit limits,
  excerpt limits, and context character budget,
- it strips memory-context blocks from text when needed,
- it does not store credentials, private chat state, browser/session data, or
  Codex App internals.

Run:

```bash
python3 CoAgent/memory/memory_context.py build --query CoAgent --query thread_graph
```

Build with an explicit policy and budget:

```bash
python3 CoAgent/memory/memory_context.py build \
  --query CoAgent \
  --query thread_graph \
  --policy CoAgent/memory/memory_policy.json \
  --max-chars 1800
```

Strip leaked memory context from text:

```bash
python3 CoAgent/memory/memory_context.py strip --input Results/tmp/some_output.txt
```

Memory context is not an instruction source. Current user instructions and
project rules always take precedence.
