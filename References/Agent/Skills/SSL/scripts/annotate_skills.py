"""Run the public SSL skill-annotation pipeline.

This script is a clean, provider-agnostic implementation of the annotation
workflow described in docs/normalizer_prompt.md. It intentionally avoids
local API keys, provider logs, and project-specific checkpoints.

Example:

    python scripts/annotate_skills.py \
        --source-root path/to/skills \
        --output-dir annotated_skill_corpus \
        --model deepseek-v3.2 \
        --base-url https://api.deepseek.com/v1 \
        --api-key-env DEEPSEEK_API_KEY

The source root is expected to contain one or more skill directories with a
SKILL.md file. The output directory will contain:

    ssl_records/<slug>.json
    skill_metadata.json
    slug_order.json
    manifest.json
    failures.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from validate_ssl_record import validate


DEFAULT_BASE_URL = "https://api.deepseek.com/v1"
DEFAULT_MODEL = "deepseek-v3.2"
DEFAULT_MAX_RETRIES = 7
DEFAULT_TIMEOUT_SECONDS = 180
DEFAULT_TEMPERATURE = 0.1


@dataclass
class SkillSource:
    slug: str
    skill_dir: Path
    skill_md: Path
    text: str


@dataclass
class AnnotationResult:
    slug: str
    ok: bool
    attempts: int
    record_path: str | None = None
    errors: list[str] | None = None


def stable_slug(path: Path) -> str:
    raw = path.name.strip()
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", raw).strip("-").lower()
    if slug:
        return slug
    digest = hashlib.sha1(str(path).encode("utf-8")).hexdigest()[:10]
    return f"skill-{digest}"


def discover_skill_sources(source_root: Path) -> list[SkillSource]:
    sources: list[SkillSource] = []
    for skill_md in sorted(source_root.rglob("SKILL.md")):
        text = skill_md.read_text(encoding="utf-8", errors="replace").strip()
        if not text:
            continue
        skill_dir = skill_md.parent
        sources.append(
            SkillSource(
                slug=stable_slug(skill_dir),
                skill_dir=skill_dir,
                skill_md=skill_md,
                text=text,
            )
        )
    return sources


def read_doc(repo_root: Path, relative: str) -> str:
    path = repo_root / relative
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace").strip()


def build_prompt(repo_root: Path, source: SkillSource, repair_errors: list[str] | None = None) -> list[dict[str, str]]:
    guidelines = read_doc(repo_root, "docs/ssl_guidelines.md")
    prompt_contract = read_doc(repo_root, "docs/normalizer_prompt.md")

    system = (
        "You are an SSL skill normalizer. Convert the provided SKILL.md artifact "
        "into one valid SSL JSON object. Output JSON only. Do not include markdown, "
        "comments, explanations, or source text outside the JSON object."
    )

    user_parts = [
        "Follow the SSL normalizer prompt contract below.",
        "",
        "## Prompt Contract",
        prompt_contract,
        "",
        "## Source Metadata",
        json.dumps(
            {
                "slug": source.slug,
                "skill_dir": str(source.skill_dir),
                "source_file": str(source.skill_md),
            },
            ensure_ascii=False,
            indent=2,
        ),
        "",
        "## SKILL.md",
        source.text,
        "",
        "## SSL Schema Guidelines",
        guidelines,
        "",
        "Return exactly one JSON object with top-level fields: skill, scenes, logic_steps.",
    ]
    if repair_errors:
        user_parts.extend(
            [
                "",
                "## Previous Validation Errors",
                "Repair the JSON so these errors no longer occur. Do not add unsupported behavior.",
                "\n".join(f"- {error}" for error in repair_errors),
            ]
        )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": "\n".join(user_parts)},
    ]


class OpenAICompatibleClient:
    def __init__(self, base_url: str, api_key: str, model: str, timeout: int, temperature: float) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.temperature = temperature

    def chat(self, messages: list[dict[str, str]]) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "response_format": {"type": "json_object"},
        }
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"provider HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"provider request failed: {exc}") from exc

        try:
            return body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"unexpected provider response: {body}") from exc


def extract_json_object(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        obj = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start < 0 or end <= start:
            raise
        obj = json.loads(cleaned[start : end + 1])
    if not isinstance(obj, dict):
        raise ValueError("normalizer output must be a JSON object")
    return obj


def annotate_one(
    source: SkillSource,
    client: OpenAICompatibleClient,
    repo_root: Path,
    record_dir: Path,
    max_retries: int,
    sleep_seconds: float,
) -> AnnotationResult:
    repair_errors: list[str] | None = None
    attempts = 0
    last_errors: list[str] = []

    for attempt in range(max_retries + 1):
        attempts = attempt + 1
        messages = build_prompt(repo_root, source, repair_errors)
        try:
            response_text = client.chat(messages)
            record = extract_json_object(response_text)
        except Exception as exc:  # Provider and parsing errors should trigger retry.
            last_errors = [str(exc)]
            repair_errors = last_errors
            time.sleep(sleep_seconds)
            continue

        errors = validate(record)
        if not errors:
            record_path = record_dir / f"{source.slug}.json"
            record_path.write_text(
                json.dumps(record, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            return AnnotationResult(
                slug=source.slug,
                ok=True,
                attempts=attempts,
                record_path=str(record_path),
            )
        last_errors = errors
        repair_errors = errors
        time.sleep(sleep_seconds)

    return AnnotationResult(
        slug=source.slug,
        ok=False,
        attempts=attempts,
        errors=last_errors,
    )


def as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    return []


def derive_metadata(slug: str, record: dict[str, Any]) -> dict[str, Any]:
    skill = record.get("skill", {})
    scenes = as_list(record.get("scenes"))
    steps = as_list(record.get("logic_steps"))

    scene_profile: dict[str, int] = {}
    for scene in scenes:
        scene_type = scene.get("scene_type")
        if scene_type:
            scene_profile[scene_type] = scene_profile.get(scene_type, 0) + 1

    resource_scopes = [step.get("resource_scope") for step in steps if step.get("resource_scope")]
    act_types = [step.get("act_type") for step in steps if step.get("act_type")]
    dependencies = as_list(skill.get("dependencies"))
    control = skill.get("control_flow_features") or {}

    return {
        "slug": slug,
        "skill_name": skill.get("skill_name"),
        "skill_goal": skill.get("skill_goal"),
        "tags": as_list(skill.get("tags")),
        "control_flow_features": {
            "has_branch": bool(control.get("has_branch")),
            "has_loop": bool(control.get("has_loop")),
            "has_tool_call": bool(control.get("has_tool_call")),
            "touches_sensitive_resources": bool(control.get("touches_sensitive_resources")),
        },
        "scene_profile": scene_profile,
        "resource_scopes": resource_scopes,
        "act_types": act_types,
        "dependencies": dependencies,
        "intent_signature": as_list(skill.get("intent_signature")),
        "top_pattern": skill.get("top_pattern"),
    }


def export_metadata(output_dir: Path) -> None:
    record_dir = output_dir / "ssl_records"
    rows: list[dict[str, Any]] = []
    slugs: list[str] = []
    for path in sorted(record_dir.glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        errors = validate(record)
        if errors:
            raise RuntimeError(f"{path} failed validation during metadata export: {errors}")
        slug = path.stem
        slugs.append(slug)
        rows.append(derive_metadata(slug, record))

    (output_dir / "skill_metadata.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (output_dir / "slug_order.json").write_text(
        json.dumps(slugs, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_manifest(
    output_dir: Path,
    source_count: int,
    results: list[AnnotationResult],
    model: str,
    base_url: str,
    max_retries: int,
) -> None:
    ok = [r for r in results if r.ok]
    manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source_count": source_count,
        "valid_records": len(ok),
        "failed_records": len(results) - len(ok),
        "normalization_yield": round(len(ok) / source_count, 6) if source_count else 0,
        "model": model,
        "base_url": base_url,
        "max_retries": max_retries,
        "outputs": {
            "records": "ssl_records/",
            "metadata": "skill_metadata.json",
            "slug_order": "slug_order.json",
            "failures": "failures.json",
        },
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    failures = [r.__dict__ for r in results if not r.ok]
    (output_dir / "failures.json").write_text(
        json.dumps(failures, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Annotate SKILL.md artifacts into SSL JSON records.")
    parser.add_argument("--source-root", required=True, type=Path, help="Root containing skill directories.")
    parser.add_argument("--output-dir", required=True, type=Path, help="Directory for annotation outputs.")
    parser.add_argument("--model", default=os.getenv("SSL_NORMALIZER_MODEL", DEFAULT_MODEL))
    parser.add_argument("--base-url", default=os.getenv("SSL_NORMALIZER_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--api-key-env", default="SSL_NORMALIZER_API_KEY")
    parser.add_argument("--max-retries", type=int, default=DEFAULT_MAX_RETRIES)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE)
    parser.add_argument("--sleep-seconds", type=float, default=1.0)
    parser.add_argument("--limit", type=int, default=None, help="Optional limit for smoke tests.")
    parser.add_argument("--resume", action="store_true", help="Skip records already present in ssl_records/.")
    parser.add_argument("--dry-run", action="store_true", help="Discover sources and print counts without calling a model.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv or sys.argv[1:])
    repo_root = Path(__file__).resolve().parents[1]
    source_root = args.source_root.resolve()
    output_dir = args.output_dir.resolve()
    record_dir = output_dir / "ssl_records"

    sources = discover_skill_sources(source_root)
    if args.limit is not None:
        sources = sources[: args.limit]

    if args.dry_run:
        print(f"Discovered {len(sources)} SKILL.md files under {source_root}")
        for source in sources[:5]:
            print(f"- {source.slug}: {source.skill_md}")
        return

    api_key = os.getenv(args.api_key_env)
    if not api_key:
        raise SystemExit(f"Missing API key environment variable: {args.api_key_env}")

    output_dir.mkdir(parents=True, exist_ok=True)
    record_dir.mkdir(parents=True, exist_ok=True)

    client = OpenAICompatibleClient(
        base_url=args.base_url,
        api_key=api_key,
        model=args.model,
        timeout=args.timeout,
        temperature=args.temperature,
    )

    results: list[AnnotationResult] = []
    for index, source in enumerate(sources, start=1):
        record_path = record_dir / f"{source.slug}.json"
        if args.resume and record_path.exists():
            print(f"[{index}/{len(sources)}] skip existing {source.slug}")
            results.append(
                AnnotationResult(
                    slug=source.slug,
                    ok=True,
                    attempts=0,
                    record_path=str(record_path),
                )
            )
            continue

        print(f"[{index}/{len(sources)}] annotate {source.slug}")
        result = annotate_one(
            source=source,
            client=client,
            repo_root=repo_root,
            record_dir=record_dir,
            max_retries=args.max_retries,
            sleep_seconds=args.sleep_seconds,
        )
        if result.ok:
            print(f"  OK attempts={result.attempts}")
        else:
            print(f"  FAIL attempts={result.attempts}: {result.errors}")
        results.append(result)

    export_metadata(output_dir)
    write_manifest(
        output_dir=output_dir,
        source_count=len(sources),
        results=results,
        model=args.model,
        base_url=args.base_url,
        max_retries=args.max_retries,
    )

    ok_count = sum(1 for result in results if result.ok)
    print(f"Completed: {ok_count}/{len(results)} valid SSL records")


if __name__ == "__main__":
    main()
