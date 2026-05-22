# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os
import shutil
import statistics
import tempfile
import time
from typing import Dict, List, Tuple

import numpy as np

# Utility constants
DEFAULT_BLUR = 3  # Gaussian-blur kernel (pixels); 0 disables blurring
DEFAULT_TOLERANCE = 5.0  # Mean-difference threshold (0-255 scale)


class Validator:
    """Utility class for capturing and validating render-product images in benchmarks.

    Example usage:

        from isaacsim.benchmark.services.validation import Validator
        from pxr import Usd
        import omni.usd

        stage = omni.usd.get_context().get_stage()
        validator = Validator(tolerance=2.5, blur_kernel=5)

        # Discover enabled render-products under the default *HydraTextures* root
        validator.build_render_product_map(stage)

        # Capture RGB images and (optionally) regenerate the golden set
        out_dir = validator.capture_images(
            stage,
            benchmark_name="my_benchmark",
            output_root="captures",
            golden_root="golden_data",
        )

        # Compare the new images against the reference
        validator.validate_images(out_dir, os.path.join("golden_data", "my_benchmark"))
    """

    def __init__(
        self,
        *,
        tolerance: float = DEFAULT_TOLERANCE,
        blur_kernel: int = DEFAULT_BLUR,
        regenerate_golden: bool = False,
        output_root: str = "captures",
        golden_root: str = "golden_data",
        auto_cleanup: bool = True,
    ) -> None:
        """Create a new *Validator* instance.

        Args:
            param tolerance: Mean-difference threshold used during validation.
            param blur_kernel: Gaussian-blur kernel size (0 disables blurring).
            param regenerate_golden: Replace the golden reference images instead of
                validating against them.
            param output_root: Base directory where capture folders are created.
            param golden_root: Base directory storing golden reference images.
            param auto_cleanup: If *True* the last capture folder is deleted
                automatically after :py:meth:`validate_images` completes.
        """
        self.tolerance: float = tolerance
        self.blur_kernel: int = blur_kernel
        self.regenerate_golden: bool = regenerate_golden

        self.output_root: str = os.fspath(output_root)
        self.golden_root: str = os.fspath(golden_root)

        self.auto_cleanup: bool = auto_cleanup

        self.render_product_map: dict[str, str] = {}
        self._last_capture_path: str | None = None
        self._last_benchmark_name: str | None = None

    def build_render_product_map(
        self,
        stage,
        root_prim_path: str = "/Render/OmniverseKit/HydraTextures",
    ) -> dict[str, str]:
        """Populate *self.render_product_map* by scanning *stage*.

        Every camera render product under *root_prim_path* is considered and validated via
        ``isaacsim.core.utils.render_product.get_camera_prim_path``.  Prims that
        fail the check are silently ignored.

        Args:
            param stage: USD stage to inspect.
            param root_prim_path: Path whose subtree is searched for render-products.

        Returns:
            Mapping from render-product USD path → human-readable folder name.
        """
        from isaacsim.core.utils.render_product import get_camera_prim_path
        from pxr import Usd

        root_prim = stage.GetPrimAtPath(root_prim_path)
        if not root_prim.IsValid():
            raise RuntimeError(f"Root prim '{root_prim_path}' not found on stage")

        self.render_product_map.clear()

        for prim in list(Usd.PrimRange(root_prim))[1:]:  # skip root itself
            try:
                nice_name = str(get_camera_prim_path(str(prim.GetPath()))).lstrip("/")
            except RuntimeError:
                continue  # not a render-product – ignore

            rp_path = str(prim.GetPath())
            if nice_name in self.render_product_map.values():
                base = nice_name
                idx = 1
                while f"{base}_{idx}" in self.render_product_map.values():
                    idx += 1
                nice_name = f"{base}_{idx}"

            self.render_product_map[rp_path] = nice_name

        return self.render_product_map

    def capture_images(
        self,
        stage,
        *,
        benchmark_name: str,
        output_root: str | None = None,
        golden_root: str | None = None,
        writer_name: str = "BasicWriter",
    ) -> str:
        """Capture RGB images for every discovered render-product.

        If *self.render_product_map* is empty it is automatically populated via
        :pymeth:`build_render_product_map` using the default *HydraTextures* root.

        The behaviour (overwrite vs. create timestamped directory) is controlled
        by *self.regenerate_golden*.

        Returns:
            Absolute path of the directory where PNGs were written.
        """
        import os
        from datetime import datetime

        import omni.replicator.core as rep

        if not self.render_product_map:
            self.build_render_product_map(stage)

        # Resolve roots
        if output_root is None:
            output_root = self.output_root
        else:
            self.output_root = os.fspath(output_root)

        if golden_root is None:
            golden_root = self.golden_root
        else:
            self.golden_root = os.fspath(golden_root)

        output_root = os.fspath(output_root)
        golden_root = os.fspath(golden_root)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if self.regenerate_golden:
            write_location = os.path.join(golden_root, benchmark_name)
            if os.path.isdir(write_location):
                shutil.rmtree(write_location)
        else:
            write_location = os.path.join(output_root, f"{benchmark_name}_{timestamp}")

        os.makedirs(write_location, exist_ok=True)

        writer = rep.WriterRegistry.get(writer_name)
        writer.initialize(output_dir=write_location, rgb=True)
        writer.attach(self.render_product_map.keys())
        rep.orchestrator.step()
        writer.detach()

        # give time for images to flush to disk
        time.sleep(1)

        # Rename folders to human-readable names
        for rp_path, nice_name in self.render_product_map.items():
            old_dir = os.path.join(write_location, rp_path.split("/")[-1])
            new_dir = os.path.join(write_location, nice_name)
            if os.path.isdir(old_dir):
                os.makedirs(os.path.dirname(new_dir), exist_ok=True)
                shutil.move(old_dir, new_dir)

        if self.regenerate_golden:
            print("\nGolden images regenerated – please verify visually:\n" + write_location)

        self._last_capture_path = write_location
        self._last_benchmark_name = benchmark_name

        return write_location

    def validate_images(
        self,
        captured_dir: str | None = None,
        golden_dir: str | None = None,
    ) -> bool:
        """Validate the captured images against the golden set.

        Args:
            captured_dir: Directory with newly captured PNGs.  If *None* the most
                recent directory returned by :py:meth:`capture_images` is used.
            golden_dir: Directory with golden PNGs.  If *None* the *golden_root*
                provided at construction time is used.
        """
        if captured_dir is None:
            captured_dir = self._last_capture_path
        else:
            self._last_capture_path = captured_dir

        if captured_dir is None:
            raise ValueError("captured_dir not specified and no capture has been performed yet")

        if golden_dir is None:
            if self._last_benchmark_name is not None:
                golden_dir = os.path.join(self.golden_root, self._last_benchmark_name)
            else:
                golden_dir = self.golden_root

        import cv2
        import numpy as np
        from PIL import Image

        print("\nValidating Images")
        print("-" * 40)

        def _collect_pngs(root: str) -> list[str]:
            return sorted(
                os.path.relpath(os.path.join(r, f), root)
                for r, _, files in os.walk(root)
                for f in files
                if f.endswith(".png")
            )

        all_passed = True

        for rp_path, nice_name in self.render_product_map.items():
            cap_root = os.path.join(captured_dir, nice_name)
            gold_root = os.path.join(golden_dir, nice_name)

            if not (os.path.isdir(cap_root) and os.path.isdir(gold_root)):
                print(f"Missing directories for render product '{nice_name}'")
                print(f"Capture dir: {cap_root}\nGolden dir:  {gold_root}")
                all_passed = False
                continue

            out_pngs = _collect_pngs(cap_root)
            gold_pngs = _collect_pngs(gold_root)

            common_files = sorted(set(out_pngs) & set(gold_pngs))

            if not common_files:
                print(f"No common PNG files for render product {nice_name}; skipping")
                continue

            for rel in common_files:
                cap_path = os.path.join(cap_root, rel)
                gold_path = os.path.join(gold_root, rel)

                cap_arr = np.array(Image.open(cap_path))
                gold_arr = np.array(Image.open(gold_path))

                if cap_arr.shape != gold_arr.shape:
                    print(f"Shape mismatch: {rel}")
                    all_passed = False
                    continue

                if self.blur_kernel > 0:
                    k = self.blur_kernel | 1  # must be odd
                    cap_arr = cv2.GaussianBlur(cap_arr, (k, k), 0)
                    gold_arr = cv2.GaussianBlur(gold_arr, (k, k), 0)

                diff = cv2.absdiff(cap_arr, gold_arr)
                mean_diff = diff.mean()

                if mean_diff <= self.tolerance:
                    continue  # passes – no diff written

                all_passed = False

                # ---------- visual diff ----------
                base = cap_arr.copy()
                base = self._ensure_rgb(base)

                mag = diff.max(axis=2) if diff.ndim == 3 else diff  # H×W
                norm = (mag * 255.0 / mag.max()).astype(np.uint8)

                red_layer = np.zeros_like(base)
                red_layer[..., 0] = 255  # R channel (RGB)

                alpha = (norm.astype(np.float32) / 255.0)[..., None]
                overlay = (red_layer.astype(np.float32) * alpha + base.astype(np.float32) * (1.0 - alpha)).astype(
                    np.uint8
                )

                tmp = tempfile.mkdtemp(prefix="diff_")
                out_png = os.path.join(tmp, f"diff_{os.path.basename(cap_path)}")
                self._write_png(out_png, overlay)
                print(f"[FAIL] {nice_name}: mean={mean_diff:.2f}  diff→ {out_png}")

        if not all_passed:
            print("\nValidation failed for some images. Check the diff images at the paths listed above.\n")
        else:
            print("\nValidation passed for all images.\n")

        if self.auto_cleanup:
            self.clear_last_capture()

        return all_passed

    def clear_last_capture(self) -> None:
        """Delete the last capture directory created by :pymeth:`capture_images`."""
        if self._last_capture_path and os.path.isdir(self._last_capture_path):
            shutil.rmtree(self._last_capture_path)
        self._last_capture_path = None

    @staticmethod
    def _ensure_rgb(arr):
        """Return a three-channel RGB *view* of *arr* (H×W×C)."""
        import cv2

        if arr.ndim == 2:  # Gray ⇒ RGB
            return cv2.cvtColor(arr, cv2.COLOR_GRAY2RGB)
        if arr.shape[2] == 4:  # RGBA ⇒ RGB
            return arr[:, :, :3]
        return arr

    @staticmethod
    def _write_png(path: str, rgb) -> None:
        """Write *rgb* (RGB) to *path* as PNG using cv2 (expects BGR)."""
        import cv2

        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        cv2.imwrite(path, bgr)

    # e2e runner
    def run(
        self,
        stage,
        *,
        benchmark_name: str,
    ) -> bool:
        """Full pipeline: discover → capture → validate.

        Returns *True* if validation passes (or when *regenerate_golden* is
        *True*); *False* otherwise.
        """
        self.build_render_product_map(stage)
        self.capture_images(stage, benchmark_name=benchmark_name)

        if self.regenerate_golden:
            return True

        result = self.validate_images()

        return result

    @classmethod
    def from_cli_args(
        cls,
        args,
        *,
        auto_cleanup: bool | None = None,
    ) -> "Validator":
        """Construct a *Validator* directly from an *argparse* result object.

        The following attribute names are read if present: ``tolerance`` (DEFAULT_TOLERANCE), ``blur_kernel``
        (DEFAULT_BLUR), ``regenerate_golden`` (False), ``output_dir`` ("captures"),
        ``golden_dir`` ("golden_data").
        """
        tol = getattr(args, "tolerance", DEFAULT_TOLERANCE)
        blur = getattr(args, "blur_kernel", DEFAULT_BLUR)
        regen = getattr(args, "regenerate_golden", False)
        out_dir = getattr(args, "output_dir", "captures")
        gold_dir = getattr(args, "golden_dir", "golden_data")

        if auto_cleanup is None:
            auto_cleanup = True

        # Convert to absolute paths (relative → cwd)
        if not os.path.isabs(out_dir):
            out_dir = os.path.join(os.getcwd(), out_dir)
        if not os.path.isabs(gold_dir):
            gold_dir = os.path.join(os.getcwd(), gold_dir)

        return cls(
            tolerance=tol,
            blur_kernel=blur,
            regenerate_golden=regen,
            output_root=str(out_dir),
            golden_root=str(gold_dir),
            auto_cleanup=auto_cleanup,
        )


