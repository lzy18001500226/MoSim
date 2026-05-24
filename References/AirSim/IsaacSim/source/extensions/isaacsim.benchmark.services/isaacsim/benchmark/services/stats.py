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
from typing import Dict


class OmniStats:
    def get_stats(self) -> Dict:
        scopes_dict = {}
        for scope in self._scopes:
            stats = self._stats_if.get_stats(scope["scopeId"])
            stats_dict = {}
            for x in stats:
                name = x["name"].replace(" - ", "_")
                name = name.replace(" ", "_")
                stats_dict[name] = x["value"]
            scopes_dict[scope["name"]] = stats_dict
        return scopes_dict
