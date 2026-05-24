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
ext.target_dir = deprecated_exts_path .. "/" .. ext.id
ext.bin_dir = ext.target_dir .. "/bin"
project_ext(ext)

-- C++ Carbonite plugin
project_ext_plugin(ext, "omni.isaac.dynamic_control.plugin")

add_files("impl", "plugins")

include_physx()

includedirs {
    "%{root}/source/extensions/isaacsim.core.includes/include",
    target_deps .. "/usd/%{cfg.buildcfg}/include",
    target_deps .. "/usd/%{cfg.buildcfg}/include/boost",
    target_deps .. "/usd_ext_physics/%{cfg.buildcfg}/include",
    target_deps .. "/omni_physics/%{config}/include",
    target_deps .. "/omni_client_library/include",
    "%{root}/source/deprecated/omni.isaac.dynamic_control/include",
}
libdirs {
    target_deps .. "/usd/%{cfg.buildcfg}/lib",
    target_deps .. "/usd_ext_physics/%{cfg.buildcfg}/lib",
    extsbuild_dir .. "/omni.usd.core/bin",
}

links { "omni.usd" }

extra_usd_libs = {
    "usdUtils",
    "usdGeom",
}
-- Begin OpenUSD
add_usd(extra_usd_libs)
-- End OpenUSD

includedirs {
    target_deps .. "/usd/%{cfg.buildcfg}/include/boost",
}

filter { "system:linux" }
includedirs {
    target_deps .. "/usd/%{cfg.buildcfg}/include/boost",
    target_deps .. "/python/include/python3.11",
}
filter { "system:windows" }
libdirs {
    target_deps .. "/tbb/lib/intel64/vc14",
}
filter {}

filter { "configurations:debug" }
defines { "_DEBUG" }
filter { "configurations:release" }
defines { "NDEBUG" }
filter {}

-- Python Bindings for Carobnite Plugin
project_ext_bindings {
    ext = ext,
    project_name = "omni.isaac.dynamic_control.python",
    module = "_dynamic_control",
    src = "bindings",
    target_subdir = "omni/isaac/dynamic_control",
}
staticruntime("Off")

includedirs {
    "%{root}/source/deprecated/omni.isaac.dynamic_control/include",
    "%{root}/source/extensions/isaacsim.core.includes/include",
    "%{root}/_build/target-deps/usd/%{cfg.buildcfg}/include",
}

libdirs {
    "%{root}/_build/target-deps/usd/%{cfg.buildcfg}/lib",
    extsbuild_dir .. "/omni.usd.core/bin",
}

extra_usd_libs = {}

-- Begin OpenUSD
add_usd(extra_usd_libs)
-- End OpenUSD

filter { "system:linux", "platforms:x86_64" }
links { "tbb" }
filter {}

filter { "system:windows", "platforms:x86_64" }
-- link_boost_for_windows({"boost_python310"})
libdirs {
    "%{root}/_build/target-deps/tbb/lib/intel64/vc14",
}
filter {}

filter { "configurations:debug" }
defines { "_DEBUG" }
filter { "configurations:release" }
defines { "NDEBUG" }
filter {}

repo_build.prebuild_link {
    { "python/scripts", ext.target_dir .. "/omni/isaac/dynamic_control/scripts" },
    { "python/tests", ext.target_dir .. "/omni/isaac/dynamic_control/tests" },
    { "docs", ext.target_dir .. "/docs" },
    { "data", ext.target_dir .. "/data" },
    { "include", ext.target_dir .. "/include" },
}

repo_build.prebuild_copy {
    { "python/*.py", ext.target_dir .. "/omni/isaac/dynamic_control" },
}
