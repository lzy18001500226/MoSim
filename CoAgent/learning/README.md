# CoAgent Learning Audits

This folder is the structured audit database for external-source learning.

Human-facing design documents live under `CoAgent/docs/`. Do not add general
architecture notes directly here unless they are structured source audits.

## Contents

| Path | Purpose |
|---|---|
| `audits/` | Source-to-architecture audit records |
| `learning_indexer.py` | Builds, validates, searches, and checks coverage for audit records |

## Audit Contract

Use the contract in `CoAgent/docs/research/LEARNING_STRATEGY.md`:

```text
source_slice:
read_files_or_urls:
architecture_claims:
adopt_now:
adapt_later:
portable_only:
reject:
unknowns:
required_patch:
verification:
next_trigger:
```

## Current Design Entrypoints

For architecture and decision work, start here instead:

- `CoAgent/docs/README.md`
- `CoAgent/docs/architecture/coagent_architecture_issue_register.md`
- `CoAgent/docs/architecture/coagent_task_team_architecture.md`
- `CoAgent/docs/architecture/coagent_vendor_pattern_mapping.md`
- `CoAgent/docs/decisions/coagent_design_decision_record.md`
- `CoAgent/docs/decisions/coagent_design_review_brief.zh.md`
- `CoAgent/docs/decisions/coagent_post_approval_backlog.md`

Current design state is `approved`, but later runtime expansion is still gated
by `CoAgent/STATUS.md` and the decisions backlog.

## Structured Index

Build and validate the source-to-architecture matrix with:

```bash
python3 CoAgent/learning/learning_indexer.py build
python3 CoAgent/learning/learning_indexer.py validate --strict
python3 CoAgent/learning/learning_indexer.py search --query context_pack
python3 CoAgent/learning/learning_indexer.py coverage
```

The generated index is:

```text
Results/coagent_learning/learning_index.json
```

It is a runtime artifact and should not be committed.
