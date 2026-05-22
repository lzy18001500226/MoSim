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
local ogn = get_ogn_project_information(ext, "isaacsim/ros2/bridge")
project_ext(ext)

project_with_location("isaacsim.ros2.bridge.check")
targetdir(ext.bin_dir)
kind("ConsoleApp")
language("C++")
add_files("impl", "compatibility")

includedirs {
    "%{root}/_build/target-deps/nv_ros2_humble/include",
    "%{root}/source/extensions/isaacsim.ros2.bridge/include",
    "%{root}/source/extensions/isaacsim.core.includes/include",
}

filter { "system:linux" }
links { "dl" }
filter { "system:windows" }
buildoptions("-D_CRT_SECURE_NO_WARNINGS")
includedirs {
    "%{root}/_build/target-deps/nv_ros2_humble/include/rosidl_runtime_c",
    "%{root}/_build/target-deps/nv_ros2_humble/include/builtin_interfaces",
    "%{root}/_build/target-deps/nv_ros2_humble/include/rosidl_typesupport_interface",
    "%{root}/_build/target-deps/nv_ros2_humble/include/rosidl_typesupport_introspection_c",
    "%{root}/_build/target-deps/nv_ros2_humble/include/rcl",
    "%{root}/_build/target-deps/nv_ros2_humble/include/rcutils",
    "%{root}/_build/target-deps/nv_ros2_humble/include/rmw",
    "%{root}/_build/target-deps/nv_ros2_humble/include/rcl_yaml_param_parser",
}
filter {}

-- Build the backend for each ROS distribution
local ros_distributions = { "humble", "jazzy" }

for _, ros_distro in ipairs(ros_distributions) do
    project_with_location("isaacsim.ros2.bridge." .. ros_distro)
    targetdir(ext.bin_dir)
    kind("SharedLib")
    language("C++")

    pic("On")
    staticruntime("Off")
    defines { "ROS2_BACKEND_" .. ros_distro:upper() }
    add_files("impl", "library/backend")
    add_files("iface", "include")
    includedirs {
        "%{root}/source/extensions/isaacsim.core.includes/include",
        "%{root}/_build/target-deps/omni_physics/%{config}/include",
        "%{root}/_build/target-deps/nv_ros2_" .. ros_distro .. "/include",
        "%{root}/_build/target-deps/nlohmann_json/include",
        "%{root}/source/extensions/isaacsim.ros2.bridge",
        "%{root}/source/extensions/isaacsim.ros2.bridge/include",
        "%{root}/_build/target-deps/omni_client_library/include",
        "%{kit_sdk_bin_dir}/dev/fabric/include/",
        "%{root}/_build/target-deps/nv_ros2_" .. ros_distro .. "/include/type_description_interfaces",
        "%{root}/_build/target-deps/nv_ros2_" .. ros_distro .. "/include/service_msgs",
        "%{root}/_build/target-deps/nv_ros2_" .. ros_distro .. "/include/rosidl_dynamic_typesupport",
    }
    libdirs {
        extsbuild_dir .. "/omni.usd.core/bin",
        "%{root}/_build/target-deps/nv_ros2_" .. ros_distro .. "/lib",
    }
    links {
        "rosidl_runtime_c",
        "rcutils",
        "rcl",
        "rmw",
        "tf2_msgs__rosidl_typesupport_c",
        "tf2_msgs__rosidl_generator_c",
        "geometry_msgs__rosidl_typesupport_c",
        "geometry_msgs__rosidl_generator_c",
        "nav_msgs__rosidl_typesupport_c",
        "nav_msgs__rosidl_generator_c",
        "std_msgs__rosidl_typesupport_c",
        "std_msgs__rosidl_generator_c",
        "rosgraph_msgs__rosidl_typesupport_c",
        "rosgraph_msgs__rosidl_generator_c",
        "sensor_msgs__rosidl_typesupport_c",
        "sensor_msgs__rosidl_generator_c",
        -- "vision_msgs__rosidl_typesupport_c", "vision_msgs__rosidl_generator_c"
        -- "ackermann_msgs__rosidl_typesupport_c", "ackermann_msgs__rosidl_generator_c"
    }

    extra_usd_libs = { "usdPhysics" }

    -- Begin OpenUSD
    add_usd(extra_usd_libs)
    -- End OpenUSD

    filter { "system:linux" }
    disablewarnings { "error=pragmas" }
    includedirs {
        "%{root}/_build/target-deps/python/include/python3.11",
    }
    buildoptions("-fvisibility=default")
    linkoptions { "-Wl,--export-dynamic" }
    filter { "system:windows" }
    includedirs {
        "%{root}/_build/target-deps/nv_ros2_" .. ros_distro .. "/include/rosidl_runtime_c",
        "%{root}/_build/target-deps/nv_ros2_" .. ros_distro .. "/include/builtin_interfaces",
        "%{root}/_build/target-deps/nv_ros2_" .. ros_distro .. "/include/geometry_msgs",
        "%{root}/_build/target-deps/nv_ros2_" .. ros_distro .. "/include/nav_msgs",
        "%{root}/_build/target-deps/nv_ros2_" .. ros_distro .. "/include/sensor_msgs",
        "%{root}/_build/target-deps/nv_ros2_" .. ros_distro .. "/include/tf2_msgs",
        "%{root}/_build/target-deps/nv_ros2_" .. ros_distro .. "/include/vision_msgs",
        "%{root}/_build/target-deps/nv_ros2_" .. ros_distro .. "/include/std_msgs",
        "%{root}/_build/target-deps/nv_ros2_" .. ros_distro .. "/include/rosgraph_msgs",
        "%{root}/_build/target-deps/nv_ros2_" .. ros_distro .. "/include/rosidl_typesupport_interface",
        "%{root}/_build/target-deps/nv_ros2_" .. ros_distro .. "/include/rosidl_typesupport_introspection_c",
        "%{root}/_build/target-deps/nv_ros2_" .. ros_distro .. "/include/rcl",
        "%{root}/_build/target-deps/nv_ros2_" .. ros_distro .. "/include/rcutils",
        "%{root}/_build/target-deps/nv_ros2_" .. ros_distro .. "/include/rmw",
        "%{root}/_build/target-deps/nv_ros2_" .. ros_distro .. "/include/rcl_yaml_param_parser",
        "%{root}/_build/target-deps/nv_ros2_" .. ros_distro .. "/include/ackermann_msgs",
    }
    libdirs {
        "%{root}/_build/target-deps/tbb/lib/intel64/vc14", -- Update for Jazzy if needed
    }
    filter {}

    filter { "configurations:debug" }
    defines { "_DEBUG" }
    filter { "configurations:release" }
    defines { "NDEBUG" }
    filter {}
