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
import copy
import json
import os
import shutil
import tempfile
import typing
from datetime import datetime as dt
from pathlib import Path
from typing import Optional

import carb
import omni.kit.app
import toml
from isaacsim.core.version import get_version

from .. import utils
from ..execution import TestExecutionEnvironmentInterface
from . import measurements


class MetricsBackendInterface:
    def add_metrics(self, test_phase: measurements.TestPhase) -> None:
        """
        accumulate metrics
        """
        pass

    def finalize(self, metrics_output_folder: str, randomize_filename_prefix: bool = False, **kwargs) -> None:
        """
        write the data to file and clear
        """
        pass


class KitGenericTelemetry(MetricsBackendInterface):
    """
    This uses the Kit Telemetry System to store metrics, which end up in Kratos
    """

    def __init__(self) -> None:
        """Manage privacy.toml required for Kit telemetry if running on TeamCity or ETM."""
        config_dir: Path = Path.home() / ".nvidia-omniverse" / "config"
        privacy_toml_path: str = str(config_dir / "privacy.toml")

        # Remove privacy.toml if it exists.
        try:
            shutil.rmtree(config_dir)
            carb.log_info("Config folder with privacy.toml removed.")
        except Exception:
            carb.log_info("Config folder empty.")

        # Creates directory for privacy.toml.
        if not os.path.exists(config_dir):
            carb.log_info(f"Creating dir for privacy.toml {config_dir}.")
            os.makedirs(config_dir)

        # Create privacy.toml.
        carb.log_info("Creating privacy.toml.")
        data = {
            "privacy": {
                "performance": True,
                "personalization": True,
                "usage": True,
                "userId": "perflab1",
                "extraDiagnosticDataOptIn": "externalBuilds",  # Kit 103
                "nvDiagnosticDataOptIn": "externalBuilds",  # Kit 102
                "eula": {"version": "2.0"},
                "gdpr": {"version": "1.0"},
            }
        }
        with open(privacy_toml_path, "w") as toml_file:
            toml.dump(data, toml_file)

    def add_metrics(self, test_phase: measurements.TestPhase):
        event_type = ("omni.kit.tests.benchmark@run_benchmark-dev",)
        # TOOD: this needs to be rewritten if we ever want to use it
        omni.kit.app.send_telemetry_event(
            event_type=event_type, duration=0.0, data1="", data2=1, value1=0.0, value2=0.0
        )


class LocalLogMetrics(MetricsBackendInterface):
    """
    Just carb.log_info to console
    """

    def add_metrics(self, test_phase: measurements.TestPhase):
        carb.log_info(f"LocalLogMetricsEvent::add_metrics {test_phase}")


