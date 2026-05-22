# SPDX-FileCopyrightText: Copyright (c) 2020-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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


import omni
import omni.replicator.core as rep
from isaacsim.core.utils.prims import set_targets


def set_target_prims(primPath: str, targetPrimPaths: list, inputName: str = "inputs:targetPrim"):
    stage = omni.usd.get_context().get_stage()
    try:
        set_targets(stage.GetPrimAtPath(primPath), inputName, targetPrimPaths)
    except Exception as e:
        print(e, primPath)


def register_node_writer_with_telemetry(*args, **kwargs):
    rep.writers.register_node_writer(*args, **kwargs)
    # Register writer for Replicator telemetry tracking
    if kwargs["name"] not in rep.WriterRegistry._default_writers:
        rep.WriterRegistry._default_writers.append(kwargs["name"])


def register_annotator_from_node_with_telemetry(*args, **kwargs):
    rep.AnnotatorRegistry.register_annotator_from_node(*args, **kwargs)
    # Register annotator for Replicator telemetry tracking
    if kwargs["name"] not in rep.AnnotatorRegistry._default_annotators:
        rep.AnnotatorRegistry._default_annotators.append(kwargs["name"])