end

-- C++ Carbonite plugin
project_ext_plugin(ext, "isaacsim.ros2.bridge.plugin")

add_files("impl", "plugins")
add_files("impl", "cuda")
add_files("iface", "include")
add_files("ogn", ogn.nodes_path)
-- link_boost_for_windows({"boost_python310"})
add_cuda_dependencies()

add_ogn_dependencies(ogn, { "python/nodes" })

include_physx()
includedirs {
    "%{root}/source/extensions/isaacsim.core.includes/include",
    "%{root}/_build/target-deps/usd/%{cfg.buildcfg}/include",
    "%{root}/_build/target-deps/usd/%{cfg.buildcfg}/include/boost",
    "%{root}/_build/target-deps/usd_ext_physics/%{cfg.buildcfg}/include",
    "%{root}/_build/target-deps/python/include/python3.11",
    "%{root}/_build/target-deps/python/include",
    "%{root}/_build/target-deps/omni_physics/%{config}/include",
    extsbuild_dir .. "/omni.syntheticdata/include",
    extsbuild_dir .. "/usdrt.scenegraph/include",
    "%{root}/_build/target-deps/omni_client_library/include",
    "%{root}/_build/target-deps/omni-isaacsim-schema/%{platform}/%{config}/include",
    "%{root}/source/extensions/isaacsim.ros2.bridge",
    "%{root}/_build/target-deps/nlohmann_json/include",
    "%{root}/source/extensions/isaacsim.core.nodes/include",
    "%{kit_sdk_bin_dir}/dev/fabric/include/",
    "%{root}/source/extensions/isaacsim.ros2.bridge/include",
}
libdirs {
    "%{root}/_build/target-deps/usd/%{cfg.buildcfg}/lib",
    "%{root}/_build/target-deps/usd_ext_physics/%{cfg.buildcfg}/lib",
    extsbuild_dir .. "/omni.usd.core/bin",
    "%{root}/_build/target-deps/omni-isaacsim-schema/%{platform}/%{config}/lib",
}
-- links {
--     "gf",  "sdf", "tf",  "usd", "usdGeom", "vt", "usdUtils", "omni.usd", , "physxSchema", "sdf", , "carb",
--     ,
-- }
links { "isaacSensorSchema", "physxSchema", "omni.usd" }

extra_usd_libs = { "usdGeom", "usdPhysics" }

-- Begin OpenUSD
add_usd(extra_usd_libs)
-- End OpenUSD

filter { "system:linux" }
disablewarnings { "error=narrowing", "error=unused-but-set-variable", "error=unused-variable" }
links { "boost_system", "stdc++fs" }
filter { "system:windows" }
filter {}

filter { "configurations:debug" }
defines { "_DEBUG" }
filter { "configurations:release" }
defines { "NDEBUG" }
filter {}

project_ext_ogn(ext, ogn)

