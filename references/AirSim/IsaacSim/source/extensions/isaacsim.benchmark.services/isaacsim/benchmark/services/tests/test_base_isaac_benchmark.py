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
import omni
from isaacsim.benchmark.services import BaseIsaacBenchmarkAsync
from isaacsim.benchmark.services.metrics.measurements import (
    BooleanMeasurement,
    DictMeasurement,
    ListMeasurement,
    SingleMeasurement,
)
from isaacsim.core.api import SimulationContext


class TestBaseIsaacBenchmarkAsync(BaseIsaacBenchmarkAsync):
    async def setUp(self):
        await omni.usd.get_context().new_stage_async()
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        await super().setUp(backend_type="LocalLogMetrics")
        pass

    async def tearDown(self):
        await super().tearDown()
        pass

    async def test_base_isaac_benchmark(self):
        self.benchmark_name = "test_base_isaac_benchmark"
        self.set_phase("loading", False, True)
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        simulation_context = SimulationContext()
        await simulation_context.initialize_simulation_context_async()
        await self.store_measurements()
        simulation_context.play()

        self.set_phase("benchmark")
        for frame in range(10):
            await omni.kit.app.get_app().next_update_async()
        await self.store_measurements()

    async def test_store_custom_measurement(self):
        self.benchmark_name = "test_custom_measurements"
        self.set_phase("loading", False, True)
        await omni.kit.app.get_app().next_update_async()
        await omni.kit.app.get_app().next_update_async()
        simulation_context = SimulationContext()
        await simulation_context.initialize_simulation_context_async()
        await self.store_measurements()
        simulation_context.play()
        await omni.kit.app.get_app().next_update_async()

        # Store different types of measurements
        measurement = BooleanMeasurement(name="bool_measure", bvalue=True)
        await self.store_custom_measurement("phase_1", measurement)

        measurement = SingleMeasurement(name="single_measure_1", value=1.23, unit="ms")
        await self.store_custom_measurement("phase_1", measurement)

        measurement = DictMeasurement(name="dict_measure", value={"key": "value"})
        await self.store_custom_measurement("phase_2", measurement)

        measurement = SingleMeasurement(name="single_measure_2", value=4.56, unit="ms")
        await self.store_custom_measurement("phase_3", measurement)

        measurement = ListMeasurement(name="list_measure", value=[1, 2, 3])
        await self.store_custom_measurement("phase_4", measurement)
        await omni.kit.app.get_app().next_update_async()
