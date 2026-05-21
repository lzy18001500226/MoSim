import json
import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SPEAR_ROOT = PROJECT_ROOT / "references" / "AirSim" / "spear"
sys.path.insert(0, str(SPEAR_ROOT / "python"))

import spear  # noqa: E402


def simplify(value):
    if isinstance(value, dict):
        return {k: simplify(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [simplify(v) for v in value]
    if isinstance(value, np.ndarray):
        return {
            "shape": list(value.shape),
            "dtype": str(value.dtype),
            "min": float(np.nanmin(value)) if value.size else None,
            "max": float(np.nanmax(value)) if value.size else None,
        }
    try:
        json.dumps(value)
    except TypeError:
        return str(value)
    return value


def main():
    out_dir = PROJECT_ROOT / "results" / "tmp" / "spear_rpc_minimal"
    out_dir.mkdir(parents=True, exist_ok=True)

    config = spear.get_config()
    spear.configure_system(config=config)
    instance = spear.Instance(config=config)
    running = instance.is_running()
    game = instance.get_game()

    with instance.begin_frame():
        viewport_desc = game.rendering_service.get_current_viewport_desc()
        actor_handles = game.unreal_service.find_actors(as_handle=True)
        bp_camera_sensor_uclass = game.unreal_service.load_class(
            uclass="AActor",
            name="/SpContent/Blueprints/BP_CameraSensor.BP_CameraSensor_C",
        )
        bp_camera_sensor = game.unreal_service.spawn_actor(
            uclass=bp_camera_sensor_uclass,
            spawn_parameters={"ObjectFlags": ["RF_Transient"]},
        )
        final_tone_curve_hdr_component = game.unreal_service.get_component_by_name(
            actor=bp_camera_sensor,
            component_name="DefaultSceneRoot.final_tone_curve_hdr_",
            uclass="USpSceneCaptureComponent2D",
        )
        game.rendering_service.align_camera_with_viewport(
            camera_sensor=bp_camera_sensor,
            camera_components=final_tone_curve_hdr_component,
            viewport_desc=viewport_desc,
            widths=160,
            heights=90,
        )
        final_tone_curve_hdr_component.Initialize()
        final_tone_curve_hdr_component.initialize_sp_funcs()

    with instance.end_frame():
        pass

    instance.step(num_frames=2)

    with instance.begin_frame():
        pass
    with instance.end_frame():
        data_bundle = final_tone_curve_hdr_component.read_pixels()

    image = data_bundle["arrays"]["data"].copy()
    image_path = out_dir / "final_tone_curve_hdr_160x90.png"
    plt.imsave(image_path, np.clip(image[:, :, [2, 1, 0]], 0.0, 1.0))
    image_min = float(np.nanmin(image))
    image_max = float(np.nanmax(image))
    image_mean = float(np.nanmean(image))

    with instance.begin_frame():
        pass
    with instance.end_frame():
        final_tone_curve_hdr_component.terminate_sp_funcs()
        final_tone_curve_hdr_component.Terminate()
        game.unreal_service.destroy_actor(actor=bp_camera_sensor)

    summary = {
        "status": "ok",
        "launch_mode": config.SPEAR.LAUNCH_MODE,
        "rpc_port": config.SP_SERVICES.RPC_SERVICE.RPC_SERVER_PORT,
        "instance_is_running": running,
        "actor_count": len(actor_handles),
        "actor_handle_sample": actor_handles[:5],
        "viewport_desc": simplify(viewport_desc),
        "image_path": str(image_path),
        "image_shape": list(image.shape),
        "image_dtype": str(image.dtype),
        "image_min": image_min,
        "image_max": image_max,
        "image_mean": image_mean,
    }
    summary_path = out_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
