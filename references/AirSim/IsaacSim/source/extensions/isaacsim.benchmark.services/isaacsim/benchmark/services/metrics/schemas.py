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
from dataclasses import dataclass
from typing import Any, List

import omni.kit.app


@dataclass
class OSConfiguration:
    platform: str
    os: str
    os_major: str
    architecture: str  # 64bit


@dataclass
class GPU:
    number: int
    gpu_id: str
    product_architecture: str
    product_brand: str
    product_name: str


@dataclass
class GPUConfiguration:
    cuda_version: float
    driver_version: str
    gpus: List[GPU]
    primary_gpu: GPU
    num_gpus: int


@dataclass
class CPUConfiguration:
    model: str


@dataclass
class MemoryConfiguration:
    ram_gb: float


@dataclass
class HardwareConfiguration:
    gpu_configuration: GPUConfiguration
    cpu_configuration: CPUConfiguration
    memory_configuration: MemoryConfiguration


@dataclass
class Application:
    name: str
    name_full: str
    kit_file: str
    version_minor: str
    version_major_minor_patch: str
    version_full: str
    build_id: str
    kit_version_minor: str
    kit_version_patch: str
    kit_build_id: str
    package_name: str
    package_full: str
    build_date: int


@dataclass
class ExecutionEnvironment:
    primary_system: str
    primary_id: str
    primary_url: str
    secondary_system: str
    secondary_id: str
    secondary_url: str
    extension_identifier: str
    etm_identifier: str
    input_build_url: str
    input_build_id: str
    hostname: str


@dataclass
class BenchmarkIdentifier:
    run_uuid: str


@dataclass
class Benchmark:
    name: str
    asset_url: str
    version_identifier: str
    checkpoint: int
    dssim_status: bool
    dssim: float
    resolution: str


@dataclass
class Metric:
    name: str
    value: Any


@dataclass
class BenchData:
    ts_created: int
    test_name: str
    schema: str
    hardware_configuration: HardwareConfiguration
    os_configuration: OSConfiguration
    application: Application
    execution_environment: ExecutionEnvironment
    benchmark_identifier: BenchmarkIdentifier
    benchmark: Benchmark
    metric: Metric

    def get_fingerprint(self) -> str:
        """Get session hash."""
        import hashlib

        params = {
            "name": self.application.name,
            "version_minor": self.application.version_minor,
            "kit_version_minor": self.application.kit_version_minor,
            "platform": self.os_configuration.platform,
            "os": self.os_configuration.os,
            "architecture": self.os_configuration.architecture,
            "cpu": self.hardware_configuration.cpu_configuration.model,
            "gpu": self.hardware_configuration.gpu_configuration.primary_gpu.product_name,
            "driver": str(self.hardware_configuration.gpu_configuration.driver_version),
            "cuda": self.hardware_configuration.gpu_configuration.cuda_version,
            "python": omni.kit.app.get_app().get_platform_info()["python_version"],
        }

        h = hashlib.sha256(json.dumps(params, sort_keys=True).encode("utf-8")).hexdigest()[:8]
        return h
