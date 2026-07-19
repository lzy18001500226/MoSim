#!/usr/bin/env python3
"""File-backed safe-stop request/ACK channel shared by ROS1 mission adapters."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SAFE_STOP_SCHEMA = "mosim.safe_stop.request.v1"
SAFE_STOP_ACK_SCHEMA = "mosim.safe_stop.ack.v1"


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")
    temporary.replace(path)


class SafeStopChannel:
    """Poll one run-scoped request and publish monotonic mission-side ACKs."""

    def __init__(self, run_id: str | None = None) -> None:
        self.run_id = str(run_id or os.environ.get("RUN_ID", "")).strip()
        self.root = (
            PROJECT_ROOT / "Results" / "ui_platform" / "orchestrator_runs" / self.run_id / "safe_stop"
            if self.run_id
            else None
        )
        self.request: dict[str, Any] | None = None

    @property
    def enabled(self) -> bool:
        return self.root is not None

    def requested(self) -> bool:
        if self.root is None:
            return False
        path = self.root / "request.json"
        if not path.is_file():
            return False
        try:
            request = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError, TypeError):
            return False
        if (
            not isinstance(request, dict)
            or request.get("schema") != SAFE_STOP_SCHEMA
            or request.get("run_id") != self.run_id
            or not request.get("request_id")
            or not request.get("operation_id")
        ):
            return False
        self.request = request
        return True

    def acknowledge(
        self,
        stage: str,
        progress_percent: int,
        *,
        terminal: bool = False,
        accepted: bool = True,
        reason_code: str | None = None,
        detail: dict[str, Any] | None = None,
    ) -> None:
        if self.root is None or self.request is None:
            return
        payload = {
            "schema": SAFE_STOP_ACK_SCHEMA,
            "run_id": self.run_id,
            "request_id": self.request["request_id"],
            "operation_id": self.request["operation_id"],
            "stage": stage,
            "progress_percent": max(0, min(100, int(progress_percent))),
            "terminal": bool(terminal),
            "accepted": bool(accepted),
            "reason_code": reason_code or f"safe_stop_{stage}",
            "updated_at": time.time(),
        }
        if detail:
            payload["detail"] = detail
        _write_json(self.root / "ack.json", payload)