class CoordinateValidator:
    """Handles coordinate validation using multiple statistical methods.

    This class provides comprehensive coordinate validation for robotic systems
    using a voting system that combines three statistical methods: tolerance-based
    bounds checking, 3-Sigma outlier detection, and Interquartile Range (IQR)
    outlier detection.
    """

    def __init__(
        self,
        historical_data_path: str = "standalone_examples/benchmarks/validation/golden_data/benchmark_robots_nova_carter_ros2/historical_coordinates_data.json",
    ):
        """Create a new CoordinateValidator instance.

        Args:
            param historical_data_path: Path to the JSON file containing historical
                coordinate data for statistical validation.
        """
        self.historical_data_path = historical_data_path
        self.historical_positions: List[List[float]] = []
        self.historical_rotations: List[List[float]] = []
        self._load_historical_data()

    def calculate_bounds_from_historical_data(self) -> Dict[str, List[float]]:
        """Calculate min/max bounds from historical coordinate data.

        Returns:
            Dictionary containing minimum and maximum bounds for positions and rotations.
            Keys include 'min_final_position', 'max_final_position',
            'min_final_rotation', and 'max_final_rotation'.

        Raises:
            ValueError: If no historical data is available to calculate bounds.

        Example:

        .. code-block:: python

            >>> validator = CoordinateValidator()
            >>> bounds = validator.calculate_bounds_from_historical_data()
            >>> bounds['min_final_position']
            [-1.0, -1.0, 0.0]
        """
        if not self.historical_positions or not self.historical_rotations:
            raise ValueError("No historical data available to calculate bounds")

        # Calculate position bounds
        positions_array = np.array(self.historical_positions)
        min_final_position = positions_array.min(axis=0).tolist()
        max_final_position = positions_array.max(axis=0).tolist()

        # Calculate rotation bounds
        rotations_array = np.array(self.historical_rotations)
        min_final_rotation = rotations_array.min(axis=0).tolist()
        max_final_rotation = rotations_array.max(axis=0).tolist()

        return {
            "min_final_position": min_final_position,
            "max_final_position": max_final_position,
            "min_final_rotation": min_final_rotation,
            "max_final_rotation": max_final_rotation,
        }

    def _load_historical_data(self) -> None:
        """Load historical coordinate data for statistical validation."""
        if os.path.exists(self.historical_data_path):
            with open(self.historical_data_path, "r") as f:
                historical_data = json.load(f)
                for record in historical_data["data"]:
                    self.historical_positions.append(record["final_position"])
                    self.historical_rotations.append(record["final_rotation"])
            print(f"Loaded {len(self.historical_positions)} historical data points for statistical validation")
        else:
            print("Warning: No historical data found. Statistical methods will be skipped.")

    def within_bounds_with_tolerance(
        self, val: List[float], min_bounds: List[float], max_bounds: List[float], tolerance_percent: float = 0.05
    ) -> Tuple[bool, List[float]]:
        """Check if a value is within bounds with additional tolerance.

        Args:
            param val: The values to check against bounds.
            param min_bounds: Minimum acceptable values for each component.
            param max_bounds: Maximum acceptable values for each component.
            param tolerance_percent: Additional tolerance as a percentage of the range.

        Returns:
            Tuple containing a boolean indicating if all values are within bounds
            and a list of exceedance percentages for each component.

        Example:

        .. code-block:: python

            >>> validator = CoordinateValidator()
            >>> within_bounds, exceedance = validator.within_bounds_with_tolerance(
            ...     [1.0, 2.0, 3.0], [0.0, 0.0, 0.0], [2.0, 2.0, 2.0]
            ... )
            >>> within_bounds
            False
        """
        exceedance_percentages = []
        all_within_bounds = True

        for i, (v, min_val, max_val) in enumerate(zip(val, min_bounds, max_bounds)):
            range_val = abs(max_val - min_val)
            tolerance = tolerance_percent * range_val

            expanded_min = min_val - tolerance
            expanded_max = max_val + tolerance

            if v < min_val:
                exceedance = abs(v - min_val)
                exceedance_percent = (exceedance / range_val) * 100 if range_val > 0 else 0
                exceedance_percentages.append(-exceedance_percent)
            elif v > max_val:
                exceedance = abs(v - max_val)
                exceedance_percent = (exceedance / range_val) * 100 if range_val > 0 else 0
                exceedance_percentages.append(exceedance_percent)
            else:
                exceedance_percentages.append(0.0)

            if not (expanded_min <= v <= expanded_max):
                all_within_bounds = False

        return all_within_bounds, exceedance_percentages

    def three_sigma_outlier_detection(
        self, val: List[float], historical_data: List[List[float]], component_names: List[str]
    ) -> Tuple[bool, List[float], Dict]:
        """Detect outliers using the 3-Sigma rule.

        Args:
            param val: The values to check for outliers.
            param historical_data: Historical data points for comparison.
            param component_names: Names of the components being validated.

        Returns:
            Tuple containing a boolean indicating if all values pass the 3-Sigma test,
            a list of z-scores, and detailed statistics for each component.

        Example:

        .. code-block:: python

            >>> validator = CoordinateValidator()
            >>> historical = [[1.0, 2.0], [1.1, 2.1], [0.9, 1.9]]
            >>> passed, z_scores, stats = validator.three_sigma_outlier_detection(
            ...     [1.0, 2.0], historical, ["X", "Y"]
            ... )
            >>> passed
            True
        """
        if not historical_data:
            return True, [0.0] * len(val), {}

        component_data = []
        for i in range(len(val)):
            component_values = [record[i] for record in historical_data]
            component_data.append(component_values)

        z_scores = []
        stats_info = {}
        all_within_3sigma = True

        for i, (v, component_values, comp_name) in enumerate(zip(val, component_data, component_names)):
            if len(component_values) < 2:
                z_scores.append(0.0)
                continue

            mean_val = statistics.mean(component_values)
            std_val = statistics.stdev(component_values)

            z_score = (v - mean_val) / std_val if std_val > 0 else 0.0
            z_scores.append(z_score)

            stats_info[comp_name] = {
                "mean": mean_val,
                "std": std_val,
                "z_score": z_score,
                "is_outlier": abs(z_score) > 3.0,
            }

            if abs(z_score) > 3.0:
                all_within_3sigma = False

        return all_within_3sigma, z_scores, stats_info

    def iqr_outlier_detection(
        self, val: List[float], historical_data: List[List[float]], component_names: List[str]
    ) -> Tuple[bool, List[float], Dict]:
        """Detect outliers using the Interquartile Range (IQR) method.

        Args:
            param val: The values to check for outliers.
            param historical_data: Historical data points for comparison.
            param component_names: Names of the components being validated.

        Returns:
            Tuple containing a boolean indicating if all values pass the IQR test,
            a list of outlier distances, and detailed statistics for each component.

        Example:

        .. code-block:: python

            >>> validator = CoordinateValidator()
            >>> historical = [[1.0, 2.0], [1.1, 2.1], [0.9, 1.9], [1.05, 2.05]]
            >>> passed, distances, stats = validator.iqr_outlier_detection(
            ...     [1.0, 2.0], historical, ["X", "Y"]
            ... )
            >>> passed
            True
        """
        if not historical_data:
            return True, [0.0] * len(val), {}

        component_data = []
        for i in range(len(val)):
            component_values = [record[i] for record in historical_data]
            component_data.append(component_values)

        outlier_distances = []
        stats_info = {}
        all_within_iqr = True

        for i, (v, component_values, comp_name) in enumerate(zip(val, component_data, component_names)):
            if len(component_values) < 4:
                outlier_distances.append(0.0)
                continue

            q1 = statistics.quantiles(component_values, n=4)[0]
            q3 = statistics.quantiles(component_values, n=4)[2]
            iqr = q3 - q1

            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr

            if v < lower_bound:
                outlier_distance = lower_bound - v
            elif v > upper_bound:
                outlier_distance = v - upper_bound
            else:
                outlier_distance = 0.0

            outlier_distances.append(outlier_distance)

            stats_info[comp_name] = {
                "q1": q1,
                "q3": q3,
                "iqr": iqr,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "outlier_distance": outlier_distance,
                "is_outlier": outlier_distance > 0,
            }

            if outlier_distance > 0:
                all_within_iqr = False

        return all_within_iqr, outlier_distances, stats_info

    def voting_validation_system(
        self,
        val: List[float],
        min_bounds: List[float],
        max_bounds: List[float],
        historical_data: List[List[float]],
        component_names: List[str],
        tolerance_percent: float = 0.05,
    ) -> Tuple[bool, Dict]:
        """Voting system combining 5% rule, 3-Sigma, and IQR methods.

        This method applies three different validation techniques and uses a voting
        system where at least 2 out of 3 methods must pass for overall validation success.

        Args:
            param val: The values to validate.
            param min_bounds: Minimum acceptable values for each component.
            param max_bounds: Maximum acceptable values for each component.
            param historical_data: Historical data points for statistical comparison.
            param component_names: Names of the components being validated.
            param tolerance_percent: Additional tolerance as a percentage of the range.

        Returns:
            Tuple containing a boolean indicating overall validation success
            and detailed results from all three validation methods.

        Example:

        .. code-block:: python

            >>> validator = CoordinateValidator()
            >>> passed, results = validator.voting_validation_system(
            ...     [1.0, 2.0], [0.0, 0.0], [2.0, 3.0],
            ...     [[1.0, 2.0], [1.1, 2.1]], ["X", "Y"]
            ... )
            >>> passed
            True
        """
        # Method 1: 5% tolerance rule
        tolerance_pass, exceedance_percentages = self.within_bounds_with_tolerance(
            val, min_bounds, max_bounds, tolerance_percent
        )

        # Method 2: 3-Sigma outlier detection
        sigma_pass, z_scores, sigma_stats = self.three_sigma_outlier_detection(val, historical_data, component_names)

        # Method 3: IQR outlier detection
        iqr_pass, outlier_distances, iqr_stats = self.iqr_outlier_detection(val, historical_data, component_names)

        methods_passed = sum([tolerance_pass, sigma_pass, iqr_pass])
        overall_pass = methods_passed >= 2

        results = {
            "overall_pass": overall_pass,
            "methods_passed": methods_passed,
            "tolerance_method": {"passed": tolerance_pass, "exceedance_percentages": exceedance_percentages},
            "three_sigma_method": {"passed": sigma_pass, "z_scores": z_scores, "statistics": sigma_stats},
            "iqr_method": {"passed": iqr_pass, "outlier_distances": outlier_distances, "statistics": iqr_stats},
        }

        return overall_pass, results

    def validate_robot_coordinates(self, robots: List, golden_data: Dict[str, List[float]]) -> bool:
        """Validate coordinates for all robots using the voting system.

        Args:
            param robots: List of robot objects with get_world_pose() method.
            param golden_data: Dictionary containing coordinate bounds and validation data.

        Returns:
            Boolean indicating whether all robots passed coordinate validation.

        Example:

        .. code-block:: python

            >>> validator = CoordinateValidator()
            >>> golden_data = validator.calculate_bounds_from_historical_data()
            >>> validation_passed = validator.validate_robot_coordinates(robots, golden_data)
            >>> validation_passed
            True
        """
        min_final_position = golden_data["min_final_position"]
        max_final_position = golden_data["max_final_position"]
        min_final_rotation = golden_data["min_final_rotation"]
        max_final_rotation = golden_data["max_final_rotation"]

        overall_validation_passed = True

        for idx, robot in enumerate(robots):
            final_position, final_rotation = robot.get_world_pose()

            # Apply voting validation system for position
            pos_pass, pos_results = self.voting_validation_system(
                final_position, min_final_position, max_final_position, self.historical_positions, ["X", "Y", "Z"]
            )

            # Apply voting validation system for rotation
            rot_pass, rot_results = self.voting_validation_system(
                final_rotation, min_final_rotation, max_final_rotation, self.historical_rotations, ["X", "Y", "Z", "W"]
            )

            robot_voting_pass = pos_pass and rot_pass
            if not robot_voting_pass:
                overall_validation_passed = False

            self._print_validation_results(
                idx, final_position, final_rotation, pos_pass, pos_results, rot_pass, rot_results, robot_voting_pass
            )

        return overall_validation_passed

    def _print_validation_results(
        self,
        robot_idx: int,
        final_position: List[float],
        final_rotation: List[float],
        pos_pass: bool,
        pos_results: Dict,
        rot_pass: bool,
        rot_results: Dict,
        robot_voting_pass: bool,
    ) -> None:
        """Print detailed validation results for a robot.

        Args:
            param robot_idx: Index of the robot being validated.
            param final_position: Final position coordinates of the robot.
            param final_rotation: Final rotation coordinates of the robot.
            param pos_pass: Whether position validation passed.
            param pos_results: Detailed position validation results.
            param rot_pass: Whether rotation validation passed.
            param rot_results: Detailed rotation validation results.
            param robot_voting_pass: Whether overall robot validation passed.
        """
        print(f"\n{'='*60}")
        print(f"Robot {robot_idx} Validation Results:")
        print(f"{'='*60}")
        print(f"Final Position: {final_position}")
        print(f"Final Rotation: {final_rotation}")

        # Position validation results
        print(f"\nPosition Validation (Voting System: {pos_results['methods_passed']}/3 methods passed):")
        print(f"  Position Result: {'PASS' if pos_pass else 'FAIL'}")

        self._print_method_results("Position", pos_results)

        # Rotation validation results
        print(f"\nRotation Validation (Voting System: {rot_results['methods_passed']}/3 methods passed):")
        print(f"  Rotation Result: {'PASS' if rot_pass else 'FAIL'}")

        self._print_method_results("Rotation", rot_results)

        # Robot-specific verdict
        print(f"\n{'='*60}")
        if robot_voting_pass:
            print(f"  ✓ SUCCESS: Robot {robot_idx} coordinates PASSED voting validation")
        else:
            print(f"  ✗ WARNING: Robot {robot_idx} coordinates FAILED voting validation")
            if not pos_pass:
                print(f"    - Position validation failed ({pos_results['methods_passed']}/3 methods passed)")
            if not rot_pass:
                print(f"    - Rotation validation failed ({rot_results['methods_passed']}/3 methods passed)")
        print(f"{'='*60}")

    def _print_method_results(self, coord_type: str, results: Dict) -> None:
        """Print results for individual validation methods.

        Args:
            param coord_type: Type of coordinate being validated (Position or Rotation).
            param results: Dictionary containing validation results from all methods.
        """
        # 5% Tolerance Method
        tolerance_result = results["tolerance_method"]
        print(f"  Method 1 - 5% Tolerance: {'PASS' if tolerance_result['passed'] else 'FAIL'}")
        exceedance = tolerance_result["exceedance_percentages"]
        if coord_type == "Position":
            print(f"    Exceedance %: [X: {exceedance[0]:.2f}%, Y: {exceedance[1]:.2f}%, Z: {exceedance[2]:.2f}%]")
        else:  # Rotation
            print(
                f"    Exceedance %: [X: {exceedance[0]:.2f}%, Y: {exceedance[1]:.2f}%, Z: {exceedance[2]:.2f}%, W: {exceedance[3]:.2f}%]"
            )

        # 3-Sigma Method
        sigma_result = results["three_sigma_method"]
        print(f"  Method 2 - 3-Sigma: {'PASS' if sigma_result['passed'] else 'FAIL'}")
        if sigma_result["statistics"]:
            for comp, stats in sigma_result["statistics"].items():
                outlier_status = "OUTLIER" if stats["is_outlier"] else "OK"
                print(
                    f"    {comp}: z-score={stats['z_score']:.3f}, mean={stats['mean']:.6f}, std={stats['std']:.6f} [{outlier_status}]"
                )

        # IQR Method
        iqr_result = results["iqr_method"]
        print(f"  Method 3 - IQR: {'PASS' if iqr_result['passed'] else 'FAIL'}")
        if iqr_result["statistics"]:
            for comp, stats in iqr_result["statistics"].items():
                outlier_status = "OUTLIER" if stats["is_outlier"] else "OK"
                print(
                    f"    {comp}: bounds=[{stats['lower_bound']:.6f}, {stats['upper_bound']:.6f}], distance={stats['outlier_distance']:.6f} [{outlier_status}]"
                )
