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
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, Tuple, Type, Union

from ..metrics.measurements import Measurement, MetadataBase

if TYPE_CHECKING:
    from ..settings import BenchmarkSettings


@dataclass
class MeasurementData:
    """
    This is the return type for the MeasurementDataRecorder get_data() method
    """

    measurements: List[Measurement] = field(default_factory=lambda: [])
    metadata: List[MetadataBase] = field(default_factory=lambda: [])
    artefacts: List[Tuple[Path, str]] = field(default_factory=lambda: [])  # (path, artefact-label)


@dataclass
class InputContext:
    """
    this is the miscellaneous input data required by recorders to operate
    """

    artifact_prefix: str = ""
    kit_version: str = ""
    phase: str = ""


class MeasurementDataRecorder:
    """
    Interface/Base class for recording metrics, metadata and filed based artifacts, there are 2 basic use cases:
    1. things we measure at a specific point in time, and don't require accumulation over a period
    2. measurements like profilers or other sampling-based systems that gather data over a time period

    It's mostly up to the call site to work out when/where each recorder starts. For classes that gather data, the gathering
    normally starts from when the class is initialized
    """

    def __init__(
        self,
        context: Optional[InputContext] = None,
        root_dir: Optional[Path] = None,
        benchmark_settings: Optional["BenchmarkSettings"] = None,
    ):
        """
        Note that although the arguments are optional here, they may not be in a derived class
        """
        pass

    def get_data(self) -> MeasurementData:
        return MeasurementData()


class MeasurementDataRecorderRegistry:

    name_to_class = {}

    @classmethod
    def add(cls, name: str, recorder: Type[MeasurementDataRecorder]) -> None:
        cls.name_to_class[name] = recorder

    @classmethod
    def get(cls, name: str) -> Union[Type[MeasurementDataRecorder], None]:
        return cls.name_to_class.get(name)

    @classmethod
    def get_many(cls, names: List[str]) -> List[Type[MeasurementDataRecorder]]:
        classes = [cls.get(x) for x in names]
        return [c for c in classes if c is not None]
