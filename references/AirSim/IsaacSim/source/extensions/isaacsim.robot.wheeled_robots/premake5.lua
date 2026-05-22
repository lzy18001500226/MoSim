-- SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
-- SPDX-License-Identifier: Apache-2.0
--
-- Licensed under the Apache License, Version 2.0 (the "License");
-- you may not use this file except in compliance with the License.
-- You may obtain a copy of the License at
--
-- http://www.apache.org/licenses/LICENSE-2.0
--
-- Unless required by applicable law or agreed to in writing, software
-- distributed under the License is distributed on an "AS IS" BASIS,
-- WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
-- See the License for the specific language governing permissions and
-- limitations under the License.

local ext = get_current_extension_info()
local ogn = get_ogn_project_information(ext, "isaacsim/robot/wheeled_robots")

-- ext.group = "omnigraph"

project_ext(ext)
-- C++ Carbonite plugin
project_ext_plugin(ext, "isaacsim.robot.wheeled_robots.plugin")
add_files("impl", "plugins")
add_files("ogn", ogn.nodes_path)

filter { "system:linux", "platforms:x86_64" }
disablewarnings { "error=narrowing", "error=unused-but-set-variable", "error=unused-variable" }
filter { "system:windows" }
libdirs {
    "%{root}/_build/target-deps/tbb/lib/intel64/vc14",
}
filter {}

add_ogn_dependencies(ogn, { "python/nodes" })
add_ogn_dependencies(ogn, { "nodes" })

includedirs {
    "%{root}/source/extensions/isaacsim.core.includes/include",
    "%{root}/_build/target-deps/usd/%{cfg.buildcfg}/include",
    "%{root}/_build/target-deps/usd/%{cfg.buildcfg}/include/boost",
    "%{root}/_build/target-deps/usd_ext_physics/%{cfg.buildcfg}/include",
    "%{root}/_build/target-deps/python/include/python3.11",

    "%{root}/_build/target-deps/omni_physics/%{config}/include",
    "%{root}/source/extensions/isaacsim.robot.wheeled_robots/include",
}

libdirs {
    "%{root}/_build/target-deps/usd/%{cfg.buildcfg}/lib",
    "%{root}/_build/target-deps/usd_ext_physics/%{cfg.buildcfg}/lib",
}

links {
    --    "usdGeom", "usdUtils", "omni.usd",
}

extra_usd_libs = {}

-- Begin OpenUSD
add_usd(extra_usd_libs)
-- End OpenUSD

filter { "configurations:debug" }
defines { "_DEBUG" }
filter { "configurations:release" }
defines { "NDEBUG" }
filter {}

project_ext_ogn(ext, ogn)

project_ext_bindings {
    ext = ext,
    project_name = ogn.python_project,
    module = ogn.bindings_module,
    src = ogn.bindings_path,
    target_subdir = ogn.bindings_target_path,
}
add_files("bindings", "bindings/*.*")
add_files("python", "python/*.py")
add_files("python/controllers", "python/controllers/*.py")
add_files("python/nodes", "python/nodes/*.py")
add_files("python/tests", "python/tests/*.py")
add_files("python/robots", "python/robots/*.py")

includedirs {

    "%{root}/source/extensions/isaacsim.robot.wheeled_robots/include",
}

-- Add the standard dependencies all OGN projects have
repo_build.prebuild_copy {
    { "python/__init__.py", ogn.python_target_path },
}

repo_build.prebuild_link {
    { "docs", ext.target_dir .. "/docs" },
    { "data", ext.target_dir .. "/data" },
    { "python/controllers", ogn.python_target_path .. "/controllers" },
    { "python/robots", ogn.python_target_path .. "/robots" },
    { "python/impl", ogn.python_target_path .. "/impl" },
    { "python/nodes", ogn.python_target_path .. "/nodes" },
    { "python/tests", ogn.python_tests_target_path },
}
