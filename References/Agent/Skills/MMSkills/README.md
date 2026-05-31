<h1 align="center">
  <img src="https://deepexperience.github.io/MMSkills/assets/mmskills_title.svg" alt="MMSkills" width="440"/><br>
  Towards Multimodal Skills for General Visual Agents
</h1>

<div align="center">

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache--2.0-green.svg)](LICENSE)
[![OSWorld](https://img.shields.io/badge/Benchmark-OSWorld-7b39e2.svg)](https://github.com/xlang-ai/OSWorld)
[![arXiv](https://img.shields.io/badge/arXiv-2605.13527-b31b1b.svg)](https://arxiv.org/abs/2605.13527)
[![Website](https://img.shields.io/badge/Website-MMSkills-0f766e.svg)](https://deepexperience.github.io/MMSkills/)
[![Skill Library](https://img.shields.io/badge/Skill%20Library-515%20MMSkills-4420A8.svg)](https://deepexperience.github.io/MMSkills/skills.html)
[![Demos](https://img.shields.io/badge/Demos-4%20Video%20Comparisons-a15c11.svg)](https://deepexperience.github.io/MMSkills/cases.html)
[![Agent Adapter](https://img.shields.io/badge/Agent%20Adapter-Codex%20%7C%20OpenClaw%20%7C%20Claude%20Code-0f766e.svg)](agent_integrations/mmskills-agent-adapter/)
[![Submit MMSkill](https://img.shields.io/badge/Submit-MMSkill%20Package-a15c11.svg)](https://deepexperience.github.io/MMSkills/submit.html)
[![GitHub stars](https://img.shields.io/github/stars/DeepExperience/MMSkills?style=social)](https://github.com/DeepExperience/MMSkills/stargazers)

</div>

<p align="center">
  <a href="#-latest-news">News</a> |
  <a href="https://arxiv.org/abs/2605.13527">Paper</a> |
  <a href="https://deepexperience.github.io/MMSkills/">Website</a> |
  <a href="https://deepexperience.github.io/MMSkills/skills.html">Skill Library</a> |
  <a href="https://deepexperience.github.io/MMSkills/cases.html">Demos</a> |
  <a href="#-agent-adapter">Agent Adapter</a> |
  <a href="#-community-submissions">Submit MMSkills</a> |
  <a href="#-overview">Overview</a> |
  <a href="#-installation">Installation</a> |
  <a href="#-quick-start">Quick Start</a> |
  <a href="#-citation">Citation</a>
</p>

<h5 align="center">If you find this project helpful, please give us a star ⭐ for the latest updates.</h5>

<div align="center">
  <img src="https://readme-typing-svg.herokuapp.com?font=Orbitron&size=18&duration=3000&pause=1000&color=4420A8&center=true&vCenter=true&width=820&lines=Welcome+to+MMSkills;Reusable+Multimodal+Procedural+Knowledge;Skill-Augmented+Visual+Agents+for+Desktop+Tasks" alt="Typing Animation purple MMSkills" />
</div>

## 📣 Latest News

- 🏆 **[May 2026]** MMSkills ranked **#1 on Hugging Face Daily Papers** on **2026.5.18**.
- 🤗 **[May 2026]** The MMSkills dataset is now available on [Hugging Face Datasets](https://huggingface.co/datasets/zhangkangning/mmskills); the paper page is also available on [Hugging Face Papers](https://huggingface.co/papers/2605.13527).
- 🌐 **[May 2026]** The project website is live with [demo comparisons](https://deepexperience.github.io/MMSkills/cases.html) and a searchable [MMSkills Library](https://deepexperience.github.io/MMSkills/skills.html) indexing **515 skills** across Ubuntu, macOS, VAB-Minecraft, and Mario.
- 🚀 **[May 2026]** The public release includes a compact multimodal desktop-skill subset, OSWorld-ready runtime adapters, task mappings, and model-agnostic skill modes.
- 🔌 **[May 2026]** We added the **MMSkills Agent Adapter** for Codex, OpenClaw, and Claude Code, with one-line Codex installation and on-demand Hugging Face skill retrieval.
- 🌱 **[May 2026]** Community MMSkill submissions are open for new domains such as autonomous driving, robotics, mobile agents, and beyond.

## 🎬 Demos

Four OSWorld demos compare the same task under no skills, text-only skill guidance, and multimodal MMSkills. These videos show selected trajectory excerpts to highlight behavioral differences between the three settings; they are not complete end-to-end trajectories. To keep GUI text readable in the GitHub README, each case uses three separate 1080p MP4 players instead of a compressed side-by-side composite. The full video layout is also available at [deepexperience.github.io/MMSkills/cases.html](https://deepexperience.github.io/MMSkills/cases.html).

<details open>
<summary><h3>1. Calc merged headers</h3></summary>

<table>
  <tr>
    <th>No skills</th>
    <th>Text-only</th>
    <th>MMSkills</th>
  </tr>
  <tr>
    <td><video src="https://github.com/user-attachments/assets/cfe1cde8-5da1-4f69-9e90-1a3ee0b82023" width="280" controls></video></td>
    <td><video src="https://github.com/user-attachments/assets/ce092ee3-4e10-44cb-bfd3-bb4780e5c9c4" width="280" controls></video></td>
    <td><video src="https://github.com/user-attachments/assets/24c8ca7a-a028-422a-8207-52b14c8b5d1e" width="280" controls></video></td>
  </tr>
</table>

Creates Sheet2, merges the requested header ranges, and writes the target labels. MMSkills follows the intended spreadsheet workflow while the other modes make slower or less reliable progress.

</details>

<details>
<summary><h3>2. VS Code local VSIX install</h3></summary>

<table>
  <tr>
    <th>No skills</th>
    <th>Text-only</th>
    <th>MMSkills</th>
  </tr>
  <tr>
    <td><video src="https://github.com/user-attachments/assets/2296cd12-733e-4f25-95d5-402b2845ae37" width="280" controls></video></td>
    <td><video src="https://github.com/user-attachments/assets/4cfdfe99-6bb6-4a40-86ae-c7703eb1182c" width="280" controls></video></td>
    <td><video src="https://github.com/user-attachments/assets/90abd134-1e2c-4bbd-833f-83938b81383a" width="280" controls></video></td>
  </tr>
</table>

Installs a local VSIX extension through the GUI workflow. The comparison highlights how multimodal skill references reduce detours around extension discovery and confirmation steps.

</details>

<details>
<summary><h3>3. GIMP text-layer move</h3></summary>

<table>
  <tr>
    <th>No skills</th>
    <th>Text-only</th>
    <th>MMSkills</th>
  </tr>
  <tr>
    <td><video src="https://github.com/user-attachments/assets/6f0d27ba-25a4-4b31-b34b-8480eb3d5fa0" width="280" controls></video></td>
    <td><video src="https://github.com/user-attachments/assets/57a4719d-0d62-4c00-a0b0-befecf5ac256" width="280" controls></video></td>
    <td><video src="https://github.com/user-attachments/assets/0e221a36-29a8-4b7f-8eac-1af5e492fbc7" width="280" controls></video></td>
  </tr>
</table>

Moves a specific text layer in GIMP. The multimodal skill package provides visual grounding for the relevant layer and toolbar state, making the edit path clearer.

</details>

<details>
<summary><h3>4. Calc chart creation</h3></summary>

<table>
  <tr>
    <th>No skills</th>
    <th>Text-only</th>
    <th>MMSkills</th>
  </tr>
  <tr>
    <td><video src="https://github.com/user-attachments/assets/55a01c94-a748-4a22-9c40-cab707aca386" width="280" controls></video></td>
    <td><video src="https://github.com/user-attachments/assets/ca310dd1-252a-4608-a0c7-7e613b31ee08" width="280" controls></video></td>
    <td><video src="https://github.com/user-attachments/assets/1a485289-ceb5-4601-8e16-1be439593145" width="280" controls></video></td>
  </tr>
</table>

Builds the requested clustered chart in LibreOffice Calc. The side-by-side run shows the effect of reusable spreadsheet procedure knowledge on multi-step GUI manipulation.

</details>

## 💡 Overview

**MMSkills** is a framework for representing, loading, and using reusable multimodal procedural knowledge for visual agents. Each skill combines textual procedure guidance, compact state-card metadata, and optional visual references. At inference time, the agent keeps only lightweight skill hints in the main context, then opens a temporary skill branch when task state suggests that a skill may help.

<div align="center">
  <img src="https://deepexperience.github.io/MMSkills/assets/full_figure.png" width="95%" alt="MMSkills overview" />
</div>

This repository is a focused open-source release. It is not a full OSWorld fork; instead, it provides the MMSkill runtime layer, an install script, OSWorld runner patches, task-to-skill mappings, and a representative public skill library.

Project pages:

- [arXiv paper](https://arxiv.org/abs/2605.13527)
- [MMSkills website](https://deepexperience.github.io/MMSkills/)
- [Searchable Multidomain Skill Library](https://deepexperience.github.io/MMSkills/skills.html)
- [Demo video comparisons](https://deepexperience.github.io/MMSkills/cases.html)

Website frontend files are published from the `gh-pages` branch. The `main` branch is kept focused on the open-source code, runtime integration, skills, and documentation.

## ✨ Highlights

<table>
  <tr>
    <td width="50%"><strong>🧩 Self-contained skill packages</strong><br>Each skill directory contains <code>SKILL.md</code>, runtime state cards, audit state cards, and visual keyframes.</td>
    <td width="50%"><strong>👁️ Multimodal evidence gating</strong><br>The runtime first decides whether visual references are needed, then loads only the requested state views.</td>
  </tr>
  <tr>
    <td width="50%"><strong>🧠 Branch-loaded planning</strong><br>A temporary planner branch consults selected skills and returns concise guidance, fallback advice, and verification cues.</td>
    <td width="50%"><strong>🔌 OSWorld ready</strong><br>Helper scripts install the agent files, runner integration, skills, and task mappings into a local OSWorld checkout.</td>
  </tr>
  <tr>
    <td width="50%"><strong>⚡ Agent-product adapter</strong><br>The <code>mmskills-agent-adapter</code> can be installed as a Codex skill and reused by OpenClaw or Claude Code through the same package contract.</td>
    <td width="50%"><strong>📦 On-demand skill retrieval</strong><br>Agents search the 515-skill Hugging Face library, download only task-relevant packages, then read <code>SKILL.md</code>, runtime states, and visual references as needed.</td>
  </tr>
  <tr>
    <td width="50%"><strong>🌱 Community-extensible library</strong><br>Researchers can submit MMSkill packages for new domains such as autonomous driving, robotics, mobile apps, web agents, and games.</td>
    <td width="50%"><strong>✅ Review-first publishing</strong><br>Submissions open GitHub issues, notify maintainers, and are reviewed before being normalized into the public Hugging Face library and website.</td>
  </tr>
</table>

## 🔌 Agent Adapter

The [`mmskills-agent-adapter`](agent_integrations/mmskills-agent-adapter/) module turns MMSkills into an installable, product-neutral skill adapter for agent systems. It keeps one shared MMSkills package format across Codex, OpenClaw, Claude Code, and future agent products instead of maintaining separate copies for each ecosystem.

The adapter is intentionally lightweight. It does not bundle the full 515-skill asset set inside the repository branch. Instead, it points agents to the public [Hugging Face MMSkills dataset](https://huggingface.co/datasets/zhangkangning/mmskills), searches the metadata index, and downloads only the skill package needed for the current task.

One-line Codex install:

```bash
curl -fsSL https://raw.githubusercontent.com/DeepExperience/MMSkills/main/scripts/install_codex_mmskills.sh | bash
```

Direct Codex skill-installer form:

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo DeepExperience/MMSkills \
  --path agent_integrations/mmskills-agent-adapter
```

After restarting Codex, invoke `$mmskills` for GUI-agent or computer-use tasks. The adapter scripts provide the standard flow:

```bash
python scripts/search_skills.py "chrome bookmark" --package ubuntu
python scripts/download_skill.py ubuntu/chrome/CHROME_Manage_Bookmarks_Reading_List_And_Shortcuts
python scripts/inspect_skill.py ~/.cache/mmskills/skills/ubuntu/chrome/CHROME_Manage_Bookmarks_Reading_List_And_Shortcuts
```

For OpenClaw and Claude Code, use the same adapter contract: call the search/download scripts, parse `SKILL.md` and `runtime_state_cards.json`, and route `Images/` into the product's visual grounding or verification layer only when visual evidence is needed.

## 🌱 Community Submissions

We welcome MMSkill packages from new domains. A submission can be a single reusable skill or a new domain collection, such as autonomous driving, robotics, mobile agents, browser workflows, scientific software, games, or other visual-agent environments.

Submit through the website entrypoint or directly through the GitHub issue form:

- Website entry: [deepexperience.github.io/MMSkills/submit.html](https://deepexperience.github.io/MMSkills/submit.html)
- GitHub issue form: [Submit an MMSkill package](https://github.com/DeepExperience/MMSkills/issues/new?template=skill_submission.yml)
- Format guide: [docs/submit_mmskills.md](docs/submit_mmskills.md)

Each submission creates a GitHub issue assigned to the maintainer account, so maintainers can receive email notifications through GitHub's repository notification settings. After review, accepted packages are normalized into the MMSkills library, uploaded to the public Hugging Face dataset, and surfaced on the website Skill Library.

## 🗂️ Repository Layout

```text
MMSkills/
├── agent_integrations/        # Codex/OpenClaw/Claude Code agent adapters and download helpers
├── mm_agents/                 # MMSkill runtime architecture and model adapters
├── osworld_integration/       # MMSkills-aware OSWorld runner files
├── skills_library/            # Public multimodal skills subset for direct runtime use
├── task_skill_mappings/       # OSWorld task-to-skill mapping for released skills
└── scripts/
    ├── install_into_osworld.py # Install this release into an OSWorld checkout
    └── sync_from_sources.py    # Maintainer sync helper for source checkouts
```

## 🧠 Architecture

The public runtime entrypoint is [`mm_agents/mm_skill_agent.py`](mm_agents/mm_skill_agent.py), exposed in OSWorld as:

```bash
--agent_type mm_skill
```

The architecture is model-agnostic. A main visual agent receives compact skill hints; when a skill may apply, the runtime opens a branch that decides whether visual evidence is needed, requests relevant state views, compares them with the live screenshot, and returns structured guidance for the next grounded action.

The reference integration supports:

- `mm_skill`: multimodal branch-loaded skill consultation.
- `general_text_skill`: text-only skill consultation for ablation and lightweight runs.
- `general`: baseline model-agnostic screenshot-to-pyautogui visual-agent routing.

Legacy `gemini`, `gemini_skill`, and `gemini_text_skill` CLI names are still accepted by the runner as aliases for compatibility, but the public files and recommended commands use the model-agnostic `general*` names.

Any screenshot-capable VLM served through an OpenAI-compatible chat-completions API can use the same `general*` and `mm_skill` interfaces by setting `--model`, `--api_model` when needed, `--base_url`, and `--api_key`.

## 🔧 Installation

### 1. Clone MMSkills

```bash
git clone https://github.com/DeepExperience/MMSkills.git
cd MMSkills
```

### 2. Install Python dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Install into OSWorld

Clone and install OSWorld following its upstream instructions, then run:

```bash
python3 scripts/install_into_osworld.py /path/to/OSWorld --with-runner --with-skills
```

This copies the MMSkill agent files into `OSWorld/mm_agents/`, installs the MMSkills-aware runner files, and copies the released `skills_library/` plus `task_skill_mappings/`.

### 4. Configure model endpoints

For an OpenAI-compatible endpoint:

```bash
export OPENAI_BASE_URL="https://your-openai-compatible-endpoint/v1"
export OPENAI_API_KEY="your_api_key"
```

For native Gemini-compatible routing, pass `--api_backend gemini` and set:

```bash
export GEMINI_BASE_URL="https://your-gemini-compatible-endpoint/v1"
export GEMINI_API_KEY="your_api_key"
```

### 5. Install the Codex Agent Adapter

MMSkills also ships a lightweight agent-product adapter under [`agent_integrations/mmskills-agent-adapter/`](agent_integrations/mmskills-agent-adapter/). The adapter is installable as a Codex skill and points agents to the full Hugging Face skill dataset for on-demand retrieval. See [Agent Adapter](#-agent-adapter) for the full cross-agent contract.

One-line Codex install:

```bash
curl -fsSL https://raw.githubusercontent.com/DeepExperience/MMSkills/main/scripts/install_codex_mmskills.sh | bash
```

Direct Codex skill-installer form:

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo DeepExperience/MMSkills \
  --path agent_integrations/mmskills-agent-adapter
```

After restarting Codex, use `$mmskills` to search and load task-relevant packages. The same adapter contract is intended for OpenClaw and Claude Code: share the MMSkills package format, keep product-specific behavior in thin adapters, and download only the skills needed for the current task from [Hugging Face Datasets](https://huggingface.co/datasets/zhangkangning/mmskills).

## 🏃 Quick Start

Run commands from the OSWorld checkout after installation.

### Baseline Without Skills

```bash
python run.py \
  --agent_type general \
  --model gpt-4o \
  --api_backend openai \
  --observation_type screenshot \
  --action_space pyautogui \
  --max_steps 20 \
  --test_all_meta_path evaluation_examples/test_nogdrive.json \
  --domain chrome \
  --result_dir results/no_skills
```

### Text-Only Skills

```bash
python run.py \
  --agent_type general_text_skill \
  --model gpt-4o \
  --api_backend openai \
  --observation_type screenshot \
  --action_space pyautogui \
  --max_steps 20 \
  --skills_library_dir skills_library \
  --task_skill_mapping_root task_skill_mappings/task_skill_mapping.json \
  --skill_mode text_only \
  --text_skill_mode branch_planner \
  --test_all_meta_path evaluation_examples/test_nogdrive.json \
  --domain chrome \
  --result_dir results/text_only
```

### Multimodal MMSkill Agent

```bash
python run.py \
  --agent_type mm_skill \
  --model gpt-4o \
  --api_backend openai \
  --observation_type screenshot \
  --action_space pyautogui \
  --max_steps 20 \
  --skills_library_dir skills_library \
  --task_skill_mapping_root task_skill_mappings/task_skill_mapping.json \
  --skill_mode multimodal \
  --task_skill_top_k 6 \
  --save_conversation_json \
  --test_all_meta_path evaluation_examples/test_nogdrive.json \
  --domain chrome \
  --result_dir results/mm_skill_multimodal
```

Use `--domain all` for the full no-Google-Drive OSWorld split. The runner writes trajectories, screenshots, `skill_invocations.json`, `skill_usage_summary.json`, and aggregate metrics under the selected `--result_dir`.

## 📚 Skill Library

The website indexes **515 skills** from the open-source Ubuntu, macOS, VAB-Minecraft, and Mario skill assets. Each skill card links to a structured view of its `SKILL.md`, runtime state cards, and ordered visual references.

Browse the live library at [deepexperience.github.io/MMSkills/skills.html](https://deepexperience.github.io/MMSkills/skills.html).

The repository also includes a compact runtime-ready subset under [`skills_library/`](skills_library/) for immediate OSWorld integration.

## 📦 Skill Package Format

```text
skills_library/<domain>/<skill_name>/
├── SKILL.md                  # Procedure, applicability, transfer limits, checks
├── runtime_state_cards.json  # Compact state/view metadata used at inference time
├── state_cards.json          # Audit-grade state metadata for inspection
├── plan.json                 # Generated plan metadata, when available
└── Images/                   # Full frames, focus crops, before/after references
```

The main agent sees only concise skill names and state hints. Detailed visual evidence is loaded lazily by the branch planner, which keeps the main context compact while preserving access to state-specific multimodal references.

`runtime_state_cards.json` is the inference-facing version: it contains compact state descriptions, when-to-use rules, visible cues, verification cues, and selected image views for branch-time loading. `state_cards.json` is the richer authoring/audit version: it keeps transfer-limit notes, highlight targets, grounding queries, bounding boxes, crop decisions, and evidence-source metadata for inspection and regeneration.

## 🧪 Outputs

MMSkills adds skill-aware artifacts to OSWorld result directories:

| File | Purpose |
|------|---------|
| `skill_invocations.json` | Per-branch consultation records, selected states, requested views, and planner outputs |
| `skill_usage_summary.json` | Aggregate skill counts, branch success counts, exhausted skills, and final actions |
| `conversation.json` | Optional main and branch conversation trace when `--save_conversation_json` is enabled |

## 🤝 Contributing

Contributions are welcome for new skills, runtime integrations, documentation, and reproducibility fixes. Please read [`CONTRIBUTING.md`](CONTRIBUTING.md) before opening an issue or pull request.

## 📄 License

This project is released under the [Apache License 2.0](LICENSE). Portions of the OSWorld integration are derived from OSWorld; see [NOTICE](NOTICE) for attribution details.

## 📝 Citation

If you use MMSkills in your research or applications, please cite our arXiv paper:

```bibtex
@misc{zhang2026mmskills,
  title = {MMSkills: Towards Multimodal Skills for General Visual Agents},
  author = {Kangning Zhang and Shuai Shao and Qingyao Li and Jianghao Lin and Lingyue Fu and Shijian Wang and Wenxiang Jiao and Yuan Lu and Weiwen Liu and Weinan Zhang and Yong Yu},
  year = {2026},
  eprint = {2605.13527},
  archivePrefix = {arXiv},
  primaryClass = {cs.AI},
  url = {https://arxiv.org/abs/2605.13527}
}
```

You can also use the machine-readable citation metadata in [`CITATION.cff`](CITATION.cff).
