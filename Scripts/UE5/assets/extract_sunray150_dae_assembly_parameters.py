#!/usr/bin/env python3
"""Extract accepted Sunray150 DAE assembly geometry parameters.

The accepted DAE/Blender assembly is the source for geometry only:
rotor centers, sensor/camera extrinsics, and conservative collision envelope.
Motor/thrust, mass, inertia, controller, and timing parameters are intentionally
left outside this extractor.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
AUDIT_DIR = PROJECT_ROOT / "UE5" / "MoSimSceneLibrary" / "SourceAssets" / "Sunray150" / "Audit"
RESULT_DIR = PROJECT_ROOT / "Results" / "unreal_scene_mapping"

FULL_ASSEMBLY_MANIFEST = AUDIT_DIR / "sunray150_dae_mid360_full_assembly_audit_manifest.json"
FRONT_MODULE_OBJECTS = RESULT_DIR / "sunray150_front_module_objects_20260603.json"
OUT_JSON = RESULT_DIR / "sunray150_dae_assembly_parameters_20260604.json"
OUT_MD = RESULT_DIR / "SUNRAY150_DAE_ASSEMBLY_PARAMETERS_20260604.md"


CURRENT_SDF = {
    "rotors_m": {
        "rotor_0_front_right": [0.065, -0.065, -0.025],
        "rotor_1_back_left": [-0.065, 0.065, -0.025],
        "rotor_2_front_left": [0.065, 0.065, -0.025],
        "rotor_3_back_right": [-0.065, -0.065, -0.025],
    },
    "camera_front_pose_xyz_rpy": [0.12, 0.0, 0.025, 0.0, 0.0, 0.0],
    "camera_down_pose_xyz_rpy": [-0.01, 0.0, -0.02, 0.0, 1.5707963, 3.14],
    "mid360_pose_xyz_rpy": [0.036, -0.0155, 0.075, 0.0, 0.0, 0.0],
    "base_collision_pose_xyz_rpy": [0.0, 0.0, -0.012, 0.0, 0.0, 0.0],
    "base_collision_size_xyz": [0.2, 0.15, 0.06],
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def round_vec(values: list[float], ndigits: int = 6) -> list[float]:
    return [round(float(v), ndigits) for v in values]


def vec_delta(new: list[float], old: list[float]) -> list[float]:
    return round_vec([new[i] - old[i] for i in range(len(new))])


def bbox_center_size(bounds_min: list[float], bounds_max: list[float]) -> tuple[list[float], list[float]]:
    center = [(bounds_min[i] + bounds_max[i]) / 2.0 for i in range(3)]
    size = [bounds_max[i] - bounds_min[i] for i in range(3)]
    return round_vec(center), round_vec(size)


def find_front_camera_body(front_objects: list[dict]) -> dict | None:
    for item in front_objects:
        name = item.get("name", "")
        if "FRONT_CAMERA_PartBody" in name:
            return item
    return None


def build_parameters() -> dict:
    full = load_json(FULL_ASSEMBLY_MANIFEST)
    front_objects = load_json(FRONT_MODULE_OBJECTS)

    rotors = {}
    for item in full["propellers"]["created"]:
        rotor_name = item["rotor"]
        center = round_vec(item["fit"]["translation_m"])
        rotors[rotor_name] = {
            "center_m": center,
            "previous_sdf_center_m": CURRENT_SDF["rotors_m"][rotor_name],
            "delta_from_previous_sdf_m": vec_delta(center, CURRENT_SDF["rotors_m"][rotor_name]),
            "confidence": "high",
            "source": "user-reviewed DAE screw-pair fit; propeller contact-plane Z accepted manually",
        }

    mid = full["mid360"]
    mid_bbox = mid["bbox_after"]
    mid_bbox_center, mid_bbox_size = bbox_center_size(mid_bbox["min"], mid_bbox["max"])
    mid_mount_center = round_vec(full["mount_reference"]["mount_center_m"])
    mid360_pose = [
        mid_mount_center[0],
        mid_mount_center[1],
        mid_mount_center[2],
        0.0,
        0.0,
        4.712389,
    ]
    mid360_laser_origin = [mid_mount_center[0], mid_mount_center[1], round(mid_mount_center[2] + 0.1, 6)]

    front_body = find_front_camera_body(front_objects)
    front_body_center = round_vec(front_body["center_m"]) if front_body else None
    front_lens_center = [0.0, 0.1032, 0.0185]
    down_lens_center = [0.0, 0.0145, -0.0263]

    assembly_bounds_min = round_vec(full["camera"]["bounds_min"])
    assembly_bounds_max = round_vec(full["camera"]["bounds_max"])
    collision_center, collision_size = bbox_center_size(assembly_bounds_min, assembly_bounds_max)

    params = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "purpose": "DAE-derived geometry replacement parameters for Sunray150 with MID360.",
        "scope": {
            "replace": ["rotor center XYZ", "camera extrinsics", "collision envelope"],
            "hold_for_review": ["MID360 mechanical mount pose", "MID360 point-cloud origin", "MID360 IMU/LiDAR extrinsic"],
            "do_not_replace": ["mass", "inertia", "motorConstant", "momentConstant", "lift_cofficient", "controller gains", "sensor timing"],
        },
        "sources": {
            "full_assembly_manifest": str(FULL_ASSEMBLY_MANIFEST.relative_to(PROJECT_ROOT)),
            "front_module_objects": str(FRONT_MODULE_OBJECTS.relative_to(PROJECT_ROOT)),
        },
        "coordinate_frame": {
            "unit": "m",
            "frame": "Sunray/SDF base_link frame used by the accepted DAE assembly audit",
            "axis_note": "Existing project convention treats +X as nose and -X as tail for MID360 connector review.",
        },
        "rotors": rotors,
        "mworks_dronefixed_mapping": {
            "Dronefixed1": rotors["rotor_0_front_right"]["center_m"],
            "Dronefixed2": rotors["rotor_2_front_left"]["center_m"],
            "Dronefixed3": rotors["rotor_1_back_left"]["center_m"],
            "Dronefixed4": rotors["rotor_3_back_right"]["center_m"],
        },
        "sdf_rotor_mapping": {
            "rotor_0": rotors["rotor_0_front_right"]["center_m"],
            "rotor_1": rotors["rotor_1_back_left"]["center_m"],
            "rotor_2": rotors["rotor_2_front_left"]["center_m"],
            "rotor_3": rotors["rotor_3_back_right"]["center_m"],
        },
        "mid360": {
            "mechanical_mount_pose_xyz_rpy_candidate": round_vec(mid360_pose),
            "laser_sensor_origin_candidate_m": mid360_laser_origin,
            "official_point_cloud_to_imu_translation_m": [0.011, 0.02329, -0.04412],
            "fast_lio_lidar_pose_in_imu_body_frame_m": [-0.011, -0.02329, 0.04412],
            "mount_center_m": mid_mount_center,
            "visual_bbox_center_m": mid_bbox_center,
            "visual_bbox_size_m": mid_bbox_size,
            "visual_bbox_min_m": round_vec(mid_bbox["min"]),
            "visual_bbox_max_m": round_vec(mid_bbox["max"]),
            "yaw_rad": 4.712389,
            "yaw_deg": 270.0,
            "confidence": "high for mount/yaw, medium for laser origin because the Sunray livox_mid360 model keeps its ray sensor at local z=0.1",
            "source": "user-reviewed four-hole MID360 fit, accepted tail-connector yaw, and local livox_mid360.sdf base_link/ray-sensor offsets",
            "official_reference": "Livox Mid-360 User Manual: point-cloud coordinate origin O-XYZ and built-in IMU position (11.0, 23.29, -44.12) mm in point-cloud coordinates.",
            "previous_sdf_pose_xyz_rpy": CURRENT_SDF["mid360_pose_xyz_rpy"],
            "delta_xyz_from_previous_sdf_m": vec_delta(mid360_pose[:3], CURRENT_SDF["mid360_pose_xyz_rpy"][:3]),
            "replacement_status": "hold_for_review",
            "review_reason": (
                "Livox official documents define a point-cloud coordinate origin O-XYZ and a built-in IMU, "
                "while FAST-LIO expects LiDAR pose in IMU body frame. The local Gazebo model also places "
                "its ray sensor at base_link local z=0.1. These are not the same as the mechanical mount center."
            ),
        },
        "cameras": {
            "front": {
                "pose_xyz_rpy": [front_lens_center[0], front_lens_center[1], front_lens_center[2], 0.0, 0.0, 0.0],
                "body_center_m": front_body_center,
                "optical_center_candidate_m": front_lens_center,
                "confidence": "medium",
                "source": "DAE front camera body plus accepted lens overlay marker",
                "previous_sdf_pose_xyz_rpy": CURRENT_SDF["camera_front_pose_xyz_rpy"],
                "delta_xyz_from_previous_sdf_m": vec_delta(front_lens_center, CURRENT_SDF["camera_front_pose_xyz_rpy"][:3]),
            },
            "down": {
                "pose_xyz_rpy": [down_lens_center[0], down_lens_center[1], down_lens_center[2], 0.0, 1.5707963, 3.14],
                "optical_center_candidate_m": down_lens_center,
                "confidence": "medium",
                "source": "accepted bottom camera lens overlay marker; retains existing down-camera RPY",
                "previous_sdf_pose_xyz_rpy": CURRENT_SDF["camera_down_pose_xyz_rpy"],
                "delta_xyz_from_previous_sdf_m": vec_delta(down_lens_center, CURRENT_SDF["camera_down_pose_xyz_rpy"][:3]),
            },
        },
        "collision_envelope": {
            "base_link_box_pose_xyz_rpy": [collision_center[0], collision_center[1], collision_center[2], 0.0, 0.0, 0.0],
            "base_link_box_size_xyz": collision_size,
            "assembly_bounds_min_m": assembly_bounds_min,
            "assembly_bounds_max_m": assembly_bounds_max,
            "confidence": "medium",
            "source": "conservative AABB of accepted full DAE assembly bounds, including propellers and top MID360",
            "previous_sdf_pose_xyz_rpy": CURRENT_SDF["base_collision_pose_xyz_rpy"],
            "previous_sdf_size_xyz": CURRENT_SDF["base_collision_size_xyz"],
        },
    }
    return params


def write_markdown(params: dict) -> None:
    lines = [
        "# Sunray150 DAE Assembly Parameters",
        "",
        "Source: accepted DAE/Blender assembly audit. These values replace geometry only.",
        "Motor/thrust, mass, inertia, controller, and timing parameters remain unchanged.",
        "",
        "## Rotor Centers",
        "",
        "| Rotor | New XYZ m | Previous SDF XYZ m | Delta m | Confidence |",
        "|---|---:|---:|---:|---|",
    ]
    for name, item in params["rotors"].items():
        lines.append(
            f"| `{name}` | `{item['center_m']}` | `{item['previous_sdf_center_m']}` | "
            f"`{item['delta_from_previous_sdf_m']}` | {item['confidence']} |"
        )

    mid = params["mid360"]
    lines += [
        "",
        "## MID360",
        "",
        f"- mechanical mount pose candidate xyz/rpy: `{mid['mechanical_mount_pose_xyz_rpy_candidate']}`",
        f"- laser sensor origin candidate: `{mid['laser_sensor_origin_candidate_m']}`",
        f"- mount center: `{mid['mount_center_m']}`",
        f"- visual bbox center: `{mid['visual_bbox_center_m']}`",
        f"- visual bbox size: `{mid['visual_bbox_size_m']}`",
        f"- official point-cloud to IMU translation m: `{mid['official_point_cloud_to_imu_translation_m']}`",
        f"- FAST-LIO LiDAR pose in IMU body frame m: `{mid['fast_lio_lidar_pose_in_imu_body_frame_m']}`",
        f"- confidence: {mid['confidence']}",
        f"- official reference: {mid['official_reference']}",
        f"- replacement status: {mid['replacement_status']} - {mid['review_reason']}",
        "",
        "## Cameras",
        "",
    ]
    for name, item in params["cameras"].items():
        lines.append(f"- {name}: pose xyz/rpy `{item['pose_xyz_rpy']}`, confidence {item['confidence']}")

    col = params["collision_envelope"]
    lines += [
        "",
        "## Collision Envelope",
        "",
        f"- base_link box pose xyz/rpy: `{col['base_link_box_pose_xyz_rpy']}`",
        f"- base_link box size xyz: `{col['base_link_box_size_xyz']}`",
        f"- source: {col['source']}",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    params = build_parameters()
    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(params, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(params)
    print(OUT_JSON)
    print(OUT_MD)


if __name__ == "__main__":
    main()