class JSONFileMetrics(MetricsBackendInterface):
    """
    Dump to a file at the end of session - just for local validation
    """

    metrics_to_upload_to_teamcity = ["Stage Load Time", "Stage FPS", "Stage DSSIM"]

    def __init__(self, execution_environment: Optional[TestExecutionEnvironmentInterface] = None):
        self._execution_environment = execution_environment
        self.data = []
        self.test_name = ""

    def add_metrics(self, test_phase: measurements.TestPhase) -> None:

        self.data.append(copy.deepcopy(test_phase))

        # Lets upload a subset of metrics to our execution environment (e.g TC).
        # In TC this shows up as metadata on the test phase
        # This should not be hardcoded though as it is below
        if self._execution_environment:
            exec_metrics = {}
            test_name = test_phase.get_metadata_field("workflow_name")
            for m in test_phase.measurements:
                measurement = typing.cast(measurements.SingleMeasurement, m)
                if measurement.name in self.metrics_to_upload_to_teamcity:
                    full_name = test_name + " " + measurement.name
                    exec_metrics[full_name] = measurement.value

            self._execution_environment.add_metrics(test_name, exec_metrics)

    def finalize(self, metrics_output_folder: str, randomize_filename_prefix: bool = False) -> None:

        # Append test name to measurement name as OVAT needs to uniquely identify
        for test_phase in self.data:
            test_name = test_phase.get_metadata_field("workflow_name")
            # Store the test name
            if test_name != self.test_name:
                if self.test_name:
                    carb.log_warn(
                        f"Nonempty test name {self.test_name} different from name {test_name} provided by test phase."
                    )
                self.test_name = test_name
                carb.log_info(f"Setting test name to {self.test_name}")

            phase_name = test_phase.get_metadata_field("phase")
            for m in test_phase.measurements:
                m.name = f"{test_name} {phase_name} {m.name}"

            for m in test_phase.metadata:
                m.name = f"{test_name} {phase_name} {m.name}"

        json_data = json.dumps(self.data, indent=4, cls=measurements.TestPhaseEncoder)

        # Generate the output filename
        if randomize_filename_prefix:
            _, metrics_filename_out = tempfile.mkstemp(
                dir=metrics_output_folder, prefix=f"metrics_{self.test_name}", suffix=".json"
            )
        else:
            metrics_filename_out = Path(metrics_output_folder) / f"metrics_{self.test_name}.json"

        with open(metrics_filename_out, "w") as f:
            carb.log_info(f"Writing metrics to {metrics_filename_out}")
            f.write(json_data)

        self.data.clear()


class OsmoKPIFile(MetricsBackendInterface):
    """
    Print metrics into a document for each phase. Only prints SingleMeasurement metrics and metadata as single key-value
    pairs.
    """

    def __init__(self, execution_environment: Optional[TestExecutionEnvironmentInterface] = None):
        self._execution_environment = execution_environment
        self._test_phases = []

    def add_metrics(self, test_phase: measurements.TestPhase) -> None:
        """Adds provided test_phase to internal list of test_phases.

        Args:
            test_phase (measurements.TestPhase): Current test phase.
        """
        self._test_phases.append(test_phase)

    def finalize(self, metrics_output_folder: str, randomize_filename_prefix: bool = False) -> None:
        """Write metrics to output file(s).

        Each test phase's SingleMeasurement metrics and metadata are written to an output JSON file, at path
        `[metrics_output_folder]/[optional random prefix]kpis_{test_name}_{test_phase}.json`.

        Args:
            metrics_output_folder (str): Output folder in which metrics files will be stored.
            randomize_filename_prefix (bool, optional): True to randomize filename prefix. Defaults to False.
        """
        for test_phase in self._test_phases:
            # Retrieve useful metadata from test_phase
            test_name = test_phase.get_metadata_field("workflow_name")
            phase_name = test_phase.get_metadata_field("phase")

            osmo_kpis = {}
            log_statements = [f"{phase_name} KPIs:"]
            # Add metadata as KPIs
            for metadata in test_phase.metadata:
                osmo_kpis[metadata.name] = metadata.data
                log_statements.append(f"{metadata.name}: {metadata.data}")
            # Add single measurements as KPIs
            for measurement in test_phase.measurements:
                if isinstance(measurement, measurements.SingleMeasurement):
                    osmo_kpis[measurement.name] = measurement.value
                    log_statements.append(f"{measurement.name}: {measurement.value} {measurement.unit}")
            # Log all KPIs to console
            carb.log_info("\n" + "\n".join(log_statements))
            # Generate the output filename
            if randomize_filename_prefix:
                _, metrics_filename_out = tempfile.mkstemp(
                    dir=metrics_output_folder, prefix=f"kpis_{test_name}_{phase_name}", suffix=".json"
                )
            else:
                metrics_filename_out = Path(metrics_output_folder) / f"kpis_{test_name}_{phase_name}.json"
            # Dump key-value pairs (fields) to the JSON document
            json_data = json.dumps(osmo_kpis, indent=4)
            with open(metrics_filename_out, "w") as f:
                carb.log_info(f"Writing KPIs to {metrics_filename_out}")
                f.write(json_data)


