// SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.


#include <carb/BindingsPythonUtils.h>
#include <carb/logging/Log.h>

#include <isaacsim/core/nodes/ICoreNodes.h>

CARB_BINDINGS("isaacsim.core.nodes.python")


namespace
{

PYBIND11_MODULE(_isaacsim_core_nodes, m)
{
    // clang-format off
    using namespace carb;
    using namespace isaacsim::core::nodes;
    m.doc() = R"pbdoc(
        Isaac Sim Core Nodes Module
        
        This module provides core functionality for simulation time management and tracking.
        It offers methods to query various time metrics in the simulation:
        
        - Simulation time (sim time)
        - Monotonic simulation time
        - System (real-world) time
        - Physics step count
        
        These time functions can be queried for the current state or for specific
        points in time using RationalTime objects or (deprecated) stage with history (swh) frame numbers.
        
        Usage:
            # Import the module
            from isaacsim.core.nodes.bindings import _isaacsim_core_nodes
            
            # Acquire the interface
            core_nodes = _isaacsim_core_nodes.acquire_interface()
            
            # Get current time metrics
            sim_time = core_nodes.get_sim_time()
            monotonic_time = core_nodes.get_sim_time_monotonic()
            system_time = core_nodes.get_system_time()
            
            # Get time metrics for a specific frame
            frame_sim_time = core_nodes.get_sim_time_at_time((0, 0))
            
            # Get physics step count
            steps = core_nodes.get_physics_num_steps()
            
            # Timeline control affects time metrics and physics steps
            timeline = omni.timeline.get_timeline_interface()
            timeline.play()  # Start simulation, physics steps will increment
            timeline.stop()  # Stop simulation, physics steps reset to 0
    )pbdoc";

    defineInterfaceClass< isaacsim::core::nodes::CoreNodes>(m, "CoreNodes", "acquire_interface", "release_interface")
        .def("get_sim_time", wrapInterfaceFunction(&CoreNodes::getSimTime),
             R"pbdoc(
                Gets the current simulation time in seconds.

                Returns:
                    float: The current simulation time in seconds.

                @deprecated: This method is deprecated and will be removed in a future release.
                Please use isaacsim.core.simulation_manager.get_simulation_time() instead.
             )pbdoc")
        .def("get_sim_time_monotonic", wrapInterfaceFunction(&CoreNodes::getSimTimeMonotonic),
             R"pbdoc(
                Gets a monotonically increasing simulation time in seconds.

                This time is guaranteed to always increase, unlike regular simulation time
                which can be reset or modified by timeline operations.

                Returns:
                    float: The monotonic simulation time in seconds.

                @deprecated: This method is deprecated and will be removed in a future release.
                Please use isaacsim.core.simulation_manager.get_simulation_monotonic() instead.
             )pbdoc")
        .def("get_system_time", wrapInterfaceFunction(&CoreNodes::getSystemTime),
             R"pbdoc(
                Gets the current system (real-world) time in seconds.

                Returns:
                    float: The current system time in seconds.

                @deprecated: This method is deprecated and will be removed in a future release.
                Please use isaacsim.core.simulation_manager.get_system_time() instead.
             )pbdoc")
        .def("get_physics_num_steps", wrapInterfaceFunction(&CoreNodes::getPhysicsNumSteps),
             R"pbdoc(
                Gets the number of physics steps completed since simulation start.

                This counter is reset to zero when the timeline is stopped.

                Returns:
                    int: The number of physics steps completed.

                @deprecated: This method is deprecated and will be removed in a future release.
                Please use isaacsim.core.simulation_manager.get_num_physics_steps() instead.
             )pbdoc")
        .def("get_sim_time_at_time", wrapInterfaceFunction(&CoreNodes::getSimTimeAtTime),
             R"pbdoc(
                Gets simulation time in seconds at a specific rational time.

                Args:
                    time (omni.fabric.RationalTime): The rational time to query.

                Returns:
                    float: The simulation time in seconds at the specified time.

                @deprecated: This method is deprecated and will be removed in a future release.
                Please use isaacsim.core.simulation_manager.get_simulation_time_at_time() instead.
             )pbdoc")
        .def("get_sim_time_at_time", [](CoreNodes* iface, const std::tuple<int64_t, uint64_t>& timeTuple) {
            int64_t numerator = std::get<0>(timeTuple);
            uint64_t denominator = std::get<1>(timeTuple);
            omni::fabric::RationalTime time(numerator, denominator);
            return iface->getSimTimeAtTime(time);
        }, R"pbdoc(
                Gets simulation time in seconds at a specific rational time.

                Args:
                    time (tuple): A tuple of (numerator, denominator) representing the rational time.

                Returns:
                    float: The simulation time in seconds at the specified time.

                @deprecated: This method is deprecated and will be removed in a future release.
                Please use isaacsim.core.simulation_manager.get_simulation_time_at_time() instead.
             )pbdoc")
        .def("get_sim_time_monotonic_at_time", wrapInterfaceFunction(&CoreNodes::getSimTimeMonotonicAtTime),
             R"pbdoc(
                Gets monotonic simulation time in seconds at a specific rational time.

                Args:
                    time (omni.fabric.RationalTime): The rational time to query.

                Returns:
                    float: The monotonic simulation time in seconds at the specified time.

                @deprecated: This method is deprecated and will be removed in a future release.
                Please use isaacsim.core.simulation_manager.get_simulation_time_monotonic_at_time() instead.
             )pbdoc")
        .def("get_sim_time_monotonic_at_time", [](CoreNodes* iface, const std::tuple<int64_t, uint64_t>& timeTuple) {
            int64_t numerator = std::get<0>(timeTuple);
            uint64_t denominator = std::get<1>(timeTuple);
            omni::fabric::RationalTime time(numerator, denominator);
            return iface->getSimTimeMonotonicAtTime(time);
        }, R"pbdoc(
                Gets monotonic simulation time in seconds at a specific rational time.

                Args:
                    time (tuple): A tuple of (numerator, denominator) representing the rational time.

                Returns:
                    float: The monotonic simulation time in seconds at the specified time.

                @deprecated: This method is deprecated and will be removed in a future release.
                Please use isaacsim.core.simulation_manager.get_simulation_time_monotonic_at_time() instead.
             )pbdoc")
        .def("get_system_time_at_time", wrapInterfaceFunction(&CoreNodes::getSystemTimeAtTime),
             R"pbdoc(
                Gets system (real-world) time in seconds at a specific rational time.

                Args:
                    time (omni.fabric.RationalTime): The rational time to query.

                Returns:
                    float: The system time in seconds at the specified time.

                @deprecated: This method is deprecated and will be removed in a future release.
                Please use isaacsim.core.simulation_manager.get_system_time_at_time() instead.
             )pbdoc")
        .def("get_system_time_at_time", [](CoreNodes* iface, const std::tuple<int64_t, uint64_t>& timeTuple) {
            int64_t numerator = std::get<0>(timeTuple);
            uint64_t denominator = std::get<1>(timeTuple);
            omni::fabric::RationalTime time(numerator, denominator);
            return iface->getSystemTimeAtTime(time);
        }, R"pbdoc(
                Gets system (real-world) time in seconds at a specific rational time.

                Args:
                    time (tuple): A tuple of (numerator, denominator) representing the rational time.

                Returns:
                    float: The system time in seconds at the specified time.

                @deprecated: This method is deprecated and will be removed in a future release.
                Please use isaacsim.core.simulation_manager.get_system_time_at_time() instead.
             )pbdoc")
        ;


}
}