-- Python Bindings for Carbonite Plugin
project_ext_bindings {
    ext = ext,
    project_name = "isaacsim.ros2.bridge.python",
    module = "_ros2_bridge",
    src = "bindings",
    target_subdir = "isaacsim/ros2/bridge",
}
includedirs {
    "%{root}/source/extensions/isaacsim.ros2.bridge/include",
}

repo_build.prebuild_link {
    { "python/impl", ext.target_dir .. "/isaacsim/ros2/bridge/impl" },
    { "python/tests", ext.target_dir .. "/isaacsim/ros2/bridge/tests" },
    { "docs", ext.target_dir .. "/docs" },
    { "data", ext.target_dir .. "/data" },
    { "include", ext.target_dir .. "/include" },
}

repo_build.prebuild_copy {
    { "python/*.py", ext.target_dir .. "/isaacsim/ros2/bridge" },
    { "rclpy/*.py", ext.target_dir .. "/humble/rclpy" },
    { "rclpy/*.py", ext.target_dir .. "/jazzy/rclpy" },
}

if os.target() == "linux" then
    repo_build.prebuild_copy {
        { "%{root}/_build/target-deps/nv_ros2_humble/lib/lib**", ext.target_dir .. "/humble/lib" },
        { "%{root}/_build/target-deps/nv_ros2_humble/lib/python3.11/site-packages", ext.target_dir .. "/humble/rclpy" },
        {
            "%{root}/_build/target-deps/nv_ros2_humble/local/lib/python3.11/dist-packages",
            ext.target_dir .. "/humble/rclpy",
        },
    }
    repo_build.prebuild_copy {
        { "%{root}/_build/target-deps/nv_ros2_jazzy/lib/lib**", ext.target_dir .. "/jazzy/lib" },
        { "%{root}/_build/target-deps/nv_ros2_jazzy/opt/libyaml_vendor/lib/**", ext.target_dir .. "/jazzy/lib" },
        { "%{root}/_build/target-deps/nv_ros2_jazzy/opt/spdlog_vendor/lib/**", ext.target_dir .. "/jazzy/lib" },
        { "%{root}/_build/target-deps/nv_ros2_jazzy/lib/python3.11/site-packages", ext.target_dir .. "/jazzy/rclpy" },
    }
end

if os.target() == "windows" then
    repo_build.prebuild_copy {
        { "%{root}/_build/target-deps/nv_ros2_humble/bin/**.dll", ext.target_dir .. "/humble/lib" },
        { "%{root}/_build/target-deps/nv_ros2_humble/Lib/site-packages", ext.target_dir .. "/humble/rclpy" },
        { "%{root}/_build/target-deps/tinyxml2/bin/**.dll", ext.target_dir .. "/humble/lib" },
    }
    repo_build.prebuild_copy {
        { "%{root}/_build/target-deps/nv_ros2_jazzy/bin/**.dll", ext.target_dir .. "/jazzy/lib" },
        { "%{root}/_build/target-deps/nv_ros2_jazzy/Lib/site-packages", ext.target_dir .. "/jazzy/rclpy" },
        { "%{root}/_build/target-deps/nv_ros2_jazzy/opt/libyaml_vendor/bin/**.dll", ext.target_dir .. "/jazzy/lib" },
        { "%{root}/_build/target-deps/nv_ros2_jazzy/opt/spdlog_vendor/bin/**.dll", ext.target_dir .. "/jazzy/lib" },
        { "%{root}/_build/target-deps/tinyxml2/bin/**.dll", ext.target_dir .. "/jazzy/lib" },
    }
end



-- Build the C++ plugin that will be loaded by the tests
project_ext_tests(ext, "isaacsim.ros2.bridge.backend_tests")
cppdialect("C++17")
    add_files("source", "library/tests")
    -- Ensure factory symbol is compiled into the test library so tests can call createFactory()
    includedirs {
        "include",
        "plugins/",
        "%{target_deps}/doctest/include",
        "%{root}/source/extensions/isaacsim.ros2.bridge/include",
        "%{root}/_build/target-deps/nlohmann_json/include",
        "%{root}/source/deprecated/omni.isaac.dynamic_control/include",
        "%{root}/source/extensions/isaacsim.core.includes/include",
        "%{root}/_build/target-deps/python/include/python3.11",
        "%{root}/_build/target-deps/python/include",
        "%{kit_sdk_bin_dir}/dev/fabric/include/",

    }
    -- link omni.kit.test (path or 'repo_precache_exts' config may need to be adjusted)
    libdirs {
        extsbuild_dir.."/omni.kit.test/bin",
    }
    add_usd()
    filter { "system:linux" }
    disablewarnings { "error=narrowing", "error=unused-but-set-variable", "error=unused-variable" }
    links { "boost_system", "stdc++fs" }
    filter { "system:windows" }
    filter {}

    filter { "configurations:debug" }
        defines { "_DEBUG" }
    filter { "configurations:release" }
        defines { "NDEBUG" }
    filter {}