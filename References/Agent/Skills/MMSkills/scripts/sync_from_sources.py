#!/usr/bin/env python3
"""Synchronize the public MMSkills subset from local development sources."""

from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

AGENT_FILES = [
    "general_agent.py",
    "general_skill_agent.py",
    "general_text_skill_agent.py",
    "_mm_skill_base.py",
    "_mm_skill_planner.py",
    "_mm_skill_state_cards.py",
    "_mm_skill_long_plan.py",
    "_mm_skill_adapter_base.py",
    "mm_skill_agent.py",
    "skill_loader.py",
    "task_skill_resolver.py",
]

OSWORLD_INTEGRATION_FILES = [
    "run.py",
    "lib_run_single.py",
    "lib_results_logger.py",
]

SELECTED_SKILLS = [
    "chrome/CHROME_Configure_Default_Search_Engine_And_Search_Preferences",
    "chrome/CHROME_Manage_Bookmarks_Reading_List_And_Shortcuts",
    "chrome/CHROME_Search_Web_And_Open_Target_Result",
    "gimp/GIMP_GIMP_Save_Projects_and_Export_Edited_Images",
    "libreoffice_calc/LIBREOFFICECALC_Create_Chart_on_Target_Sheet_with_Exact_Title_and_Type",
    "libreoffice_calc/LIBREOFFICECALC_Sort_and_Filter_Calc_Tables",
    "libreoffice_calc/LIBREOFFICECALC_Use_Formulas_and_Functions_in_Calc_Cells",
    "libreoffice_impress/LIBREOFFICEIMPRESS_Insert_and_Configure_Images_Audio_and_Interactive_Media",
    "libreoffice_impress/LIBREOFFICEIMPRESS_Manage_Slide_Structure_Ordering_and_Layouts",
    "libreoffice_writer/LIBREOFFICEWRITER_Find_and_Replace_Text_or_Formatting",
    "libreoffice_writer/LIBREOFFICEWRITER_Save_Export_and_Template_Writer_Documents",
    "os/OS_Manage_Files_and_Archives_in_Files",
    "os/OS_Query_System_State_in_Terminal",
    "thunderbird/THUNDERBIRD_Compose_Format_and_Send_Thunderbird_Emails",
    "vlc/VLC_Open_Local_Media_And_Verify_Playback_Surface",
    "vs_code/VSCODE_Search_and_Replace_Project_Content",
]


def ignore_generated(_: str, names: list[str]) -> set[str]:
    return {
        name
        for name in names
        if name in {".DS_Store", "__pycache__"} or name.endswith(".pyc")
    }


def copy_file(src: Path, dst: Path) -> None:
    if not src.exists():
        raise FileNotFoundError(src)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def copy_tree(src: Path, dst: Path) -> None:
    if not src.exists():
        raise FileNotFoundError(src)
    if dst.exists():
        shutil.rmtree(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst, ignore=ignore_generated)


def sync_agents(osworld_root: Path) -> None:
    mm_agents_src = osworld_root / "mm_agents"
    for filename in AGENT_FILES:
        copy_file(mm_agents_src / filename, REPO_ROOT / "mm_agents" / filename)
    copy_file(
        mm_agents_src / "utils" / "qwen_vl_utils.py",
        REPO_ROOT / "mm_agents" / "utils" / "qwen_vl_utils.py",
    )
    for filename in OSWORLD_INTEGRATION_FILES:
        copy_file(osworld_root / filename, REPO_ROOT / "osworld_integration" / filename)
    patch_global_mapping_resolver()


def patch_global_mapping_resolver() -> None:
    """Keep single-file mapping support in the released resolver."""
    resolver_path = REPO_ROOT / "mm_agents" / "task_skill_resolver.py"
    text = resolver_path.read_text(encoding="utf-8")
    text = text.replace(
        "and not self._mapping_file_for_domain(domain).exists()",
        "and not self._domain_mapping_file_exists(domain)",
    )
    text = text.replace(
        "if mapping_file.exists():",
        "if mapping_file is not None and mapping_file.exists():",
    )
    old = (
        "    def _mapping_file_for_domain(self, domain: str) -> Path:\n"
        "        if not self._mapping_root:\n"
        "            return Path()\n"
        "        if self._mapping_root.is_file():\n"
        "            return Path()\n"
        "        return self._mapping_root / domain / \"task_skill_mapping_generated.json\"\n"
    )
    new = (
        "    def _mapping_file_for_domain(self, domain: str) -> Optional[Path]:\n"
        "        if not self._mapping_root:\n"
        "            return None\n"
        "        if self._mapping_root.is_file():\n"
        "            return None\n"
        "        return self._mapping_root / domain / \"task_skill_mapping_generated.json\"\n"
        "\n"
        "    def _domain_mapping_file_exists(self, domain: str) -> bool:\n"
        "        mapping_file = self._mapping_file_for_domain(domain)\n"
        "        return bool(mapping_file is not None and mapping_file.exists())\n"
    )
    if old in text:
        text = text.replace(old, new)
    resolver_path.write_text(text, encoding="utf-8")


def sync_skills(skills_source_root: Path) -> set[str]:
    selected_basenames = {Path(item).name for item in SELECTED_SKILLS}
    target_root = REPO_ROOT / "skills_library"
    for rel_path in SELECTED_SKILLS:
        copy_tree(skills_source_root / rel_path, target_root / rel_path)
    return selected_basenames


def generate_global_mapping(skills_source_root: Path, selected_basenames: set[str]) -> None:
    mapping: dict[str, dict[str, list[str]]] = {}
    for domain_dir in sorted(path for path in skills_source_root.iterdir() if path.is_dir()):
        mapping_file = domain_dir / "task_skill_mapping_generated.json"
        if not mapping_file.exists():
            continue
        payload = json.loads(mapping_file.read_text(encoding="utf-8"))
        task_to_skills = payload.get("task_to_skills", {})
        if not isinstance(task_to_skills, dict):
            continue

        domain_mapping: dict[str, list[str]] = {}
        for task_id, task_payload in task_to_skills.items():
            if not isinstance(task_payload, dict):
                continue
            raw_skills = task_payload.get("skills", [])
            retained: list[str] = []
            for item in raw_skills:
                if isinstance(item, str):
                    skill_name = item
                elif isinstance(item, dict):
                    skill_name = str(item.get("skill_name", "") or "")
                else:
                    continue
                basename = Path(skill_name.strip()).name
                if basename in selected_basenames and basename not in retained:
                    retained.append(basename)
            if retained:
                domain_mapping[str(task_id)] = retained

        if domain_mapping:
            mapping[domain_dir.name] = domain_mapping

    output = REPO_ROOT / "task_skill_mappings" / "task_skill_mapping.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(mapping, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--osworld-root",
        type=Path,
        default=Path(os.environ.get("OSWORLD_ROOT", "../OSWorld")),
        help="Local OSWorld checkout containing the MMSkills agent implementation.",
    )
    parser.add_argument(
        "--skills-source-root",
        type=Path,
        default=Path(
            os.environ.get(
                "MMSKILLS_SOURCE_ROOT",
                "../generated_ubuntu_skills",
            )
        ),
        help="Source directory containing generated Ubuntu MMSkills.",
    )
    args = parser.parse_args()

    sync_agents(args.osworld_root.expanduser())
    selected_basenames = sync_skills(args.skills_source_root.expanduser())
    generate_global_mapping(args.skills_source_root.expanduser(), selected_basenames)
    print(f"Synchronized {len(AGENT_FILES)} agent files and {len(SELECTED_SKILLS)} skills.")


if __name__ == "__main__":
    main()
