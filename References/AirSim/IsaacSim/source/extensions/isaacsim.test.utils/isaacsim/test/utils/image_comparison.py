# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

import os

import numpy as np
from PIL import Image


def compute_difference_metrics(
    golden_array: np.ndarray,
    test_array: np.ndarray,
    *,
    percentiles: list[float] | tuple[float, ...] = (50, 75, 90, 95, 99),
    allclose_rtol: float = 1e-05,
    allclose_atol: float = 1e-08,
    ignore_blank_pixels: bool = False,
) -> dict[str, object]:
    """Compute difference metrics between two image arrays.

    Computes a reusable set of metrics for image comparison, including ``np.allclose``
    with the provided tolerances, mean and max absolute differences, RMSE, and a set
    of requested percentiles of absolute differences.

    Args:
        param golden_array: Reference image array.
        param test_array: Test image array to compare.
        param percentiles: Sequence of percentiles to compute for absolute differences.
        param allclose_rtol: Relative tolerance for the allclose metric.
        param allclose_atol: Absolute tolerance for the allclose metric.
        param ignore_blank_pixels: If True, ignore blank pixels in the comparison.

    Returns:
        A dictionary containing the computed metrics: ``allclose``, ``rtol``, ``atol``,
        ``mean_abs``, ``max_abs``, ``rmse``, and ``percentiles`` (a mapping from percentile
        to value).

    Raises:
        ValueError: If image shapes do not match.

    Example:

    .. code-block:: python

        >>> import numpy as np
        >>> from isaacsim.test.utils.image_comparison import compute_difference_metrics
        >>> a = np.zeros((2, 2), dtype=np.uint8)
        >>> b = np.zeros((2, 2), dtype=np.uint8)
        >>> metrics = compute_difference_metrics(a, b)
        >>> bool(metrics["allclose"])  # True if arrays are close with defaults
        True
    """
    if golden_array.shape != test_array.shape:
        raise ValueError(f"Image shapes do not match: golden {golden_array.shape} vs test {test_array.shape}")

    # Promote to float for numeric stability, keep NaNs to leverage equal_nan in allclose.
    golden_float = golden_array.astype(np.float64, copy=False)
    test_float = test_array.astype(np.float64, copy=False)

    # Build mask to compute stats on valid numeric entries only.
    valid_mask = np.isfinite(golden_float) & np.isfinite(test_float)
    if ignore_blank_pixels:
        valid_mask = valid_mask & (golden_float != 0) & (test_float != 0)
    if np.any(valid_mask):
        diff_vals = np.abs(golden_float[valid_mask] - test_float[valid_mask])
        rmse = float(np.sqrt(np.mean((golden_float[valid_mask] - test_float[valid_mask]) ** 2)))
        mean_diff = float(np.mean(diff_vals))
        max_diff = float(np.max(diff_vals))
    else:
        # No valid numeric elements; define neutral statistics.
        diff_vals = np.array([0.0], dtype=np.float64)
        rmse = 0.0
        mean_diff = 0.0
        max_diff = 0.0

    # Compute allclose across the full arrays (NaN == NaN when equal_nan=True).
    allclose_result = np.allclose(golden_float, test_float, rtol=allclose_rtol, atol=allclose_atol, equal_nan=True)

    # Compute requested percentiles.
    percentile_values: dict[float, float] = {}
    for p in sorted(set(percentiles)):
        percentile_values[p] = float(np.percentile(diff_vals, p))

    return {
        "allclose": bool(allclose_result),
        "rtol": float(allclose_rtol),
        "atol": float(allclose_atol),
        "mean_abs": float(mean_diff),
        "max_abs": float(max_diff),
        "rmse": float(rmse),
        "percentiles": percentile_values,
    }


def print_difference_statistics(metrics: dict[str, object]) -> None:
    """Pretty-print image difference metrics.

    Prints a stable summary of the metrics computed by ``compute_difference_metrics``.

    Args:
        param metrics: Dictionary returned by ``compute_difference_metrics``.

    Returns:
        None.

    Example:

    .. code-block:: python

        >>> import numpy as np
        >>> from isaacsim.test.utils.image_comparison import (
        ...     compute_difference_metrics, print_difference_statistics
        ... )
        >>> a = np.zeros((2, 2), dtype=np.uint8)
        >>> b = np.ones((2, 2), dtype=np.uint8)
        >>> m = compute_difference_metrics(a, b)
        >>> print_difference_statistics(m)  # doctest: +ELLIPSIS
        ...
    """
    header = "=== All metrics ==="
    print(f"\n{header}")

    print(f"Allclose (rtol={metrics['rtol']}, atol={metrics['atol']}): " f"{'PASS' if metrics['allclose'] else 'FAIL'}")
    print(f"Mean absolute difference: {metrics['mean_abs']:.3f}")
    print(f"Max absolute difference: {metrics['max_abs']:.3f}")
    print(f"Root Mean Square Error (RMSE): {metrics['rmse']:.3f}")

    for p in sorted(metrics.get("percentiles", {}).keys()):
        p_value = metrics["percentiles"][p]
        print(f"{int(p)}th percentile of differences: {p_value:.3f}")

    print("=" * len(header) + "\n")


