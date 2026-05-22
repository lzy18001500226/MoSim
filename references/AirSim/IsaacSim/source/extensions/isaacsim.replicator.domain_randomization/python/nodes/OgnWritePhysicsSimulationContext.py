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

import carb
import numpy as np
import omni.graph.core as og
import torch
from isaacsim.replicator.domain_randomization import SIMULATION_CONTEXT_ATTRIBUTES
from isaacsim.replicator.domain_randomization import physics_view as physics

OPERATION_TYPES = ["direct", "additive", "scaling"]


def apply_randomization_operation(operation, attribute_name, samples, on_reset):
    if on_reset:
        return physics._simulation_context_reset_values[attribute_name]
    if operation == "additive":
        return physics._simulation_context_reset_values[attribute_name] + samples
    elif operation == "scaling":
        return physics._simulation_context_reset_values[attribute_name] * samples
    else:
        return samples


def modify_initial_values(operation, attribute_name, samples):
    if operation == "additive":
        physics._simulation_context_reset_values[attribute_name] = (
            physics._simulation_context_initial_values[attribute_name] + samples
        )
    elif operation == "scaling":
        physics._simulation_context_reset_values[attribute_name] = (
            physics._simulation_context_initial_values[attribute_name] * samples
        )
    else:
        physics._simulation_context_reset_values[attribute_name] = samples


class OgnWritePhysicsSimulationContext:
    @staticmethod
    def compute(db) -> bool:
        view_name = db.inputs.prims
        attribute_name = db.inputs.attribute
        operation = db.inputs.operation
        values = db.inputs.values
        if db.inputs.indices is None or len(db.inputs.indices) == 0:
            db.outputs.execOut = og.ExecutionAttributeState.ENABLED
            return False
        indices = np.array(db.inputs.indices)
        on_reset = db.inputs.on_reset

        try:
            simulation_context = physics._simulation_context
            if simulation_context is None:
                raise ValueError(f"Expected a registered simulation_context")
            if attribute_name not in SIMULATION_CONTEXT_ATTRIBUTES:
                raise ValueError(
                    f"Expected an attribute in {SIMULATION_CONTEXT_ATTRIBUTES}, but instead received {attribute_name}"
                )
            if operation not in OPERATION_TYPES:
                raise ValueError(f"Expected an operation type in {OPERATION_TYPES}, but instead received {operation}")

            samples = np.array(values).reshape(len(indices), -1)[0]
        except Exception as error:
            db.log_error(f"WritePhysics Error: {error}")
            db.outputs.execOut = og.ExecutionAttributeState.DISABLED
            return False

        if on_reset:
            modify_initial_values(operation, attribute_name, samples)

        if attribute_name == "gravity":
            gravity = apply_randomization_operation(operation, attribute_name, samples, on_reset)
            simulation_context.physics_sim_view.set_gravity(carb.Float3(gravity[0], gravity[1], gravity[2]))

        db.outputs.execOut = og.ExecutionAttributeState.ENABLED
        return True
