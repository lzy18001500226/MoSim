#!/usr/bin/env python3
"""Import the accepted Sunray rotor audio layers into MoSimSceneLibrary.

The runtime rotor-audio component loads these same-source layers:

    /Game/Audio/MoSim/SunrayRotorHoverLoop.SunrayRotorHoverLoop
    /Game/Audio/MoSim/SunrayRotorLoadLoop.SunrayRotorLoadLoop
    /Game/Audio/MoSim/SunrayRotorSpoolUp.SunrayRotorSpoolUp
    /Game/Audio/MoSim/SunrayRotorSpoolDown.SunrayRotorSpoolDown

This script derives non-hover layers from the reviewed hover WAV and writes a
small evidence JSON so the audio route is reproducible instead of an
editor-only click.
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import wave
from pathlib import Path
from typing import Any

from run_scene_truth_export import (
    ENGINE_ROOT_BY_VERSION,
    resolve_editor_cmd,
    tail_lines,
    to_windows_path,
)


ROOT = Path(__file__).resolve().parents[2]
RENDERER_UPROJECT = ROOT / "UE5/MoSimSceneLibrary/MoSimSceneLibrary.uproject"
DEFAULT_SOURCE_WAV = (
    ROOT
    / "UE5/MoSimSceneLibrary/SourceAssets/Audio/SunrayRotor/"
    / "sunray_rotor_hover_loop_854382_cc0_preview.wav"
)
DEFAULT_SOURCE_MANIFEST = (
    ROOT
    / "UE5/MoSimSceneLibrary/SourceAssets/Audio/SunrayRotor/"
    / "sunray_rotor_hover_loop_854382_cc0_preview_manifest.json"
)
DEFAULT_ASSET_PATH = "/Game/Audio/MoSim/SunrayRotorHoverLoop"
DEFAULT_DERIVED_DIR = ROOT / "UE5/MoSimSceneLibrary/SourceAssets/Audio/SunrayRotor/Derived"
DEFAULT_AUDIO_LAYERS = [
    {
        "layer_id": "hover_loop",
        "source_key": "hover",
        "asset_path": "/Game/Audio/MoSim/SunrayRotorHoverLoop",
        "looping": True,
        "runtime_role": "base hover loop",
    },
    {
        "layer_id": "load_loop",
        "source_key": "load",
        "asset_path": "/Game/Audio/MoSim/SunrayRotorLoadLoop",
        "looping": True,
        "runtime_role": "maneuver/load layer for forward/back/lateral motion",
    },
    {
        "layer_id": "spool_up",
        "source_key": "spool_up",
        "asset_path": "/Game/Audio/MoSim/SunrayRotorSpoolUp",
        "looping": False,
        "runtime_role": "takeoff motor spin-up one-shot",
    },
    {
        "layer_id": "spool_down",
        "source_key": "spool_down",
        "asset_path": "/Game/Audio/MoSim/SunrayRotorSpoolDown",
        "looping": False,
        "runtime_role": "landing motor spin-down one-shot",
    },
]


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def output_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def read_wav_mono(path: Path) -> tuple[int, list[float]]:
    with wave.open(str(path), "rb") as handle:
        channels = handle.getnchannels()
        sample_width = handle.getsampwidth()
        sample_rate = handle.getframerate()
        frames = handle.getnframes()
        payload = handle.readframes(frames)
    if sample_width != 2:
        raise RuntimeError(f"Expected 16-bit PCM WAV, got sample_width={sample_width}: {path}")
    if channels < 1:
        raise RuntimeError(f"Expected at least one channel in WAV: {path}")
    values: list[float] = []
    stride = channels * sample_width
    for offset in range(0, len(payload), stride):
        acc = 0
        for channel in range(channels):
            start = offset + channel * sample_width
            acc += int.from_bytes(payload[start : start + sample_width], byteorder="little", signed=True)
        values.append((acc / channels) / 32768.0)
    return sample_rate, values


def write_wav_mono(path: Path, sample_rate: int, samples: list[float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm = bytearray()
    for value in samples:
        clipped = max(-1.0, min(1.0, value))
        pcm.extend(int(round(clipped * 32767.0)).to_bytes(2, byteorder="little", signed=True))
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(bytes(pcm))


def wrapped_sample(samples: list[float], position: float) -> float:
    if not samples:
        return 0.0
    length = len(samples)
    position = position % length
    left = int(math.floor(position))
    right = (left + 1) % length
    alpha = position - left
    return samples[left] * (1.0 - alpha) + samples[right] * alpha


def soft_clip(value: float) -> float:
    return math.tanh(value * 1.15)


def derive_load_loop(source: list[float]) -> list[float]:
    output: list[float] = []
    previous = source[0] if source else 0.0
    for index in range(len(source)):
        base = wrapped_sample(source, index * 1.075)
        high = base - 0.985 * previous
        previous = base
        tremolo = 0.92 + 0.08 * math.sin(2.0 * math.pi * index / 2400.0)
        output.append(soft_clip((base * 0.58 + high * 1.65) * 0.82 * tremolo))
    return output


def derive_spool(source: list[float], sample_rate: int, *, seconds: float, start_rate: float, end_rate: float, fade_in: bool) -> list[float]:
    frame_count = max(1, int(sample_rate * seconds))
    output: list[float] = []
    position = 0.0
    for index in range(frame_count):
        alpha = index / max(1, frame_count - 1)
        smooth = alpha * alpha * (3.0 - 2.0 * alpha)
        rate = start_rate + (end_rate - start_rate) * smooth
        position += rate
        envelope = smooth if fade_in else 1.0 - smooth
        edge = min(1.0, index / max(1.0, sample_rate * 0.045), (frame_count - index - 1) / max(1.0, sample_rate * 0.045))
        output.append(soft_clip(wrapped_sample(source, position) * envelope * edge * 0.95))
    return output


def derive_audio_layers(source_wav: Path, source_manifest: Path, derived_dir: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    sample_rate, source_samples = read_wav_mono(source_wav)
    source_payload: dict[str, Any] = {}
    if source_manifest.exists():
        source_payload = json.loads(source_manifest.read_text(encoding="utf-8"))
    derived_paths = {
        "hover": source_wav,
        "load": derived_dir / "sunray_rotor_load_loop_854382_cc0_derived.wav",
        "spool_up": derived_dir / "sunray_rotor_spool_up_854382_cc0_derived.wav",
        "spool_down": derived_dir / "sunray_rotor_spool_down_854382_cc0_derived.wav",
    }
    write_wav_mono(derived_paths["load"], sample_rate, derive_load_loop(source_samples))
    write_wav_mono(
        derived_paths["spool_up"],
        sample_rate,
        derive_spool(source_samples, sample_rate, seconds=2.2, start_rate=0.54, end_rate=1.13, fade_in=True),
    )
    write_wav_mono(
        derived_paths["spool_down"],
        sample_rate,
        derive_spool(source_samples, sample_rate, seconds=2.6, start_rate=1.03, end_rate=0.38, fade_in=False),
    )
    layers: list[dict[str, Any]] = []
    for layer in DEFAULT_AUDIO_LAYERS:
        source_path = derived_paths[layer["source_key"]]
        layers.append({**layer, "source_wav": source_path})
    generation = {
        "schema": "mosim.sunray_rotor_audio_layer_generation.v1",
        "ok": True,
        "source_wav": str(source_wav),
        "source_manifest": str(source_manifest),
        "source_payload": source_payload,
        "sample_rate": sample_rate,
        "source_duration_seconds": len(source_samples) / sample_rate if sample_rate else None,
        "layers": [
            {
                "layer_id": layer["layer_id"],
                "source_wav": str(layer["source_wav"]),
                "asset_path": layer["asset_path"],
                "looping": layer["looping"],
                "runtime_role": layer["runtime_role"],
            }
            for layer in layers
        ],
        "derivation_policy": [
            "Only the reviewed 854382 CC0 hover source is used.",
            "LoadLoop is a same-source high-frequency/load-colored loop.",
            "SpoolUp and SpoolDown are same-source pitch/envelope one-shots.",
            "No fly-by or moving-camera recording is used.",
        ],
    }
    return layers, generation


def write_editor_import_script(
    script_path: Path,
    *,
    layers: list[dict[str, Any]],
    source_manifest: Path,
    generation_payload: dict[str, Any],
    evidence_path: Path,
) -> None:
    serialized_layers = [
        {
            **layer,
            "source_wav": to_windows_path(layer["source_wav"]),
        }
        for layer in layers
    ]
    source = f"""
