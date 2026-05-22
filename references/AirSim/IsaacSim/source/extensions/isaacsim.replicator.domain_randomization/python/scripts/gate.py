# SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

from omni.replicator.core.utils import ReplicatorItem, ReplicatorWrapper, create_node


@ReplicatorWrapper
def on_interval(interval):
    """
    Args:
        interval (int): The frequency interval for randomization. The interval is incremented
                        by isaacsim.replicator.domain_randomization.physics_view.step_randomization() call.
    """
    node = create_node("isaacsim.replicator.domain_randomization.OgnIntervalFiltering")
    trigger_node = ReplicatorItem._get_context()

    node.get_attribute("inputs:interval").set(interval)
    trigger_node.get_attribute("outputs:execOut").connect(node.get_attribute("inputs:execIn"), True)
    trigger_node.get_attribute("outputs:frameNum").connect(node.get_attribute("inputs:frameCounts"), True)

    return node


@ReplicatorWrapper
def on_env_reset():
    node = create_node("isaacsim.replicator.domain_randomization.OgnIntervalFiltering")
    trigger_node = ReplicatorItem._get_context()

    node.get_attribute("inputs:ignoreInterval").set(True)
    trigger_node.get_attribute("outputs:execOut").connect(node.get_attribute("inputs:execIn"), True)
    trigger_node.get_attribute("outputs:resetInds").connect(node.get_attribute("inputs:indices"), True)

    return node
