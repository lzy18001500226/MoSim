#!/usr/bin/env python3
"""Keep formation optimization enabled during Swarm-Formation collision replans."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


OLD_CALL = "planFromLocalTraj(true, false)"
NEW_CALL = "planFromLocalTraj(true, true)"
RIGID_LEADER_FOLLOWER_CALL = "planFromLocalTraj(true, !rigid_leader_follower_mode_)"


def patch_source(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    replacements = text.count(OLD_CALL)
    patched = text.replace(OLD_CALL, NEW_CALL)
    peer_trajectory_calls = patched.count(NEW_CALL)
    rigid_leader_follower_calls = patched.count(RIGID_LEADER_FOLLOWER_CALL)
    formation_contract_calls = peer_trajectory_calls + rigid_leader_follower_calls

    if OLD_CALL in patched:
        raise RuntimeError(f"formation-disabling collision replan remains in {path}")
    if peer_trajectory_calls < 1 or formation_contract_calls < 2:
        raise RuntimeError(
            f"expected one peer-trajectory replan plus two formation-contract collision replans in {path}, "
            f"found peer={peer_trajectory_calls}, rigid={rigid_leader_follower_calls}"
        )

    if patched != text:
        path.write_text(patched, encoding="utf-8")

    return {
        "status": "patched" if replacements else "already_patched",
        "source": str(path),
        "replacements": replacements,
        # Keep the historical field for prior result readers; the count now
        # includes the conditional rigid leader-follower replan when present.
        "formation_preserving_calls": formation_contract_calls,
        "peer_trajectory_preserving_calls": peer_trajectory_calls,
        "rigid_leader_follower_collision_replans": rigid_leader_follower_calls,
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
