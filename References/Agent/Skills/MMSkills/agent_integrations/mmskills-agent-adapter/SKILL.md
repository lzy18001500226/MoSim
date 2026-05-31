---
name: mmskills
description: Use MMSkills for GUI, computer-use, visual-agent, OSWorld, Ubuntu desktop, macOS, Minecraft, or Mario tasks where reusable multimodal skill packages can guide planning, state recognition, or verification. Also use when installing, downloading, searching, or adapting MMSkills packages for Codex, OpenClaw, Claude Code, or other agent products.
---

# MMSkills Agent Adapter

MMSkills Agent Adapter is a unified adapter for locating and using multimodal skill packages from the public MMSkills dataset. The same skill package schema should be used across Codex, OpenClaw, Claude Code, and other agent products; product-specific integration should stay in thin adapters, not in duplicated skill content.

## Asset Source

The full public skill library is hosted on Hugging Face:

- Dataset: https://huggingface.co/datasets/zhangkangning/mmskills
- Paper page: https://huggingface.co/papers/2605.13527
- Project website: https://deepexperience.github.io/MMSkills/skills.html

The dataset currently exposes 515 packages across Ubuntu, macOS, VAB-Minecraft, and Mario. Do not assume all packages are installed locally. Search and download only the relevant packages when needed.

## Quick Commands

Run these commands from this skill directory:

```bash
python scripts/search_skills.py "chrome bookmark" --package ubuntu
python scripts/download_skill.py ubuntu/chrome/CHROME_Manage_Bookmarks_Reading_List_And_Shortcuts
python scripts/inspect_skill.py ~/.cache/mmskills/skills/ubuntu/chrome/CHROME_Manage_Bookmarks_Reading_List_And_Shortcuts
```

Use `MMSKILLS_HOME=/path/to/cache` to store downloaded packages outside the default `~/.cache/mmskills`.

## Use Workflow

1. Infer the task surface: package, platform, app, and operation family.
2. Search the dataset index with `scripts/search_skills.py`.
3. Download the best-matching package with `scripts/download_skill.py` if it is not already local.
4. Read the package in this order:
   - `SKILL.md` for procedure, applicability, preconditions, and failure modes.
   - `runtime_state_cards.json` for compact state cues and verification signals.
   - `Images/` only when visual grounding, state comparison, or UI verification is needed.
5. Use the package as guidance, not as a hard coordinate script. Transfer the operational pattern, visible cues, and verification logic to the live task state.

## Cross-Agent Contract

MMSkills packages are product-neutral. Each package may contain:

```text
<package>/<domain>/<skill>/
├── SKILL.md
├── runtime_state_cards.json
├── plan.json
└── Images/
```

Codex, OpenClaw, and Claude Code should share this package format. The only product-specific pieces should be:

- where packages are cached;
- which tool opens images or screenshots;
- how the agent routes retrieved guidance back into its planner;
- whether the product can use visual references directly or should fall back to text-only cues.

Read `references/integration_targets.md` before implementing a new product adapter. Read `references/asset_sources.md` when changing dataset URLs, cache locations, or download behavior.

## When Visual Evidence Is Useful

Load visual references when:

- the task depends on recognizing a specific UI state, dialog, control, or result surface;
- text-only procedure is ambiguous;
- the package has a verification state that matches the current screenshot;
- the agent needs a recovery cue after a failed or uncertain GUI action.

Prefer focus crops for local control recognition and full frames for global state recognition.
