# COAGENT-MINILOOP-03 Retrospective

Status: superseded_not_visible

The attempt below is preserved as historical diagnostic evidence only. It must
not be used as proof of current visible department communication because the
user confirmed the department conversations had already been deleted from the
UI.

## Keep

- Use `codex exec resume` only after validating both conditions:
  the target conversation is currently visible to the user, and the registry
  status is `active_visible`.
- Keep scoped packets narrow and make the result path explicit.
- Import worker output through `result_router` before calling a task done.

## Change

- Do not assume registry ids or local rollout files are current. A local rollout
  file is not sufficient; the user-visible conversation must still exist.
- Reject dispatch before transport when the department status is not
  `active_visible`.
- Do not run transport validation in parallel while the adapter shares one
  shadow Codex home.
- For custom packets, require `result_file:` or pass `--result-file`.

## Follow-Up

- Create or confirm a current visible department conversation before registering
  it as dispatchable.
- Run a Codex App UI visibility/stability proof separately.
- Decide whether each long Git task should reuse a persistent DevOps
  conversation or create a scoped task conversation under DevOps ownership.
