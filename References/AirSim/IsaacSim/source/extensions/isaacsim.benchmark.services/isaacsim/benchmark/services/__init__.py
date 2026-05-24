# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

import builtins

if hasattr(builtins, "ISAAC_LAUNCHED_FROM_TERMINAL") and builtins.ISAAC_LAUNCHED_FROM_TERMINAL is False:
    # ISAAC_LAUNCHED_FROM_TERMINAL is set to False by SimulationApp, so this will be triggered by standalone Python
    # workflows only
    from .base_isaac_benchmark import BaseIsaacBenchmark
if (hasattr(builtins, "ISAAC_LAUNCHED_FROM_TERMINAL") and builtins.ISAAC_LAUNCHED_FROM_TERMINAL is True) or not hasattr(
    builtins, "ISAAC_LAUNCHED_FROM_TERMINAL"
):
    # This will be triggered if running from an async workflow (non-standalone)
    from .base_isaac_benchmark_async import BaseIsaacBenchmarkAsync