import json
from pathlib import Path
import unreal

source_manifest = Path({to_windows_path(source_manifest)!r})
layers = {serialized_layers!r}
generation_payload = {generation_payload!r}
evidence_path = Path({to_windows_path(evidence_path)!r})

source_payload = {{}}
if source_manifest.exists():
    source_payload = json.loads(source_manifest.read_text(encoding="utf-8"))

editor_asset_library = unreal.EditorAssetLibrary
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
imported_layers = []

for layer in layers:
    source_wav = Path(layer["source_wav"])
    asset_path = layer["asset_path"]
    destination_path, asset_name = asset_path.rsplit("/", 1)
    object_path = asset_path + "." + asset_name
    if not source_wav.exists():
        raise RuntimeError("Sunray rotor source WAV missing: " + str(source_wav))
    if not editor_asset_library.does_directory_exist(destination_path):
        editor_asset_library.make_directory(destination_path)

    task = unreal.AssetImportTask()
    task.filename = str(source_wav)
    task.destination_path = destination_path
    task.destination_name = asset_name
    task.automated = True
    task.save = True
    task.replace_existing = True
    task.replace_existing_settings = True
    asset_tools.import_asset_tasks([task])

    imported_paths = [str(obj.get_path_name()) for obj in task.get_objects() if obj]
    asset = unreal.load_asset(object_path)
    exists = bool(asset)
    compression_result = {{
        "requested": "PCM",
        "ok": False,
        "method": "",
        "before": "",
        "after": "",
        "error": "",
    }}
    if exists:
        try:
            getter = getattr(asset, "get_sound_asset_compression_type", None)
            if callable(getter):
                compression_result["before"] = str(getter())
        except Exception as exc:
            compression_result["before"] = "unavailable: " + str(exc)
        try:
            enum_type = getattr(unreal, "SoundAssetCompressionType", None)
            pcm_value = getattr(enum_type, "PCM", None) if enum_type else None
            if pcm_value is not None:
                setter = getattr(asset, "set_sound_asset_compression_type", None)
                if callable(setter):
                    setter(pcm_value)
                    compression_result["method"] = "set_sound_asset_compression_type"
                else:
                    asset.set_editor_property("sound_asset_compression_type", pcm_value)
                    compression_result["method"] = "set_editor_property(sound_asset_compression_type)"
                getter = getattr(asset, "get_sound_asset_compression_type", None)
                compression_result["after"] = str(getter()) if callable(getter) else str(
                    asset.get_editor_property("sound_asset_compression_type")
                )
                compression_result["ok"] = "PCM" in compression_result["after"]
            else:
                compression_result["error"] = "unreal.SoundAssetCompressionType.PCM unavailable"
        except Exception as exc:
            compression_result["error"] = str(exc)
        if layer["looping"]:
            try:
                asset.set_editor_property("looping", True)
            except Exception:
                try:
                    asset.bLooping = True
                except Exception:
                    pass
        editor_asset_library.save_asset(object_path, only_if_is_dirty=False)

    duration_seconds = None
    sample_rate = None
    num_channels = None
    if exists:
        for attr_name, payload_key in (
            ("duration", "duration_seconds"),
            ("sample_rate", "sample_rate"),
            ("num_channels", "num_channels"),
        ):
            try:
                value = getattr(asset, attr_name)
                if attr_name == "duration":
                    duration_seconds = float(value)
                elif attr_name == "sample_rate":
                    sample_rate = int(value)
                elif attr_name == "num_channels":
                    num_channels = int(value)
            except Exception:
                pass

    asset_data = editor_asset_library.find_asset_data(object_path)
    imported_layers.append({{
        "layer_id": layer["layer_id"],
        "runtime_role": layer["runtime_role"],
        "looping": layer["looping"],
        "ok": exists,
        "source_wav": str(source_wav),
        "destination_path": destination_path,
        "asset_name": asset_name,
        "asset_path": asset_path,
        "object_path": object_path,
        "imported_paths": imported_paths,
        "asset_class": str(asset.get_class().get_name()) if exists else "",
        "asset_data_package_name": str(asset_data.package_name) if asset_data else "",
        "compression": compression_result,
        "duration_seconds": duration_seconds,
        "sample_rate": sample_rate,
        "num_channels": num_channels,
    }})

