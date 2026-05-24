# SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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
import tempfile
from pathlib import Path
from shutil import copy, copytree, rmtree
from typing import Dict, List, Optional, Tuple

import carb

from .utils import get_calling_test_id


def print_info_log(str):
    carb.log_info(str)


class TestExecutionEnvironmentInterface:
    @classmethod
    def upload_artefact(cls, artefact_filepath: str, key: str):
        """
        key can be something like "golden", "diff" etc
        """
        pass

    @classmethod
    def add_metrics(cls, test_phase: str, metrics: Dict):
        pass

    """
    actions that we would normally call in e.g unittest.setupClass
    """

    def store_shader_cache_contents(self):
        """
        call to store the list of shader cache files which exist before a test is
        run
        """
        pass

    """
    actions that we would normally call in unittest.teardownClass
    """

    def delete_recent_shaders(self):
        """
        delete everything that's not in the initial shader cache - i.e delete any shader
        files that were created by the test we just ran
        """
        pass


def get_cache_paths() -> List[Tuple[str, str]]:
    def get_cache_path(setting_name) -> Optional[str]:
        settings = carb.settings.get_settings()
        cache_path = settings.get(setting_name)
        if cache_path:
            # It's possible? that a cache path doesn't exist at the start of the first run
            # let's look at the logging and see how often this happens in practice if at all
            if os.path.exists(cache_path):
                return cache_path
            else:
                carb.log_warn(f"get_cache_paths: Cache path {cache_path} doesn't exist - won't track")
        return None

    cache_path_list = [
        (get_cache_path("/rtx/shaderDb/shaderCachePath"), "shader_cache"),
        (get_cache_path("/rtx/shaderDb/driverShaderCachePath"), "driver_shader_cache"),
        (get_cache_path("/rtx-transient/resourcemanager/localTextureCachePath"), "texture_cache"),
    ]

    return [(c, l) for c, l in cache_path_list if c]


class LocalExecutionEnvironment(TestExecutionEnvironmentInterface):
    def __init__(self):
        self.tmp_dir = tempfile.mkdtemp()
        self._shader_cache_tracker = None
        self._texture_cache_tracker = None

    def upload_artefact(self, artefact_filepath, key: str):
        # TODO: Validate this
        # TODO: Write a text file containing key->filepath
        copy(artefact_filepath, self.tmp_dir)

        test_id = get_calling_test_id()
        print_info_log(
            f"LocalExecutionEnvironment copied '{artefact_filepath} => {self.tmp_dir} {key}' for test {test_id}"
        )

    def add_metrics(self, test_phase: str, metrics: Dict):
        test_id = get_calling_test_id()
        print_info_log(f"LocalExecutionEnvironment add_metrics '{test_phase} => {metrics}")

    def store_shader_cache_contents(self):

        cache_tracker_paths = get_cache_paths()
        self.cache_trackers = [
            KitCacheTrackerDeleter(Path(cache_path), label) for cache_path, label in cache_tracker_paths
        ]

    def delete_recent_shaders(self):
        for ct in self.cache_trackers:
            ct.delete_added_files(dry_run=True)


class TestExecutionEnvironment:
    """
    Factory/Creator type class that tries to guess what Execution Environment you're in
    and return the appropriate Class
    Having an abstracted Execution Environment allows you to to different things e.g startup/teardown depending
    on where you are running..
    """

    instances = {}

    @classmethod
    def get_instance(cls) -> TestExecutionEnvironmentInterface:
        return cls.instances.setdefault("local", LocalExecutionEnvironment())
