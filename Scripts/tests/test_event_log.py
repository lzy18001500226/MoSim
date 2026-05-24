#!/usr/bin/env python3
"""Regression checks for controller event-log generation."""

from __future__ import annotations

import csv
import importlib.util
from pathlib import Path
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[2]


def load_event_module():
    path = ROOT / "Scripts" / "Results" / "generate_event_log.py"
    spec = importlib.util.spec_from_file_location("generate_event_log", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load generate_event_log.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_event_log_records_mode_changes() -> None:
    module = load_event_module()
    temp_dir = ROOT / ".tmp" / f"event_log_{uuid4().hex}"
    raw = temp_dir / "raw.csv"
    try:
        temp_dir.mkdir(parents=True)
        with raw.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(["time", "controller_mode", "event_code", "safety_active"])
            writer.writerow([0.0, 1, 10, 0])
            writer.writerow([1.0, 1, 10, 0])
            writer.writerow([2.0, 2, 20, 1])
            writer.writerow([3.0, 3, 30, 1])
            writer.writerow([4.0, 4, 40, 1])
        payload = module.build_event_log(module.read_rows(raw), scene_id="fixture", controller_id="nmpc_indi_l1")
    finally:
        if raw.exists():
            raw.unlink()
        if temp_dir.exists():
            temp_dir.rmdir()
        tmp_root = ROOT / ".tmp"
        if tmp_root.exists() and not any(tmp_root.iterdir()):
            tmp_root.rmdir()

    events = payload["events"]
    names = [item["event"] for item in events]
    if names != ["NORMAL", "SAFETY_FILTER_ACTIVE", "DEGRADED_RETURN", "EMERGENCY_LAND"]:
        raise AssertionError(payload)
    if payload["event_count"] != 4:
        raise AssertionError(payload)


def test_event_log_maps_system_mode_6_to_degraded_nav() -> None:
    module = load_event_module()
    temp_dir = ROOT / ".tmp" / f"event_log_system_{uuid4().hex}"
    raw = temp_dir / "raw.csv"
    try:
        temp_dir.mkdir(parents=True)
        with raw.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(["time", "flight_mode", "event_code", "safety_status"])
            writer.writerow([0.0, 3, 30, 0])
            writer.writerow([0.35, 6, 30, 3])
            writer.writerow([0.86, 3, 30, 0])
        payload = module.build_event_log(module.read_rows(raw), scene_id="system_gps_dropout", controller_id="awff")
    finally:
        if raw.exists():
            raw.unlink()
        if temp_dir.exists():
            temp_dir.rmdir()
        tmp_root = ROOT / ".tmp"
        if tmp_root.exists() and not any(tmp_root.iterdir()):
            tmp_root.rmdir()

    names = [item["event"] for item in payload["events"]]
    if names != ["DEGRADED_RETURN", "DEGRADED_NAV", "DEGRADED_RETURN"]:
        raise AssertionError(payload)
