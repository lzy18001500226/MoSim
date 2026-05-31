# 🧭 Task-Skill Mapping

`task_skill_mapping.json` is a compact global mapping from OSWorld domain and
task ID to the released skill subset.

Use it with the MMSkills-aware OSWorld runner:

```bash
python run.py \
  --agent_type mm_skill \
  --skills_library_dir skills_library \
  --task_skill_mapping_root task_skill_mappings/task_skill_mapping.json \
  --skill_mode multimodal
```

The resolver also supports per-domain generated mapping files, but this release
uses one global file to keep the anonymous repository small and easy to inspect.
