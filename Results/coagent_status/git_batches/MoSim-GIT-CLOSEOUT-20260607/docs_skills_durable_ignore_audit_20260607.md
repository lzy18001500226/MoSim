# Docs/Skills durable ignore audit

- task: MoSim-GIT-CLOSEOUT-20260607
- visible_untracked_after: 0
- ignored_untracked_after: 26210
- class_counts: venv=26089; pycache=95; egg_info=18; build_dist=5; ue_lfs_pointer=2; ds_store=1
- cleanup: removed redundant root rules for Docs/Skills/Blender-MCP .venv and Docs/Skills/Unreal pycache
- verification: visible count remained 0 and ignored count remained 26210 after cleanup
- note: many dependency/build paths are covered by each imported project's own .gitignore plus root class guards
