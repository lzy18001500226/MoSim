# Sysblock Docs Index

These docs are reference data, not execution rules. Do not load the whole `docs/` directory by default. The execution rules are in `SKILL.md`, `SKILL_ZH.md`, and the parent `ty-sysplorer-modeling-rules/references/sysblock_style_guide.md`.

## Files

| File | Use Only When |
|---|---|
| `SysblockParameters.md` | Need concrete block parameter names or parameter spelling. |
| `SysplorerEmbeddedCoder 2.0.md` | Need library overview or block-family names. |
| `sysblock_demo_Python.md` | Need a Python API example, after confirming it does not conflict with current parent rules. |

## Guardrails

- Sysblock topology must be created and edited through official APIs via `call_code(mode="run_script")`.
- Do not use text `.mo`, `SetModelText`, or handwritten `connect()` equations for Sysblock topology.
- Use the parent path rules; do not default to MCP server temp directories.