editor_asset_library.save_directory("/Game/Audio/MoSim", only_if_is_dirty=False, recursive=True)
payload = {{
    "schema": "mosim.sunray_rotor_audio_import.v2",
    "ok": all(layer["ok"] for layer in imported_layers),
    "source_manifest": str(source_manifest),
    "source_payload": source_payload,
    "generation": generation_payload,
    "layers": imported_layers,
    "claim_boundary": [
        "UE Content audio import/readiness only.",
        "Rotor sound layers are derived only from the reviewed hover source.",
        "Rotor sound is driven by MWORKS MotorCommand/pose/motion state in UE for review.",
        "Not MWORKS dynamics, controller, planner, closed-loop, or performance evidence."
    ],
}}
evidence_path.parent.mkdir(parents=True, exist_ok=True)
evidence_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
if not payload["ok"]:
    raise RuntimeError("Sunray rotor audio import failed: " + json.dumps(payload, ensure_ascii=False))
"""
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(source.strip() + "\n", encoding="utf-8")


def build_command(editor_cmd: Path, script_path: Path) -> list[str]:
    return [
        str(editor_cmd),
        to_windows_path(RENDERER_UPROJECT),
        "-run=pythonscript",
        f"-script={to_windows_path(script_path)}",
        "-nosplash",
        "-stdout",
        "-FullStdOutLogOutput",
        "-unattended",
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-wav", type=Path, default=DEFAULT_SOURCE_WAV)
    parser.add_argument("--source-manifest", type=Path, default=DEFAULT_SOURCE_MANIFEST)
    parser.add_argument("--asset-path", default=DEFAULT_ASSET_PATH, help="Legacy single-layer path; v2 imports the full layer set.")
    parser.add_argument("--derived-dir", type=Path, default=DEFAULT_DERIVED_DIR)
    parser.add_argument("--engine-version", default="5.5")
    parser.add_argument("--engine-root", type=Path, default=None)
    parser.add_argument("--editor-cmd", type=Path, default=None)
    parser.add_argument(
        "--script-path",
        type=Path,
        default=ROOT / "Results/tmp/import_sunray_rotor_hover_audio_editor.py",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=ROOT / "Results/tmp/import_sunray_rotor_hover_audio_latest.json",
    )
    parser.add_argument("--log-output", type=Path, default=None)
    parser.add_argument("--timeout-seconds", type=float, default=None)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_wav = args.source_wav if args.source_wav.is_absolute() else ROOT / args.source_wav
    source_manifest = args.source_manifest if args.source_manifest.is_absolute() else ROOT / args.source_manifest
    derived_dir = args.derived_dir if args.derived_dir.is_absolute() else ROOT / args.derived_dir
    script_path = args.script_path if args.script_path.is_absolute() else ROOT / args.script_path
    evidence_path = args.json_output if args.json_output.is_absolute() else ROOT / args.json_output
    engine_root = args.engine_root or ENGINE_ROOT_BY_VERSION.get(args.engine_version)
    editor_cmd = resolve_editor_cmd(RENDERER_UPROJECT, engine_root, args.editor_cmd)
    layers, generation_payload = derive_audio_layers(source_wav, source_manifest, derived_dir)
    write_editor_import_script(
        script_path,
        layers=layers,
        source_manifest=source_manifest,
        generation_payload=generation_payload,
        evidence_path=evidence_path,
    )
    command = build_command(editor_cmd, script_path)
    payload: dict[str, Any] = {
        "renderer_uproject": rel(RENDERER_UPROJECT),
        "source_wav": rel(source_wav),
        "source_manifest": rel(source_manifest),
        "derived_dir": rel(derived_dir),
        "layers": [
            {
                **layer,
                "source_wav": rel(layer["source_wav"]),
            }
            for layer in layers
        ],
        "editor_cmd": to_windows_path(editor_cmd),
        "script_path": rel(script_path),
        "json_output": rel(evidence_path),
        "command": command,
        "dry_run": args.dry_run,
    }
    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    try:
        completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=args.timeout_seconds)
    except subprocess.TimeoutExpired as exc:
        if args.log_output:
            log_path = args.log_output if args.log_output.is_absolute() else ROOT / args.log_output
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_text(output_text(exc.stdout) + output_text(exc.stderr), encoding="utf-8", errors="replace")
            payload["log_output"] = rel(log_path)
            payload["tail"] = tail_lines(log_path, 80)
        payload.update({"ok": False, "reason": "timeout", "timeout_seconds": args.timeout_seconds})
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return 124
    if args.log_output:
        log_path = args.log_output if args.log_output.is_absolute() else ROOT / args.log_output
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text((completed.stdout or "") + (completed.stderr or ""), encoding="utf-8", errors="replace")
        payload["log_output"] = rel(log_path)
        payload["tail"] = tail_lines(log_path, 80)
    if evidence_path.exists():
        payload["import_evidence"] = json.loads(evidence_path.read_text(encoding="utf-8"))
    import_evidence = payload.get("import_evidence", {})
    log_text = ""
    if args.log_output:
        log_path = args.log_output if args.log_output.is_absolute() else ROOT / args.log_output
        if log_path.exists():
            log_text = log_path.read_text(encoding="utf-8", errors="replace")
    else:
        log_text = (completed.stdout or "") + (completed.stderr or "")
    payload["editor_clean_exit"] = completed.returncode == 0
    payload["nonfatal_audio_decoder_ensure"] = (
        completed.returncode != 0
        and bool(import_evidence.get("ok"))
        and "Decoder for AudioFormat 'BINKA' not found" in log_text
        and "SunrayRotor" in log_text
    )
    payload["ok"] = bool(import_evidence.get("ok")) and (
        completed.returncode == 0 or payload["nonfatal_audio_decoder_ensure"]
    )
    payload["returncode"] = completed.returncode
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["ok"] else completed.returncode or 1


if __name__ == "__main__":
    raise SystemExit(main())
