# Profile Output Templates

These templates document the static artifacts emitted by
`Scripts/quality/check_experiment_profile.py`.

They are not filled runtime evidence. A real run must replace placeholders,
record source hashes, attach logs and metrics, and then validate the resulting
bundle with the relevant run-level checker.

| Template | Purpose |
| --- | --- |
| `launch_plan.skeleton.template.json` | Orchestrator launch intent after Profile validation. |
| `RUN_MANIFEST.skeleton.template.json` | Minimum run evidence manifest shape before runtime fields are filled. |
| `profile_rejection.template.json` | Structured rejection packet for incompatible Profile combinations. |
