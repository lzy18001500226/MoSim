import os
import sys
import time
import traceback
from pathlib import Path

import bpy
import addon as blender_mcp_addon


REPO_ROOT = Path(r"C:\Users\HP\Desktop\MoSim")
ADDON_PATH = REPO_ROOT / "Docs" / "Skills" / "Blender-MCP" / "addon.py"
LOG_DIR = REPO_ROOT / "Results" / "logs" / "blender_mcp"
LOG_PATH = LOG_DIR / "start_blender_mcp.log"


def log(message: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def enable_addon() -> None:
    if not ADDON_PATH.exists():
        raise FileNotFoundError(f"Missing Blender MCP addon: {ADDON_PATH}")

    bpy.ops.preferences.addon_install(filepath=str(ADDON_PATH), overwrite=True)
    bpy.ops.preferences.addon_enable(module="addon")

    prefs = bpy.context.preferences.addons.get("addon")
    if prefs and hasattr(prefs.preferences, "telemetry_consent"):
        prefs.preferences.telemetry_consent = False

    bpy.ops.wm.save_userpref()
    log("Blender MCP addon installed/enabled with telemetry_consent=false")


def start_server() -> None:
    scene = bpy.context.scene
    scene.blendermcp_port = int(os.environ.get("BLENDER_MCP_PORT", "9876"))
    host = os.environ.get("BLENDER_MCP_HOST", "0.0.0.0")
    scene.blendermcp_use_polyhaven = False
    scene.blendermcp_use_hyper3d = False
    scene.blendermcp_use_sketchfab = False
    scene.blendermcp_use_hunyuan3d = False

    if hasattr(bpy.types, "blendermcp_server") and bpy.types.blendermcp_server:
        bpy.types.blendermcp_server.stop()
        del bpy.types.blendermcp_server
        scene.blendermcp_server_running = False
        log("Stopped existing Blender MCP addon server before rebinding host")

    if scene.blendermcp_server_running:
        log(f"Blender MCP addon server already running on port {scene.blendermcp_port}")
        return

    bpy.types.blendermcp_server = blender_mcp_addon.BlenderMCPServer(host=host, port=scene.blendermcp_port)
    bpy.types.blendermcp_server.start()
    scene.blendermcp_server_running = True
    log(f"Blender MCP addon server started host={host} port={scene.blendermcp_port}")


def main() -> None:
    try:
        log(f"Starting Blender MCP bootstrap with Blender {bpy.app.version_string}")
        enable_addon()
        start_server()
        log("Blender MCP bootstrap complete")
    except Exception as exc:
        log(f"Blender MCP bootstrap failed: {exc}")
        log(traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
