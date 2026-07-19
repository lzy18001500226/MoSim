#!/usr/bin/env python3
"""Run the persistent MoSim Orchestrator request service."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.orchestration import CatalogRuntimeBackend, MoSimOrchestrator
from src.orchestration.service import (
    DEFAULT_REQUEST_DIR,
    DEFAULT_RESPONSE_DIR,
    OrchestratorService,
    exclusive_service_lock,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request-dir", type=Path, default=DEFAULT_REQUEST_DIR)
    parser.add_argument("--response-dir", type=Path, default=DEFAULT_RESPONSE_DIR)
    parser.add_argument("--poll-interval-s", type=float, default=0.25)
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()
    orchestrator = MoSimOrchestrator(backend=CatalogRuntimeBackend())
    service = OrchestratorService(orchestrator, args.request_dir, args.response_dir)
    lock_path = args.request_dir.parent / "orchestrator_service.lock"
    try:
        with exclusive_service_lock(lock_path):
            if args.once:
                print(service.process_once())
                return 0
            service.serve(poll_interval_s=args.poll_interval_s)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
