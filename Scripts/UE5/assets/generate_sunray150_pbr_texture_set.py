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


PROJECT_ROOT = Path(r"C:\Users\HP\Desktop\MoSim")
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
    weave_a = 0.5 + 0.5 * np.sin((x + y) * math.tau * 32.0)
    weave_b = 0.5 + 0.5 * np.sin((x - y) * math.tau * 32.0)
    checker = ((np.floor((x + y) * 18) + np.floor((x - y) * 18)) % 2)
    noise = random_field(11)
    pattern = 0.42 * weave_a + 0.36 * weave_b + 0.22 * noise
    pattern = np.where(checker > 0, pattern * 0.75, pattern * 1.15)
    base = np.dstack([16 + pattern * 28, 17 + pattern * 30, 17 + pattern * 30])
    rough = 95 + (1 - pattern) * 75
    bump = 118 + (pattern - 0.5) * 80
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
        "gold_aluminum": brushed_metal("sunray150_gold_anodized_aluminum", (172, 111, 30), 22),
        "mid360_silver": brushed_metal("mid360_silver_grey_aluminum", (128, 126, 118), 23),
        "black_rubber": rubber("sunray150_black_rubber", (5, 5, 5), 31),
        "smoked_guard": rubber("sunray150_smoked_translucent_guard", (54, 59, 60), 32),
        "pcb_black": pcb(),
    }
    manifest_path = OUT_DIR / "sunray150_texture_manifest.json"
    manifest_path.write_text(__import__("json").dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(str(manifest_path))


if __name__ == "__main__":
    main()
