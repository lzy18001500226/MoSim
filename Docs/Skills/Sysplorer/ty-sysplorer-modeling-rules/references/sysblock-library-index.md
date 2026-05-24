# SysblockModelLibrary — retrieval strategy (not a full index)

The Sysblock block reference corpus under `resources/SysblockModelLibrary/` is large. **Do not** paste the whole tree into prompts.

## Preferred order

1. **`get_lib_model_document(full_class_name)`** — authoritative class docs from Sysplorer for loaded libraries (`SysplorerEmbeddedCoder.*`, …).
2. **`resources_retrieval`** — `action="corpora"` with `corpus_id="sysblock_model_library"` (or manifest-equivalent id) to obtain resolved paths and `resources_retrieval_index_path`, then `action="search"` with explicit `sources` / `index_path` for block semantics, parameters, and examples.
3. **Path-locked execution** — after the task is confirmed as Sysblock, follow **`modeling_path_router.md` §3** and **`sysblock_style_guide.md`** in this skill’s `references/` for run-script loops, API usage, and verification.

## Notes

- `sysblock_model_library` is typically **not** in default merged search; pass **`sources`** explicitly when searching module docs.
- Block **parameter API keys** may be cross-checked against `resources/SysplorerAPI/SysblockParameters.md` when shipped (not RAG); still prefer `get_lib_model_document` for installed classes.
