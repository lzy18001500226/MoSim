# MMSkills Asset Sources

The canonical public asset source is the Hugging Face dataset:

```text
https://huggingface.co/datasets/zhangkangning/mmskills
```

The dataset exposes complete package directories under paths such as:

```text
ubuntu/chrome/CHROME_Add_Shortcut_to_New_Tab_Page/
mac/productivity/Apple_Notes_Create_and_Open_Titled_Notes/
vab_minecraft/MINECRAFT_Craft_Tiered_Tools_And_Mining_Gates/
mario/Mario_cross_gaps_and_separated_platforms/
```

Each package should be treated as a portable unit containing `SKILL.md`, `runtime_state_cards.json`, optional planning metadata, and image references.

## Cache Locations

Default local cache:

```text
~/.cache/mmskills
```

Override with:

```bash
export MMSKILLS_HOME=/path/to/mmskills-cache
```

Downloaded packages are stored under:

```text
$MMSKILLS_HOME/skills/<package>/<domain>/<skill>/
```

## Download Strategy

Use the dataset server rows API for lightweight search metadata. Use the Hugging Face tree API to list files in a selected package. Use the raw `resolve/main` URLs to download package files.

Do not download the full dataset unless the user explicitly asks for it. The intended product behavior is on-demand retrieval of task-relevant packages.
