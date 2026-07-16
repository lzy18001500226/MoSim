"""Project-local file queue service for the two native GUI clients."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .core import ORCHESTRATOR_COMMANDS, PROJECT_ROOT, MoSimOrchestrator, _write_json


DEFAULT_REQUEST_DIR = PROJECT_ROOT / "Results" / "ui_platform" / "orchestrator_requests"
DEFAULT_RESPONSE_DIR = PROJECT_ROOT / "Results" / "ui_platform" / "orchestrator_responses"
MAX_REQUEST_BYTES = 64 * 1024


@dataclass
class OrchestratorService:
    orchestrator: MoSimOrchestrator
    request_dir: Path = DEFAULT_REQUEST_DIR
    response_dir: Path = DEFAULT_RESPONSE_DIR
    processed: set[str] = field(default_factory=set)

    def _response_path(self, request_path: Path) -> Path:
        return self.response_dir / f"{request_path.stem}.response.json"

    def process_request(self, request_path: Path) -> dict[str, Any]:
        request_id = request_path.stem
        if request_path.is_symlink() or request_path.stat().st_size > MAX_REQUEST_BYTES:
            return self.orchestrator._response(request_id, False, "request_file_rejected")
        try:
            request = json.loads(request_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            return self.orchestrator._response(request_id, False, "request_invalid_json", detail=str(exc))
        if not isinstance(request, dict):
            return self.orchestrator._response(request_id, False, "request_must_be_object")
        action = request.get("action") or request.get("command")
        request_id = str(request.get("request_id") or request_id)
        if action not in ORCHESTRATOR_COMMANDS:
            return self.orchestrator._response(request_id, False, "unsupported_action")
        arguments = dict(request)
        arguments.pop("action", None)
        arguments.pop("command", None)
        arguments.pop("schema", None)
        arguments["request_id"] = request_id
        try:
            return getattr(self.orchestrator, action)(**arguments)
        except TypeError as exc:
            return self.orchestrator._response(request_id, False, "request_arguments_invalid", detail=str(exc))

    def process_once(self) -> int:
        self.request_dir.mkdir(parents=True, exist_ok=True)
        self.response_dir.mkdir(parents=True, exist_ok=True)
        count = 0
        for request_path in sorted(self.request_dir.glob("*.json")):
            key = request_path.name
            response_path = self._response_path(request_path)
            if key in self.processed or response_path.exists():
                continue
            response = self.process_request(request_path)
            _write_json(response_path, response)
            self.processed.add(key)
            count += 1
        return count

    def serve(self, *, poll_interval_s: float = 0.25, stop_file: Path | None = None) -> None:
        if poll_interval_s < 0.05 or poll_interval_s > 5.0:
            raise ValueError("poll_interval_s must be between 0.05 and 5.0")
        stop_file = stop_file or self.request_dir / "STOP"
        while not stop_file.exists():
            self.process_once()
            time.sleep(poll_interval_s)