class OmniPerfKPIFile(MetricsBackendInterface):
    """
    Prints metrics into a document for upload to PostgreSQL database.
    """

    def __init__(self, execution_environment: Optional[TestExecutionEnvironmentInterface] = None):
        self._execution_environment = execution_environment
        self._test_phases = []

    def add_metrics(self, test_phase: measurements.TestPhase) -> None:
        """Adds provided test_phase to internal list of test_phases.

        Args:
            test_phase (measurements.TestPhase): Current test phase.
        """
        self._test_phases.append(test_phase)

    def finalize(self, metrics_output_folder: str, randomize_filename_prefix: bool = False) -> None:
        """Write metrics to output file(s).

        Measurement metrics and metadata are written to an output JSON file, at path
        `[metrics_output_folder]/[optional random prefix]kpis_{test_name}.json`.

        Args:
            metrics_output_folder (str): Output folder in which metrics file will be stored.
            randomize_filename_prefix (bool, optional): True to randomize filename prefix. Defaults to False.
        """
        workflow_data = {}
        app_version = get_version()
        workflow_data["App Info"] = [app_version[0], app_version[1], app_version[-1]]
        workflow_data["timestamp"] = dt.now().isoformat()

        workflow_data["Kit"] = utils.get_kit_version_branch()[2]  # get kit version

        for test_phase in self._test_phases:
            # Retrieve useful metadata from test_phase
            test_name = test_phase.get_metadata_field("workflow_name")
            phase_name = test_phase.get_metadata_field("phase")

            phase_data = {}
            log_statements = [f"{phase_name} Metrics:"]
            # Add metadata as metrics
            for metadata in test_phase.metadata:
                phase_data[metadata.name] = metadata.data
                log_statements.append(f"{metadata.name}: {metadata.data}")
            # Add measurements as metrics
            for measurement in test_phase.measurements:
                if isinstance(measurement, measurements.SingleMeasurement):
                    log_statements.append(f"{measurement.name}: {measurement.value} {measurement.unit}")
                    phase_data[measurement.name] = measurement.value
            # Log all metrics to console
            carb.log_info("\n" + "\n".join(log_statements))

            workflow_data[phase_name] = phase_data

        # Generate the output filename
        if randomize_filename_prefix:
            _, metrics_filename_out = tempfile.mkstemp(
                dir=metrics_output_folder, prefix=f"kpis_{test_name}", suffix=".json"
            )
        else:
            metrics_filename_out = Path(metrics_output_folder) / f"kpis_{test_name}.json"
        # Dump key-value pairs (fields) to the JSON document
        json_data = json.dumps(workflow_data, indent=4)
        with open(metrics_filename_out, "w") as f:
            carb.log_info(f"Writing metrics to {metrics_filename_out}")
            f.write(json_data)


class MetricsBackend:
    """
    Note the OVATMetrics is handled by a post process that takes the files generated by JSONFileMetricsEvent
    and gathers and updates them
    """

    @classmethod
    def get_instance(
        cls,
        execution_environment: Optional[TestExecutionEnvironmentInterface] = None,
        instance_type: Optional[str] = None,
    ) -> MetricsBackendInterface:
        """Return instance."""
        if instance_type == "KitGenericTelemetry":
            return KitGenericTelemetry()
        elif instance_type == "LocalLogMetrics":
            return LocalLogMetrics()
        elif instance_type == "JSONFileMetrics":
            return JSONFileMetrics()
        elif instance_type == "OsmoKPIFile":
            return OsmoKPIFile()
        elif instance_type == "OmniPerfKPIFile":
            return OmniPerfKPIFile()
        else:
            if bool(os.getenv("TEAMCITY_VERSION")) or bool(os.getenv("ETM_ACTIVE")):
                return JSONFileMetrics(execution_environment)
            else:
                return JSONFileMetrics(execution_environment)
