# Design Cache

This directory stores migrated design drafts, superseded architecture notes,
and consolidation plans. It is not an active execution source.

Use current design documents in this order:

```text
Docs/Design/README.md
Docs/Design/需求.md
Docs/Design/架构.md
Docs/Design/架构/README.md
```

Cache layout:

| Directory | Purpose |
| --- | --- |
| `consolidation_plans/` | Migration and consolidation plans. |
| `superseded/` | Retired drafts that were replaced by current design docs. |
| `old_architecture/` | Former numbered `01-10` design set. |

Do not cite cache files as current project truth unless a current design document
explicitly routes to a section for trace-back.
