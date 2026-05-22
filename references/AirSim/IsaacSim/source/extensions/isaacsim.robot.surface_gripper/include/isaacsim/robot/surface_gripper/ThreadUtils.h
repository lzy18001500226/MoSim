// SPDX-FileCopyrightText: Copyright (c) 2020-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

#pragma once


#include <carb/tasking/ITasking.h>
#include <carb/tasking/TaskingUtils.h>

namespace isaacsim
{
namespace robot
{
namespace surface_gripper
{

template <typename Func>
inline void parallelForIndex(size_t count, Func func)
{
    auto tasking = carb::getCachedInterface<carb::tasking::ITasking>();

    carb::tasking::TaskGroup threads;

    for (size_t i = 0; i < count; i += 1)
    {
        tasking->addTask(carb::tasking::Priority::eHigh, threads, [i, count, &func]() { func(i); });
    }
    threads.wait();
}

} // namespace surface_gripper
} // namespace robot
} // namespace isaacsim
