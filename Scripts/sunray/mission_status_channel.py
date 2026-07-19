#!/usr/bin/env python3
"""Run-scoped live mission status shared by ROS1 mission adapters and QGC."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MISSION_STATUS_SCHEMA = "mosim.mission_status.v1"


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


class MissionStatusChannel:
    """Publish adapter phase and per-vehicle acknowledgements without controlling flight."""

    def __init__(
        self,
        adapter_id: str,
        vehicle_ids: list[str],
        *,
        run_id: str | None = None,
        output_path: Path | None = None,
        minimum_write_interval_s: float = 0.25,
    ) -> None:
        self.run_id = str(run_id or os.environ.get("RUN_ID", "")).strip()
        self.adapter_id = str(adapter_id)
        self.output_path = output_path or (
            PROJECT_ROOT
            / "Results"
            / "ui_platform"
            / "orchestrator_runs"
            / self.run_id
            / "mission_status.json"
        )
        self.enabled = bool(self.run_id)
        self.minimum_write_interval_s = max(0.0, float(minimum_write_interval_s))
        self.last_write_at = 0.0
        self.last_error = ""
        self.phase = "init"
        self.state = "running"
        self.terminal = False
        self.accepted: bool | None = None
        self.reason_code = "mission_adapter_started"
        self.blockers: list[str] = []
        self.vehicles = {
            vehicle_id: {
                "vehicle_id": vehicle_id,
                "connected": False,
                "armed": False,
                "mode": "",
                "updated_at": 0.0,
            }
            for vehicle_id in vehicle_ids
        }
        self._write(force=True)

    def _payload(self, now: float) -> dict[str, Any]:
        return {
            "schema": MISSION_STATUS_SCHEMA,
            "run_id": self.run_id,
            "adapter_id": self.adapter_id,
            "phase": self.phase,
            "state": self.state,
            "terminal": self.terminal,
            "accepted": self.accepted,
            "reason_code": self.reason_code,
            "blockers": self.blockers,
            "vehicles": list(self.vehicles.values()),
            "updated_at": now,
        }

    def _write(self, *, force: bool = False) -> None:
        if not self.enabled:
            return
        now = time.time()
        if not force and now - self.last_write_at < self.minimum_write_interval_s:
            return
        self.last_write_at = now
        try:
            _write_json(self.output_path, self._payload(now))
            self.last_error = ""
        except OSError as exc:
            # Operator observability must never interrupt the flight-control path.
            self.last_error = str(exc)

    def update_phase(self, phase: str) -> None:
        self.phase = str(phase)
        self.reason_code = f"mission_phase_{self.phase}"
        self._write(force=True)

    def update_vehicle(self, vehicle_id: str, *, connected: bool, armed: bool, mode: str) -> None:
        if vehicle_id not in self.vehicles:
            return
        self.vehicles[vehicle_id] = {
            "vehicle_id": vehicle_id,
            "connected": bool(connected),
            "armed": bool(armed),
            "mode": str(mode),
            "updated_at": time.time(),
        }
        self._write()

    def finish(self, *, result_status: str, accepted: bool, blockers: list[str] | None = None) -> None:
        self.state = str(result_status)
        self.terminal = True
        self.accepted = bool(accepted)
        self.reason_code = f"mission_result_{result_status}"
        self.blockers = list(blockers or [])
        self._write(force=True)
