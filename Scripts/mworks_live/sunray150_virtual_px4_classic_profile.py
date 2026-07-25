"""Read the locked virtual Sunray150 controller defaults from the project profile."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROFILE_PATH = ROOT / "Config" / "plant" / "sunray150_virtual_px4_classic_profile.json"


def load_rt1_controller_defaults() -> tuple[float, float, float]:
    """Return mass, gravity, and hover percentage for the RT1 thrust map."""
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    return (
        float(profile["mass_accounting"]["px4ctrl_runtime_mass_kg"]),
        float(profile["gravity_mps2"]),
        float(profile["controller_calibration"]["mworks_controller_hover_percentage"]),
    )
