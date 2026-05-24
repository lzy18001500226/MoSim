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
from .. import utils
from . import measurements

# List of other "metadata" metrics to be filtered out of each phase
additional_metadata = ["num_cpus", "gpu_device_name"]
# List of metrics to remove from the summary report
default_exclusions = [
    "System CPU iowait",
    "System CPU system",
    "System CPU user",
    "System CPU idle",
    "GPU Memory Dedicated",
]


class Report:
    def __init__(self):
        self._test_phases = []
        self._phase_data = []
        self._addt_metadata = []
        self._report_width = 50  # char width
        self._frametime_metrics = {}

    def add_metric_phase(self, test_phase: measurements.TestPhase) -> None:
        """
        Adds provided test_phase to internal list of test_phases. Adds formatted lines
            matching to given phase as key-value pairs.

        Args:
            test_phase (measurements.TestPhase): Current test phase.
        """
        self._test_phases.append(test_phase)
        formatted_lines = self.process_phase(test_phase)
        self._phase_data.append({test_phase.get_metadata_field("phase"): formatted_lines})

    def process_phase(self, test_phase):
        """
        Processes metric data for given phase into formatted strings.

        Args:
            test_phase (measurements.TestPhase): Current test phase.
        Returns:
            List of formatted strings containing metric data for given phase
        """
        logs = []
        phase_name = f"Phase: {test_phase.get_metadata_field('phase')}"
        logs.append(f"| {phase_name:<{self._report_width}} |")

        for measurement in test_phase.measurements:
            if isinstance(measurement, measurements.SingleMeasurement):
                if measurement.name in additional_metadata:
                    self._add_metadata(measurement)
                elif measurement.name not in default_exclusions:
                    if "frametime" in measurement.name.lower():
                        self._process_frametime_metric(measurement)
                    else:
                        logs.append(self._format_measurement(measurement))

        if self._frametime_metrics:
            logs.extend(self.get_frametime_metrics())
            self._frametime_metrics.clear()

        return logs

    def _format_measurement(self, measurement):
        """
        Create formatted line from measurement object.

        Args:
            measurement (measurements.SingleMeasurement): Measurement object.
        Returns:
            Formatted string containing metric data
        """
        line = f"{measurement.name}: {measurement.value} {measurement.unit}"
        return f"| {line:<{self._report_width}} |"

    def _add_metadata(self, measurement):
        """
        Adds measurement to metadata list. Metadata list is only printed out
        once instead of per phase.
        """
        metadata = f"{measurement.name}: {measurement.value} {measurement.unit}"
        if metadata not in self._addt_metadata:
            self._addt_metadata.append(metadata)

    def _process_frametime_metric(self, measurement):
        """
        Generates table containing frametime data organized by type.

        Args:
            measurement (str): measurement data
        """
        metric_type = measurement.name.split(" ")[0]  # min/max/mean/stddev
        frametime = measurement.name.split(" ")[1]  # render/physics/gpu
        if frametime not in self._frametime_metrics:
            self._frametime_metrics[frametime] = {}
        self._frametime_metrics[frametime][metric_type] = f"{measurement.value:.2f}"

    def print_formatted_lines(self, phase):
        """
        Prints formatted metric data to log by phase.

        Args:
            phase (dict): Current measurement phase
        """
        for key, value in phase.items():
            for line in value:
                print(line)

    def add_separator(self):
        """
        Adds dashed line to separate report sections.
        """
        separator = "|" + "-" * (self._report_width + 2) + "|"
        return separator

    def print_metadata(self):
        """
        Prints formatted metadata for the benchmark to log.
        """
        for metadata in self._test_phases[0].metadata[:-1]:
            formatted = f"{metadata.name}: {metadata.data}"
            print(f"| {formatted:<{self._report_width}} |")
        for data in self._addt_metadata:
            print(f"| {data:<{self._report_width}} |")

    def get_frametime_metrics(self):
        """
        Formats frametime metric data in a table format
        """
        logs = []
        label = f"{'Frametimes (ms):':<12}{'mean':>8} | {'stdev':>6} | {'min':>5} | {'max':>5}"
        logs.append(f"| {label:<{self._report_width}} |")
        for thread, metrics in self._frametime_metrics.items():
            mean = metrics.get("Mean", "-")
            stddev = metrics.get("Stdev", "-")
            min_val = metrics.get("Min", "-")
            max_val = metrics.get("Max", "-")
            line = f"{thread:<16}{mean:>8} | {stddev:>6} | {min_val:>5} | {max_val:>5}"
            logs.append(f"| {line:<{self._report_width}} |")
        return logs

    def create_report(self):
        """
        Prints final report structure/data to log separated by phases.
        """
        print(self.add_separator())
        title = "Summary Report"
        print(f"| {title:^{self._report_width}} |")
        print(self.add_separator())
        self.print_metadata()
        for phase in self._phase_data:
            print(self.add_separator())
            self.print_formatted_lines(phase)
        print(self.add_separator())
