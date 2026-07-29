"""Static contract for the generated local ROS1 source workspace."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "Config" / "runtime" / "ros1_local_source_manifest.v1.json"
SCRIPT_PATH = ROOT / "Scripts" / "sunray" / "prepare_local_ros1_workspace.sh"
PX4_BUILD_SCRIPT_PATH = ROOT / "Scripts" / "sunray" / "build_local_px4_sitl.sh"


class LocalRos1SourceWorkspaceContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    def test_manifest_uses_src_as_the_only_project_source_root(self) -> None:
        self.assertEqual(self.manifest["schema"], "mosim.ros1_local_source_manifest.v1")
        self.assertEqual(self.manifest["project_source_root"], "src")
        self.assertEqual(self.manifest["workspace_root"], "build/ros1/local_source_ws")

        for component in self.manifest["components"]:
            source_path = component["source_path"]
            self.assertTrue(source_path.startswith("src/"), component)
            self.assertTrue((ROOT / source_path).is_dir(), source_path)

    def test_profiles_resolve_to_existing_src_directories(self) -> None:
        profiles = self.manifest["profiles"]

        def collect(profile_id: str, visited: set[str] | None = None) -> list[dict[str, str]]:
            visited = set() if visited is None else visited
            self.assertNotIn(profile_id, visited)
            visited.add(profile_id)
            profile = profiles[profile_id]
            links: list[dict[str, str]] = []
            if "extends" in profile:
                links.extend(collect(profile["extends"], visited))
            links.extend(profile["links"])
            return links

        for profile_id in profiles:
            workspace_paths: set[str] = set()
            for link in collect(profile_id):
                self.assertTrue(link["source_path"].startswith("src/"), link)
                self.assertTrue((ROOT / link["source_path"]).is_dir(), link)
                self.assertNotIn(link["workspace_path"], workspace_paths, link)
                workspace_paths.add(link["workspace_path"])

    def test_extended_profiles_include_parent_build_packages(self) -> None:
        profiles = self.manifest["profiles"]

        def collect_packages(profile_id: str) -> list[str]:
            profile = profiles[profile_id]
            packages: list[str] = []
            if "extends" in profile:
                packages.extend(collect_packages(profile["extends"]))
            packages.extend(profile.get("build_packages", []))
            return list(dict.fromkeys(packages))

        self.assertEqual(
            collect_packages("controller"),
            [
                "sunray_msgs",
                "livox_ros_driver",
                "livox_laser_simulation",
                "sunray_simulator",
                "px4ctrl",
            ],
        )

    def test_workspace_script_rejects_legacy_source_roots(self) -> None:
        script = SCRIPT_PATH.read_text(encoding="utf-8")
        self.assertIn("workspace must remain below", script)
        self.assertIn("manifest source resolves outside src", script)
        self.assertIn("--only-pkg-with-deps", script)
        self.assertIn("sanitize_ros_build_environment", script)
        self.assertIn("--verify", script)
        self.assertIn("build_packages.extend(parent_packages)", script)
        self.assertIn("ROSPACK_REALPATH", script)
        self.assertIn("unset ROS_PACKAGE_PATH", script)
        self.assertNotIn("References/", script)
        self.assertNotIn("/opt/mosim_work", script)
        self.assertNotIn("Results/", script)

    def test_px4_snapshot_contains_the_required_classic_sitl_sources(self) -> None:
        px4 = ROOT / "src" / "flight_stack" / "px4" / "PX4-Autopilot"
        self.assertTrue((px4 / "LICENSE").is_file())
        self.assertTrue((px4 / "src" / "modules" / "mavlink" / "mavlink").is_dir())
        self.assertTrue((px4 / "Tools" / "simulation" / "gazebo-classic" / "sitl_gazebo-classic").is_dir())
        self.assertFalse((px4 / ".git").exists())
        self.assertFalse((px4 / "build").exists())

    def test_px4_build_entrypoint_keeps_outputs_outside_the_source_tree(self) -> None:
        script = PX4_BUILD_SCRIPT_PATH.read_text(encoding="utf-8")

        self.assertIn("src/flight_stack/px4/PX4-Autopilot", script)
        self.assertIn("build/px4/px4_sitl_default", script)
        self.assertIn("--build-dir must remain below build/px4/", script)
        self.assertIn("cmake -S", script)
        self.assertIn("-DCONFIG=px4_sitl_default", script)
        self.assertIn("--bootstrap-python", script)
        self.assertIn("build/px4/python_deps", script)
        self.assertIn("Tools/setup/requirements.txt", script)
        self.assertIn("/opt/ros/noetic/lib/python3/dist-packages", script)
        self.assertIn("PX4_BOOTSTRAP_PACKAGES=(kconfiglib future)", script)
        self.assertIn("import menuconfig, defconfig, genconfig, genmsg, future", script)
        self.assertIn("--target", script)
        self.assertNotIn("References/", script)
        self.assertNotIn("Results/", script)
        self.assertNotIn("/opt/mosim_work", script)

    def test_px4_snapshot_has_a_version_fallback_without_git_metadata(self) -> None:
        px4 = ROOT / "src" / "flight_stack" / "px4" / "PX4-Autopilot"
        px4_cmake = (px4 / "CMakeLists.txt").read_text(encoding="utf-8")
        version_cmake = (px4 / "src" / "lib" / "version" / "CMakeLists.txt").read_text(
            encoding="utf-8"
        )
        snapshot_template = (px4 / "src" / "lib" / "version" / "build_git_version_snapshot.h.in").read_text(
            encoding="utf-8"
        )

        self.assertIn('set(PX4_GIT_TAG "v1.14.0")', px4_cmake)
        self.assertIn('set(PX4_SNAPSHOT_GIT_VERSION "3c0f1446ec13fa199dcbfc5cf4bd6c24176806df")', px4_cmake)
        self.assertIn(
            'set(PX4_SNAPSHOT_MAVLINK_GIT_VERSION "4cc36bca4b62f9e5e17665426f9d56afea6f5775")',
            px4_cmake,
        )
        self.assertIn("source snapshot has no Git metadata", px4_cmake)
        self.assertIn('if(EXISTS "${PX4_SOURCE_DIR}/.git")', px4_cmake)
        self.assertIn("build_git_version_snapshot.h.in", version_cmake)
        self.assertIn("PX4 source snapshot version is not declared", version_cmake)
        self.assertIn("PX4 MAVLink snapshot version is not declared", version_cmake)
        self.assertIn("PX4_GIT_VERSION_STR", snapshot_template)
        self.assertIn("MAVLINK_LIB_GIT_VERSION_STR", snapshot_template)
        self.assertIn("MAVLINK_LIB_GIT_VERSION_BINARY", snapshot_template)
        self.assertIn("PX4_GIT_TAG_STR", snapshot_template)

    def test_foundation_sources_do_not_depend_on_symlink_crossing_paths(self) -> None:
        simulator_cmake = (
            ROOT / "src" / "simulation" / "gazebo" / "sunray" / "CMakeLists.txt"
        ).read_text(encoding="utf-8")
        ugv_source = (
            ROOT / "src" / "simulation" / "gazebo" / "sunray" / "src" / "ugv_circle.cpp"
        ).read_text(encoding="utf-8")
        livox_cmake = (
            ROOT
            / "src"
            / "simulation"
            / "gazebo"
            / "plugins"
            / "sunray"
            / "livox_laser_simulation"
            / "CMakeLists.txt"
        ).read_text(encoding="utf-8")

        self.assertNotIn("../../General_Module/sunray_common/common_lib", simulator_cmake)
        self.assertIn("${catkin_EXPORTED_TARGETS}", simulator_cmake)
        self.assertIn("#include <sunray_msgs/UAVState.h>", ugv_source)
        self.assertIn("${${PROJECT_NAME}_EXPORTED_TARGETS}", livox_cmake)

    def test_flight_adapter_uses_active_catkin_exports(self) -> None:
        adapter_cmake = (
            ROOT / "src" / "flight_stack" / "mavros" / "sunray_uav_control" / "CMakeLists.txt"
        ).read_text(encoding="utf-8")

        self.assertIn("find_path(SUNRAY_COMMON_LIB_DIR", adapter_cmake)
        self.assertIn("${CMAKE_SOURCE_DIR}/General_Module/sunray_common/common_lib", adapter_cmake)
        self.assertIn("${catkin_EXPORTED_TARGETS}", adapter_cmake)
        self.assertNotIn("sunray_control_gencpp)", adapter_cmake)

    def test_fast_lio_waits_for_its_generated_messages(self) -> None:
        fast_lio_cmake = (ROOT / "src" / "perception" / "fast_lio" / "CMakeLists.txt").read_text(
            encoding="utf-8"
        )

        self.assertIn("add_dependencies(fastlio_mapping ${${PROJECT_NAME}_EXPORTED_TARGETS}", fast_lio_cmake)
        self.assertIn("eigen_conversions", fast_lio_cmake)

    def test_px4ctrl_default_generated_backend_is_local_and_complete(self) -> None:
        px4ctrl = ROOT / "src" / "control" / "runtime_adapters" / "px4ctrl"
        generated = px4ctrl / "generated"
        legacy = generated / "legacy_px4ctrl"
        expected_legacy_files = [
            "PX4CTRL_Core_CFunction_Sysblock.c",
            "PX4CTRL_Core_CFunction_Sysblock.h",
            "PX4CTRL_Core_CFunction_Sysblock_data.c",
            "PX4CTRL_Core_CFunction_Sysblock_private.h",
            "PX4CTRL_Core_CFunction_Sysblock_extern_include.h",
            "mwb_runtime.h",
            "mwb_types.h",
            "extern_inc/momodel_extern_ince1.c",
        ]

        self.assertTrue((generated / "README.md").is_file())
        for relative_path in expected_legacy_files:
            self.assertTrue((legacy / relative_path).is_file(), relative_path)
        self.assertTrue((generated / "golden_slice" / "px4ctrl_core.cpp").is_file())
        self.assertTrue((generated / "golden_slice" / "px4ctrl_core.h").is_file())

        px4ctrl_cmake = (px4ctrl / "CMakeLists.txt").read_text(encoding="utf-8")
        self.assertIn("MOSIM_PX4CTRL_GENERATED_ROOT", px4ctrl_cmake)
        self.assertIn("mosim_require_path_within", px4ctrl_cmake)
        self.assertIn("${catkin_EXPORTED_TARGETS}", px4ctrl_cmake)
        self.assertNotIn("Results/", px4ctrl_cmake)
        self.assertNotIn("Scripts/sunray/px4ctrl_golden_slice", px4ctrl_cmake)


if __name__ == "__main__":
    unittest.main()