def compare_arrays_within_tolerances(
    golden_array: np.ndarray,
    test_array: np.ndarray,
    allclose_rtol: float | None = 1e-05,
    allclose_atol: float | None = 1e-08,
    mean_tolerance: float | None = None,
    max_tolerance: float | None = None,
    absolute_tolerance: float | None = None,
    percentile_tolerance: tuple | None = None,
    rmse_tolerance: float | None = None,
    print_all_stats: bool = False,
) -> dict[str, object]:
    """Compare two image arrays against tolerance-based criteria.

    Args:
        param golden_array: Reference image array.
        param test_array: Test image array to compare.
        param allclose_rtol: Relative tolerance for np.allclose (default: 1e-05). Pass None to
            disable allclose check (requires allclose_atol=None too).
        param allclose_atol: Absolute tolerance for np.allclose (default: 1e-08). Pass None to
            disable allclose check (requires allclose_rtol=None too).
        param mean_tolerance: Maximum acceptable mean absolute difference (optional).
        param max_tolerance: Maximum acceptable max absolute difference (optional).
        param absolute_tolerance: Maximum absolute difference for any pixel (optional).
        param percentile_tolerance: Tuple of (percentile, tolerance) for percentile-based comparison (optional).
        param rmse_tolerance: Maximum acceptable root mean square error (optional).
        param print_all_stats: If True, compute and print all metrics regardless of criteria.

    Returns:
        A dictionary with keys: ``passed`` (bool), ``criteria`` (mapping of criterion
        to bool), ``metrics`` (the computed metrics), and ``thresholds`` (configured values).

    Example:

    .. code-block:: python

        >>> import numpy as np
        >>> from isaacsim.test.utils.image_comparison import compare_arrays_within_tolerances
        >>> a = np.zeros((2, 2), dtype=np.uint8)
        >>> b = np.ones((2, 2), dtype=np.uint8)
        >>> res = compare_arrays_within_tolerances(a, b, mean_tolerance=0.1)
        >>> sorted(res["criteria"].keys())  # doctest: +ELLIPSIS
        ...
    """
    if golden_array.shape != test_array.shape:
        raise ValueError(f"Image shapes do not match: golden {golden_array.shape} vs test {test_array.shape}")

    if golden_array.dtype != test_array.dtype:
        test_array = test_array.astype(golden_array.dtype)

    default_percentiles = [50, 75, 90, 95, 99]
    extra_percentiles = []
    if percentile_tolerance is not None:
        if isinstance(percentile_tolerance, (tuple, list)) and len(percentile_tolerance) == 2:
            extra_percentiles = [float(percentile_tolerance[0])]
        else:
            raise ValueError("percentile_tolerance must be a tuple of (percentile, tolerance)")
    percentiles_to_compute = sorted(set(default_percentiles + extra_percentiles))

    metrics_rtol = allclose_rtol if allclose_rtol is not None else 1e-05
    metrics_atol = allclose_atol if allclose_atol is not None else 1e-08

    metrics = compute_difference_metrics(
        golden_array=golden_array,
        test_array=test_array,
        percentiles=percentiles_to_compute,
        allclose_rtol=metrics_rtol,
        allclose_atol=metrics_atol,
    )

    criteria_results: dict[str, bool] = {}

    if not (allclose_rtol is None and allclose_atol is None):
        criteria_results["allclose"] = bool(metrics["allclose"])  # evaluated with metrics_rtol/metrics_atol

    if mean_tolerance is not None:
        criteria_results["mean"] = float(metrics["mean_abs"]) <= float(mean_tolerance)

    if max_tolerance is not None:
        criteria_results["max"] = float(metrics["max_abs"]) <= float(max_tolerance)

    if absolute_tolerance is not None:
        criteria_results["absolute"] = float(metrics["max_abs"]) <= float(absolute_tolerance)

    if percentile_tolerance is not None:
        percentile, tolerance = float(percentile_tolerance[0]), float(percentile_tolerance[1])
        percentile_value = float(metrics["percentiles"].get(float(percentile), np.nan))
        criteria_results[f"percentile_{int(percentile)}"] = percentile_value <= tolerance

    if rmse_tolerance is not None:
        criteria_results["rmse"] = float(metrics["rmse"]) <= float(rmse_tolerance)

    passed = all(criteria_results.values()) if criteria_results else True

    thresholds: dict[str, object] = {
        "rtol": float(metrics_rtol),
        "atol": float(metrics_atol),
    }
    if mean_tolerance is not None:
        thresholds["mean_tolerance"] = float(mean_tolerance)
    if max_tolerance is not None:
        thresholds["max_tolerance"] = float(max_tolerance)
    if absolute_tolerance is not None:
        thresholds["absolute_tolerance"] = float(absolute_tolerance)
    if percentile_tolerance is not None:
        thresholds["percentile_tolerance"] = (float(percentile_tolerance[0]), float(percentile_tolerance[1]))
    if rmse_tolerance is not None:
        thresholds["rmse_tolerance"] = float(rmse_tolerance)

    if print_all_stats:
        print_difference_statistics(metrics)

    return {"passed": passed, "criteria": criteria_results, "metrics": metrics, "thresholds": thresholds}


