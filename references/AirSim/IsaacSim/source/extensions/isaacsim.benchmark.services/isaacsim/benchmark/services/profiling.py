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
import gzip
import os
import shutil

import carb

from . import utils


async def convert_chrome_to_tracy(json_path: str, tracy_path: str) -> str:
    """Convert CPU trace JSON file to Tracy format."""
    from omni.kit.profiler.tracy import tracy

    # Convert JSON to Tracy.
    carb.log_info(f"Converting {json_path} to {tracy_path}")
    tracy.convert_json_to_tracy(json_path, tracy_path)

    # If there was a problem with tracy, just return the original file
    if not os.path.exists(tracy_path):
        carb.log_warn(f"Unable to create tracy file for {json_path}...")
        return json_path

    # Compress file.
    with open(tracy_path, "rb") as f_in:
        with gzip.open(tracy_path + ".gz", "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    return tracy_path + ".gz"
