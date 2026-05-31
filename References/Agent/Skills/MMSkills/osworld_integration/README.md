# 🔌 OSWorld Integration Files

This directory contains the MMSkills-aware runner files that can be copied into a local OSWorld checkout:

- `run.py`
- `lib_run_single.py`
- `lib_results_logger.py`

They add:

- the `general`, `general_text_skill`, and `mm_skill` agent paths,
- task-to-skill resolution,
- per-task skill invocation logs,
- skill usage summaries,
- result aggregation for MMSkills experiments.

Install from the repository root:

```bash
python3 scripts/install_into_osworld.py /path/to/OSWorld --with-runner --with-skills
```

Use `--with-runner` when you want to replace OSWorld runner files with the MMSkills-aware versions. Use `--with-skills` when you also want to copy the released skill subset and task mappings into the OSWorld checkout.