def compare_images_within_tolerances(
    golden_file_path: str,
    test_file_path: str,
    allclose_rtol: float | None = 1e-05,
    allclose_atol: float | None = 1e-08,
    mean_tolerance: float | None = None,
    max_tolerance: float | None = None,
    absolute_tolerance: float | None = None,
    percentile_tolerance: tuple | None = None,
    rmse_tolerance: float | None = None,
    print_all_stats: bool = False,
) -> dict[str, object]:
    """Compare two image files against tolerance-based criteria.

    Args:
        param golden_file_path: Path to the reference image file.
        param test_file_path: Path to the test image file to compare.
        param allclose_rtol: Relative tolerance for np.allclose (default: 1e-05). Pass None to
            disable allclose check (requires allclose_atol=None too).
        param allclose_atol: Absolute tolerance for np.allclose (default: 1e-08). Pass None to
            disable allclose check (requires allclose_rtol=None too).
        param mean_tolerance: Maximum acceptable mean absolute difference (optional).
        param max_tolerance: Maximum acceptable max absolute difference (optional).
        param absolute_tolerance: Maximum absolute difference for any pixel (optional).
        param percentile_tolerance: Tuple of (percentile, tolerance) for percentile-based comparison (optional).
        param rmse_tolerance: Maximum acceptable root mean square error (optional).
        param print_all_stats: If True, compute and print all metrics regardless of criteria.

    Returns:
        A dictionary with keys: ``passed`` (bool), ``criteria`` (mapping of criterion
        to bool), ``metrics`` (the computed metrics), and ``thresholds`` (configured values).

    Example:

    .. code-block:: python

        >>> from isaacsim.test.utils.image_comparison import compare_images_within_tolerances
        >>> res = compare_images_within_tolerances("golden.png", "test.png", mean_tolerance=1.0)
        >>> isinstance(res["passed"], bool)
        True
    """
    if not os.path.exists(golden_file_path):
        raise FileNotFoundError(f"Golden image file not found: {golden_file_path}")
    if not os.path.exists(test_file_path):
        raise FileNotFoundError(f"Test image file not found: {test_file_path}")

    golden_img = Image.open(golden_file_path)
    test_img = Image.open(test_file_path)

    golden_array = np.array(golden_img)
    test_array = np.array(test_img)

    def _squeeze_singleton_channel(arr: np.ndarray) -> np.ndarray:
        if arr.ndim == 3 and arr.shape[2] == 1:
            return arr[:, :, 0]
        return arr

    golden_array = _squeeze_singleton_channel(golden_array)
    test_array = _squeeze_singleton_channel(test_array)

    if (
        golden_array.ndim == 3
        and test_array.ndim == 3
        and golden_array.shape[0] == test_array.shape[0]
        and golden_array.shape[1] == test_array.shape[1]
        and {golden_array.shape[2], test_array.shape[2]} == {3, 4}
    ):
        if golden_array.shape[2] == 4:
            golden_array = golden_array[:, :, :3]
        if test_array.shape[2] == 4:
            test_array = test_array[:, :, :3]

    return compare_arrays_within_tolerances(
        golden_array=golden_array,
        test_array=test_array,
        allclose_rtol=allclose_rtol,
        allclose_atol=allclose_atol,
        mean_tolerance=mean_tolerance,
        max_tolerance=max_tolerance,
        absolute_tolerance=absolute_tolerance,
        percentile_tolerance=percentile_tolerance,
        rmse_tolerance=rmse_tolerance,
        print_all_stats=print_all_stats,
    )
