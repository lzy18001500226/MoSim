# Future Write Gate For QuadrotorControllerBlocks Package Shell

Task 006 is read-only. A future write task must be separately approved before creating `Models/QuadrotorControllerBlocks/package.mo` or `package.order`.

## Proposed Write Scope

Allowed only in a future task:

- `Models/QuadrotorControllerBlocks/package.mo`
- `Models/QuadrotorControllerBlocks/package.order`
- evidence directory for that future task
- return/blocker packet

Do not edit controller `.mo` files in the first package-shell write gate unless PMO separately approves packaging-header migration.

## Static Gates Before MCP

1. `package.order` contains only approved category entries, no duplicates, trailing newline.
2. `package.mo` category aliases cover all 19 active main `.mo` files.
3. Every alias extends a current flat class target.
4. Existing flat class files remain present and unchanged.
5. Backup/upgrade directories remain untouched.
6. All scenario configs and experiment models that currently use flat controller names remain compatible.
7. `git diff --check` passes on the future write scope.

## MCP/GUI Gates In A Separate Validation Task

If PMO needs live MWORKS evidence after the static package shell:

1. Reuse the existing logged-in MWORKS/Sysplorer window; do not close or restart it.
2. Run a GUI sentinel before and after any MCP action.
3. Use Sysplorer MCP only after a minimal session health probe.
4. Load official baseline and controller files in the known dependency order when required.
5. `check_model` representative classes before any simulation.
6. Do not run Smart Layout or diagram writeback unless a separate graphical-layout task approves it.

## Rollback Boundary

- If the package shell changes load semantics or makes flat controller classes unavailable, revert only the future `package.mo/package.order` package-shell files.
- Do not touch active controller `.mo` files or backup directories while rolling back the package-shell experiment.

## Claim Boundary

A package-shell write gate would still be package organization evidence only. It would not prove controller performance, graphical acceptance, planner readiness, live runtime ack, or closed-loop success.
