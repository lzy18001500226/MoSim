#!/usr/bin/env python3
"""Download one MMSkills package from the Hugging Face dataset."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


DATASET = "zhangkangning/mmskills"
REVISION = "main"
HF_DATASET_URL = f"https://huggingface.co/datasets/{DATASET}"
TREE_API = f"https://huggingface.co/api/datasets/{DATASET}/tree/{REVISION}"
RAW_BASE = f"{HF_DATASET_URL}/resolve/{REVISION}"


def cache_root() -> Path:
    return Path(os.environ.get("MMSKILLS_HOME", "~/.cache/mmskills")).expanduser()


def normalize_skill_path(value: str) -> str:
    value = value.strip()
    for marker in (f"{HF_DATASET_URL}/tree/{REVISION}/", f"{HF_DATASET_URL}/resolve/{REVISION}/"):
        if value.startswith(marker):
            value = value[len(marker) :]
    value = value.removeprefix("/")
    value = value.removesuffix("/SKILL.md")
    return value.rstrip("/")


def urlopen_with_retry(url: str, timeout: int = 120):
    request = urllib.request.Request(url, headers={"User-Agent": "mmskills-agent-adapter/0.1"})
    last_error: Exception | None = None
    for attempt in range(4):
        try:
            return urllib.request.urlopen(request, timeout=timeout)
        except urllib.error.HTTPError as error:
            last_error = error
            if error.code not in {429, 500, 502, 503, 504}:
                raise
        except urllib.error.URLError as error:
            last_error = error
        time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Failed to fetch {url}: {last_error}")


def fetch_json(url: str) -> list[dict]:
    with urlopen_with_retry(url, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def list_package_files(skill_dir: str) -> list[str]:
    encoded = urllib.parse.quote(skill_dir, safe="/")
    payload = fetch_json(f"{TREE_API}/{encoded}?recursive=1")
    files = [item["path"] for item in payload if item.get("type") == "file"]
    if not files:
        raise FileNotFoundError(f"No files found for Hugging Face dataset path: {skill_dir}")
    return files


def download_file(remote_path: str, local_path: Path) -> None:
    local_path.parent.mkdir(parents=True, exist_ok=True)
    encoded = urllib.parse.quote(remote_path, safe="/")
    with urlopen_with_retry(f"{RAW_BASE}/{encoded}", timeout=120) as response:
        with local_path.open("wb") as output:
            shutil.copyfileobj(response, output)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_path", help="Dataset package path, with or without trailing /SKILL.md")
    parser.add_argument("--dest", type=Path, default=None, help="Destination root; defaults to $MMSKILLS_HOME/skills")
    parser.add_argument("--text-only", action="store_true", help="Skip Images/ files and download text metadata only")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    args = parser.parse_args()

    skill_dir = normalize_skill_path(args.skill_path)
    dest_root = args.dest.expanduser() if args.dest else cache_root() / "skills"
    target_dir = dest_root / skill_dir

    if target_dir.exists() and not args.force:
        print(f"Already exists: {target_dir}")
        print("Use --force to overwrite, or inspect it directly.")
        return 0

    files = list_package_files(skill_dir)
    if args.text_only:
        files = [path for path in files if "/Images/" not in path]

    downloaded = 0
    for remote_path in files:
        local_path = dest_root / remote_path
        if local_path.exists() and not args.force:
            continue
        download_file(remote_path, local_path)
        downloaded += 1

    print(f"Downloaded {downloaded} files to {target_dir}")
    print(f"Inspect: python scripts/inspect_skill.py {target_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
