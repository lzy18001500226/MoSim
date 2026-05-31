"""Project-default `ts_project` wrapper.

aspect_rules_ts 3.x requires each `ts_project` call to pick a transpiler
explicitly — there is no global default. Every place in this repo that
compiles TS should use this wrapper so we have a single choice of
transpiler (`tsc`) and avoid sprinkling the same boilerplate.

Swapping to swc later is a one-line change here, not 20 edits.
"""

load("@aspect_rules_ts//ts:defs.bzl", _ts_project = "ts_project")

def ts_project(**kwargs):
    """ts_project with `transpiler = "tsc"` pinned repo-wide.

    Note on type-check semantics: this wrapper runs tsc exactly as
    `pnpm build` would — full emit + strict checks. If a target has
    intentionally loose type surfaces (e.g. wasm-bindgen-derived
    interfaces), pass `declaration = False` + `no_emit = True` at the
    call site to skip declaration emit while still checking types.
    """
    kwargs.setdefault("transpiler", "tsc")
    _ts_project(**kwargs)
