# Integration Targets

MMSkills should use one product-neutral package format across agent products. Avoid separate Codex, Claude Code, and OpenClaw skill content unless a product cannot read the shared package shape.

## Codex

Codex can install this adapter as a normal skill because this directory contains `SKILL.md`.

Direct install through the Codex skill installer:

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo DeepExperience/MMSkills \
  --path agent_integrations/mmskills-agent-adapter
```

After installation, restart Codex and invoke `$mmskills` when the task benefits from reusable visual-agent procedural knowledge.

## Claude Code / CC

Use the same adapter content and scripts. If the local Claude Code setup supports skill-style folders, copy or symlink this directory into its skill location. If it does not, keep this directory in the project and instruct the agent to read `SKILL.md`, then use the scripts for search and package retrieval.

The shared package format remains unchanged. Only the local install location and image-viewing mechanism should differ.

## OpenClaw

OpenClaw should call the same search and download scripts, then load selected package assets into its planner or tool layer:

1. Search metadata with `scripts/search_skills.py`.
2. Download the selected package with `scripts/download_skill.py`.
3. Parse `SKILL.md` and `runtime_state_cards.json`.
4. Route image files from `Images/` into OpenClaw's visual grounding or state-matching component when needed.

## Text-Only Fallback

If an agent cannot consume images, it can still use:

- `SKILL.md`
- `runtime_state_cards.json`
- image labels and visible cues from runtime cards

This is a weaker mode than multimodal use, but it preserves the same package source and avoids a separate text-only fork.
