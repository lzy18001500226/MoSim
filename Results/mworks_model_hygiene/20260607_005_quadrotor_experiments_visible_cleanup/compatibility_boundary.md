# Compatibility Boundary

This 005 cleanup is a non-destructive display/package organization change for `Models/QuadrotorExperiments`.

- `package.order` now lists only the 11 category package entries requested by PMO.
- Historical flat classes are not deleted, moved, renamed, or migrated in this task.
- Flat class compatibility paths remain defined by sibling `.mo` files or embedded definitions in `package.mo`.
- The four added `TraceIsolation` entries are category aliases that extend existing flat legacy smoke models.
- This is not MWORKS GUI acceptance, `check_model`, simulation evidence, Factory trace consumption, controller performance, planner readiness, live runtime ack, plant tracking, or closed-loop evidence.

Next validation should be a separately scoped static diff review and, only if PMO assigns it, a GUI/manual package-browser review that reuses the existing MWORKS/Sysplorer window without closing or restarting it.
