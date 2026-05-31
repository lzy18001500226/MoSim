# Contributing to MMSkills

Thank you for helping improve MMSkills. This repository is intentionally compact, so contributions should keep the release easy to inspect, install, and reproduce.

## Good First Contributions

- Fix documentation gaps in the README or integration notes.
- Add verification notes to existing skills.
- Improve OSWorld installation and result-logging instructions.
- Add small, representative skills with text, state cards, and visual references.
- Report reproducibility issues with exact command lines and environment details.

## Community Skill Submissions

Use the MMSkill submission issue form for new skill packages or new domains:

```text
https://github.com/DeepExperience/MMSkills/issues/new?template=skill_submission.yml
```

See [docs/submit_mmskills.md](docs/submit_mmskills.md) for the package format, review workflow, and acceptance checklist.

## Skill Contribution Checklist

Each new skill should include:

- `SKILL.md` with applicability, procedure, transfer limits, and verification cues.
- `runtime_state_cards.json` with compact state metadata for inference.
- `state_cards.json` with audit-grade state metadata.
- `Images/` containing only the visual references needed by the state cards.
- A task mapping entry when the skill should be auto-selected for OSWorld tasks.

Keep images and metadata focused. Do not add private trajectories, secrets, API keys, or user-specific paths.

## Pull Request Guidelines

1. Open an issue first for broad changes, new domains, or behavior changes in the runtime.
2. Keep pull requests scoped to one concern.
3. Include the command you used to validate the change.
4. Update documentation when command-line flags, output files, or skill formats change.
5. Avoid committing generated result directories, local logs, virtual environments, or private benchmark data.

## Local Validation

For documentation-only changes, inspect the rendered Markdown and check links when possible.

For runtime changes, run a small OSWorld subset after installing the integration:

```bash
python3 scripts/install_into_osworld.py /path/to/OSWorld --with-runner --with-skills
```

Then run the relevant OSWorld command from the OSWorld checkout and include the result directory path in the pull request.
