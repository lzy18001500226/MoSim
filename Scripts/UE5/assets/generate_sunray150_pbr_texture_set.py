#!/usr/bin/env python3
"""Generate project-local procedural texture maps for Sunray150 materials.

The maps are deterministic placeholders for the Blender audit pipeline. They
replace flat color-only materials with inspectable texture channels that can be
retouched later in ArmorPaint or Material Maker.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


PROJECT_ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = PROJECT_ROOT / "UE5" / "MoSimSceneLibrary" / "SourceAssets" / "Sunray150" / "Textures"
SIZE = 1024


def save_rgb(name: str, arr: np.ndarray) -> str:
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / name
    Image.fromarray(arr, "RGB").save(path)
    return str(path)


def save_gray(name: str, arr: np.ndarray) -> str:
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / name
    Image.fromarray(arr, "L").save(path)
    return str(path)


def normalized_grid(size: int = SIZE) -> tuple[np.ndarray, np.ndarray]:
    y, x = np.mgrid[0:size, 0:size]
    return x / size, y / size


def random_field(seed: int, size: int = SIZE) -> np.ndarray:
    rng = np.random.default_rng(seed)
    base = rng.normal(0, 1, (size, size))
    # Cheap low-pass texture by repeated neighbor averaging.
    for _ in range(6):
        base = (
            base
            + np.roll(base, 1, 0)
            + np.roll(base, -1, 0)
            + np.roll(base, 1, 1)
            + np.roll(base, -1, 1)
        ) / 5.0
    base -= base.min()
    base /= max(base.max(), 1e-9)
    return base


def carbon_fiber() -> dict[str, str]:
    x, y = normalized_grid()
    weave_a = 0.5 + 0.5 * np.sin((x + y) * math.tau * 52.0)
    weave_b = 0.5 + 0.5 * np.sin((x - y) * math.tau * 52.0)
    checker = ((np.floor((x + y) * 30) + np.floor((x - y) * 30)) % 2)
    noise = random_field(11)
    pattern = 0.46 * weave_a + 0.40 * weave_b + 0.14 * noise
    pattern = np.where(checker > 0, pattern * 0.58, pattern * 1.32)
    sheen = np.clip(pattern ** 1.35, 0.0, 1.0)
    base = np.dstack([4 + sheen * 44, 5 + sheen * 45, 5 + sheen * 43])
    rough = 86 + (1 - sheen) * 122
    bump = 112 + (pattern - 0.5) * 150
    return {
        "base_color": save_rgb("sunray150_carbon_fiber_base.png", base),
        "roughness": save_gray("sunray150_carbon_fiber_roughness.png", rough),
        "bump": save_gray("sunray150_carbon_fiber_bump.png", bump),
    }


def brushed_metal(prefix: str, base_rgb: tuple[int, int, int], seed: int) -> dict[str, str]:
    x, y = normalized_grid()
    noise = random_field(seed)
    scratches = 0.5 + 0.5 * np.sin(x * math.tau * 210 + noise * 5.0)
    fine = random_field(seed + 100)
    pattern = 0.58 * scratches + 0.42 * fine
    base = np.dstack([base_rgb[i] + (pattern - 0.5) * 42 for i in range(3)])
    rough = 65 + (1 - pattern) * 105
    bump = 125 + (pattern - 0.5) * 42
    return {
        "base_color": save_rgb(f"{prefix}_base.png", base),
        "roughness": save_gray(f"{prefix}_roughness.png", rough),
        "bump": save_gray(f"{prefix}_bump.png", bump),
    }


def mid360_housing() -> dict[str, str]:
    x, y = normalized_grid()
    noise = random_field(24)
    side_shadow = np.clip((x - 0.58) * 3.0, 0.0, 1.0)
    edge_sheen = np.clip((0.22 - np.abs(y - 0.30)) * 3.0, 0.0, 1.0)
    soft = 0.55 + 0.45 * noise
    base = np.dstack(
        [
            70 + soft * 24 - side_shadow * 18 + edge_sheen * 18,
            72 + soft * 24 - side_shadow * 18 + edge_sheen * 18,
            70 + soft * 22 - side_shadow * 16 + edge_sheen * 16,
        ]
    )
    rough = 92 + (1.0 - soft) * 54 - edge_sheen * 20
    bump = 126 + (noise - 0.5) * 22
    return {
        "base_color": save_rgb("mid360_silver_grey_aluminum_base.png", base),
        "roughness": save_gray("mid360_silver_grey_aluminum_roughness.png", rough),
        "bump": save_gray("mid360_silver_grey_aluminum_bump.png", bump),
    }


def rubber(prefix: str, base_rgb: tuple[int, int, int], seed: int) -> dict[str, str]:
    noise = random_field(seed)
    pores = random_field(seed + 1)
    pattern = 0.65 * noise + 0.35 * pores
    base = np.dstack([base_rgb[i] + pattern * 18 for i in range(3)])
    rough = 185 + pattern * 55
    bump = 120 + (pattern - 0.5) * 38
    return {
        "base_color": save_rgb(f"{prefix}_base.png", base),
        "roughness": save_gray(f"{prefix}_roughness.png", rough),
        "bump": save_gray(f"{prefix}_bump.png", bump),
    }


def propeller_composite() -> dict[str, str]:
    x, y = normalized_grid()
    noise = random_field(61)
    span = np.abs(x - 0.5)
    chord = np.abs(y - 0.5)
    fiber = 0.5 + 0.5 * np.sin((x * 2.8 + y * 0.35 + noise * 0.08) * math.tau * 42.0)
    smoky = 0.55 * noise + 0.25 * fiber + 0.20 * (1.0 - span)
    # Smoked propeller plastic: dark in mass, with soft translucent streaks,
    # not white paint blocks.
    base = np.dstack([8 + smoky * 26, 9 + smoky * 26, 9 + smoky * 25])
    highlight = np.clip(1.0 - chord * 5.0, 0.0, 1.0) * np.clip(span * 2.0, 0.0, 1.0)
    base += highlight[:, :, None] * np.array([9, 9, 8])
    rough = 128 + (1.0 - smoky) * 74
    bump = 124 + (fiber - 0.5) * 34 + (noise - 0.5) * 18
    return {
        "base_color": save_rgb("sunray150_smoked_propeller_base.png", base),
        "roughness": save_gray("sunray150_smoked_propeller_roughness.png", rough),
        "bump": save_gray("sunray150_smoked_propeller_bump.png", bump),
    }


def camera_polymer() -> dict[str, str]:
    noise = random_field(71)
    pores = random_field(72)
    edge_wear = np.maximum(0.0, pores - 0.74) * 24.0
    base = np.dstack([5 + noise * 10 + edge_wear, 5 + noise * 10 + edge_wear, 5 + noise * 10 + edge_wear])
    rough = 185 + pores * 48
    bump = 120 + (noise - 0.5) * 30
    return {
        "base_color": save_rgb("sunray150_camera_black_polymer_base.png", base),
        "roughness": save_gray("sunray150_camera_black_polymer_roughness.png", rough),
        "bump": save_gray("sunray150_camera_black_polymer_bump.png", bump),
    }


def mid360_window() -> dict[str, str]:
    x, y = normalized_grid()
    radial = np.sqrt((x - 0.5) ** 2 + (y - 0.42) ** 2)
    sweep = 0.5 + 0.5 * np.sin((x * 1.6 + y * 0.9) * math.tau)
    blue = np.clip(1.0 - radial * 1.8, 0.0, 1.0)
    reflection = np.exp(-(((x - 0.24) / 0.052) ** 2 + ((y - 0.17) / 0.034) ** 2))
    teal_core = np.exp(-(((x - 0.44) / 0.20) ** 2 + ((y - 0.40) / 0.28) ** 2))
    edge_dark = np.clip(radial * 2.4, 0.0, 1.0)
    # Real MID-360 window is a dark blue/teal glossy optical dome, not a pale
    # cyan cap. Keep highlights strong but avoid washing the whole dome white.
    base = np.dstack(
        [
            1 + blue * 2 + reflection * 5,
            18 + blue * 40 + teal_core * 54 + sweep * 4 + reflection * 12 - edge_dark * 8,
            38 + blue * 74 + teal_core * 36 + sweep * 5 + reflection * 18 - edge_dark * 16,
        ]
    )
    rough = 28 + (1.0 - blue) * 36
    bump = 128 + (sweep - 0.5) * 10
    return {
        "base_color": save_rgb("mid360_blue_optical_window_base.png", base),
        "roughness": save_gray("mid360_blue_optical_window_roughness.png", rough),
        "bump": save_gray("mid360_blue_optical_window_bump.png", bump),
    }


def battery_heatshrink() -> dict[str, str]:
    x, y = normalized_grid()
    noise = random_field(81)
    vertical_wrinkle = 0.5 + 0.5 * np.sin(x * math.tau * 18.0 + noise * 0.55)
    label_band = (x > 0.42) & (x < 0.58)
    base = np.dstack([5 + noise * 12, 5 + noise * 12, 5 + noise * 12])
    base[label_band] += np.array([10, 10, 10])
    rough = 175 + vertical_wrinkle * 52
    bump = 118 + (vertical_wrinkle - 0.5) * 46 + (noise - 0.5) * 18
    return {
        "base_color": save_rgb("sunray150_battery_heatshrink_base.png", base),
        "roughness": save_gray("sunray150_battery_heatshrink_roughness.png", rough),
        "bump": save_gray("sunray150_battery_heatshrink_bump.png", bump),
    }


def pcb() -> dict[str, str]:
    base = np.zeros((SIZE, SIZE, 3), dtype=np.float32)
    base[:, :, :] = (7, 13, 9)
    img = Image.fromarray(base.astype(np.uint8), "RGB")
    draw = ImageDraw.Draw(img)
    rng = np.random.default_rng(45)
    for _ in range(120):
        x0, y0 = rng.integers(0, SIZE, 2)
        x1 = int(np.clip(x0 + rng.integers(-120, 120), 0, SIZE - 1))
        y1 = int(np.clip(y0 + rng.integers(-120, 120), 0, SIZE - 1))
        draw.line((int(x0), int(y0), x1, y1), fill=(90, 78, 45), width=int(rng.integers(1, 4)))
    for _ in range(80):
        x0, y0 = rng.integers(0, SIZE - 30, 2)
        w, h = rng.integers(8, 45), rng.integers(5, 32)
        fill = tuple(map(int, rng.choice([(18, 18, 18), (35, 35, 32), (115, 115, 105)], 1)[0]))
        draw.rectangle((int(x0), int(y0), int(x0 + w), int(y0 + h)), fill=fill)
    return {
        "base_color": save_rgb("sunray150_pcb_black_base.png", np.asarray(img)),
        "roughness": save_gray("sunray150_pcb_black_roughness.png", np.full((SIZE, SIZE), 130)),
        "bump": save_gray("sunray150_pcb_black_bump.png", 120 + random_field(46) * 45),
    }


def main() -> None:
    manifest = {
        "carbon_fiber": carbon_fiber(),
        "dark_metal": brushed_metal("sunray150_dark_anodized_metal", (28, 29, 28), 21),
        "gold_aluminum": brushed_metal("sunray150_gold_anodized_aluminum", (138, 91, 28), 22),
        "mid360_silver": mid360_housing(),
        "black_rubber": rubber("sunray150_black_rubber", (5, 5, 5), 31),
        "smoked_guard": rubber("sunray150_smoked_translucent_guard", (54, 59, 60), 32),
        "smoked_propeller": propeller_composite(),
        "camera_polymer": camera_polymer(),
        "mid360_window": mid360_window(),
        "battery_heatshrink": battery_heatshrink(),
        "pcb_black": pcb(),
    }
    manifest_path = OUT_DIR / "sunray150_texture_manifest.json"
    manifest_path.write_text(__import__("json").dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(str(manifest_path))


if __name__ == "__main__":
    main()
