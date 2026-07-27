#!/usr/bin/env python3
"""Create a minimal project-local CoAgent adapter scaffold."""

from __future__ import annotations

import argparse
import datetime as _dt
import json
from pathlib import Path
from string import Template
import sys


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
ASSET_ROOT = SKILL_DIR / "assets" / "project_adapter"

TEMPLATE_FILES = {
    "README.md": ASSET_ROOT / "README.md.template",
    "dispatch/department_threads.json": ASSET_ROOT
    / "dispatch"
    / "department_threads.json.template",
    "docs/adapters/README.md": ASSET_ROOT / "docs" / "adapters" / "README.md.template",
    "protocol/README.md": ASSET_ROOT / "protocol" / "README.md.template",
}


def _resolve(path_text: str) -> Path:
    return Path(path_text).expanduser().resolve()


def _project_name(project_root: Path) -> str:
    return project_root.name or "Project"


def _render(template_path: Path, values: dict[str, str]) -> str:
    text = template_path.read_text(encoding="utf-8")
    # Templates use {{NAME}} to stay readable in Markdown/JSON.
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    # Keep Template available for future $NAME additions without failing.
    return Template(text).safe_substitute(values)


def build_plan(project_root: Path, global_coagent_root: Path, overwrite: bool) -> dict:
    adapter_root = project_root / "CoAgent"
    created_at = _dt.datetime.now().astimezone().isoformat(timespec="seconds")
    values = {
        "PROJECT_NAME": _project_name(project_root),
        "PROJECT_ROOT": str(project_root),
        "GLOBAL_COAGENT_ROOT": str(global_coagent_root),
        "CREATED_AT": created_at,
    }
    values.update({f"{key}_JSON": json.dumps(value, ensure_ascii=False) for key, value in values.items()})
    files = []
    for rel, template in TEMPLATE_FILES.items():
        target = adapter_root / rel
        exists = target.exists()
        action = "overwrite" if exists and overwrite else "skip" if exists else "create"
        files.append(
            {
                "relative_path": str(Path("CoAgent") / rel),
                "target": str(target),
                "template": str(template),
                "exists": exists,
                "action": action,
                "content": _render(template, values),
            }
        )
    return {
        "schema": "coagent.project_bootstrap.plan.v1",
        "project_root": str(project_root),
        "adapter_root": str(adapter_root),
        "global_coagent_root": str(global_coagent_root),
        "global_core_exists": global_coagent_root.exists(),
        "overwrite": overwrite,
        "files": files,
        "summary": {
            "create_count": sum(1 for f in files if f["action"] == "create"),
            "skip_count": sum(1 for f in files if f["action"] == "skip"),
            "overwrite_count": sum(1 for f in files if f["action"] == "overwrite"),
        },
    }


def apply_plan(plan: dict) -> list[dict]:
    results = []
    adapter_root = Path(plan["adapter_root"]).resolve()
    for item in plan["files"]:
        target = Path(item["target"]).resolve()
        try:
            target.relative_to(adapter_root)
        except ValueError as exc:
            raise RuntimeError(f"refusing to write outside adapter root: {target}") from exc

        if item["action"] == "skip":
            results.append({"target": str(target), "action": "skip", "ok": True})
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(item["content"], encoding="utf-8", newline="\n")
        results.append({"target": str(target), "action": item["action"], "ok": True})
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=".", help="Target project root.")
    parser.add_argument(
        "--global-coagent-root",
        default=r"C:\Users\HP\Desktop\CoAgent",
        help="Reusable global CoAgent core path to record as a pointer.",
    )
    parser.add_argument("--apply", action="store_true", help="Write planned files.")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing generated target files.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    args = parser.parse_args(argv)

    project_root = _resolve(args.project_root)
    global_coagent_root = _resolve(args.global_coagent_root)
    plan = build_plan(project_root, global_coagent_root, args.overwrite)

    output = {"plan": plan, "applied": False, "results": []}
    if args.apply:
        output["results"] = apply_plan(plan)
        output["applied"] = True

    if args.json:
        # Avoid dumping template contents into normal console output.
        compact = json.loads(json.dumps(output))
        for item in compact["plan"]["files"]:
            item.pop("content", None)
        print(json.dumps(compact, ensure_ascii=False, indent=2))
    else:
        mode = "APPLY" if args.apply else "PLAN"
        print(f"[{mode}] project_root={project_root}")
        print(f"[{mode}] adapter_root={plan['adapter_root']}")
        print(f"[{mode}] global_coagent_root={global_coagent_root}")
        print(f"[{mode}] global_core_exists={plan['global_core_exists']}")
        for item in plan["files"]:
            print(f"{item['action']}: {item['relative_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
