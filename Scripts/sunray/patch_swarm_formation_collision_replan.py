#!/usr/bin/env python3
"""Keep formation optimization enabled during Swarm-Formation collision replans."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


OLD_CALL = "planFromLocalTraj(true, false)"
NEW_CALL = "planFromLocalTraj(true, true)"


def patch_source(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    replacements = text.count(OLD_CALL)
    patched = text.replace(OLD_CALL, NEW_CALL)
    preserved_calls = patched.count(NEW_CALL)

    if OLD_CALL in patched:
        raise RuntimeError(f"formation-disabling collision replan remains in {path}")
    if preserved_calls < 2:
        raise RuntimeError(
            f"expected at least two formation-preserving collision replans in {path}, "
            f"found {preserved_calls}"
        )

    if patched != text:
        path.write_text(patched, encoding="utf-8")

    return {
        "status": "patched" if replacements else "already_patched",
        "source": str(path),
        "replacements": replacements,
        "formation_preserving_calls": preserved_calls,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    args = parser.parse_args()

    source = args.source.resolve()
    if not source.is_file():
        raise SystemExit(f"source missing: {source}")
    print(json.dumps(patch_source(source), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
