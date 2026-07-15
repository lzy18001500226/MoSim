#!/usr/bin/env bash
# Build Sunray's official Gazebo Classic Livox plugin in an isolated ROS1 overlay.

set -euo pipefail

PROJECT_ROOT="${PROJECT_ROOT:-/mnt/c/Users/HP/Desktop/MoSim}"
SUNRAY_WS="${SUNRAY_WS:-${PROJECT_ROOT}/References/Sunray}"
LIVOX_PLUGIN_WS="${LIVOX_PLUGIN_WS:-${PROJECT_ROOT}/Results/sunray_ros1/workspaces/sunray_livox_plugin_ws}"
LOG_PATH="${LOG_PATH:-${PROJECT_ROOT}/Results/sunray_ros1/sunray_livox_plugin_build.log}"
PATCH_STAMP="${LIVOX_PLUGIN_WS}/.mosim_multiuav_livox_patch_v1"

SRC_PKG="${SUNRAY_WS}/simulation/gazebo_plugin/livox_laser_simulation"
DST_PKG="${LIVOX_PLUGIN_WS}/src/livox_laser_simulation"

if [[ ! -d "${SRC_PKG}" ]]; then
  echo "Sunray livox_laser_simulation source missing: ${SRC_PKG}" >&2
  exit 2
fi

mkdir -p "$(dirname "${LOG_PATH}")"
mkdir -p "${LIVOX_PLUGIN_WS}/src"
mkdir -p "${DST_PKG}"
cp -a "${SRC_PKG}/." "${DST_PKG}/"

PLUGIN_CPP="${DST_PKG}/src/livox_points_plugin.cpp"
python3 - "${PLUGIN_CPP}" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")

if "reuse cached csv scan mode" not in text:
    text = text.replace(
        '#include <limits>\n#include "csv_reader.hpp"',
        '#include <limits>\n#include "csv_reader.hpp"\n#include <algorithm>\n#include <map>\n#include <mutex>',
        1,
    )
    text = text.replace(
        "        std::vector<std::vector<double>> datas;\n",
        "        std::shared_ptr<const std::vector<std::vector<double>>> datas;\n",
        1,
    )
    old_csv = '''        ROS_INFO_STREAM("load csv file name:" << file_name);
        if (!CsvReader::ReadCsvFile(file_name, datas))
        {
            ROS_INFO_STREAM("cannot get csv file!" << file_name << "will return !");
            return;
        }

'''
    new_csv = '''        ROS_INFO_STREAM("load csv file name:" << file_name);
        {
            static std::mutex csv_cache_mutex;
            static std::map<std::string, std::shared_ptr<const std::vector<std::vector<double>>>> csv_cache;

            std::lock_guard<std::mutex> lock(csv_cache_mutex);
            auto cache_it = csv_cache.find(file_name);
            if (cache_it == csv_cache.end())
            {
                auto loaded_datas = std::make_shared<std::vector<std::vector<double>>>();
                if (!CsvReader::ReadCsvFile(file_name, *loaded_datas))
                {
                    ROS_INFO_STREAM("cannot get csv file!" << file_name << "will return !");
                    return;
                }
                datas = loaded_datas;
                csv_cache[file_name] = loaded_datas;
            }
            else
            {
                datas = cache_it->second;
                ROS_INFO_STREAM("reuse cached csv scan mode, data size:" << datas->size());
            }
        }
'''
    if old_csv not in text:
        raise SystemExit("livox csv load block not found")
    text = text.replace(old_csv, new_csv, 1)
    text = text.replace("convertDataToRotateInfo(datas, aviaInfos);", "convertDataToRotateInfo(*datas, aviaInfos);", 1)

old_collision = '''        laserCollision = physics->CreateCollision("multiray", _parent->ParentName());
        laserCollision->SetName("ray_sensor_collision");
'''
if old_collision in text:
    new_collision = '''        laserCollision = physics->CreateCollision("multiray", _parent->ParentName());
        std::string collision_name = _parent->ParentName() + "_" + _parent->Name() + "_ray_sensor_collision";
        std::replace(collision_name.begin(), collision_name.end(), ':', '_');
        std::replace(collision_name.begin(), collision_name.end(), '/', '_');
        laserCollision->SetName(collision_name);
'''
    text = text.replace(old_collision, new_collision, 1)

entry_marker = "[MoSimLivoxLoadEnter]"
if entry_marker not in text:
    text = text.replace(
        "        std::string file_name = sdf->Get<std::string>(\"csv_file_name\");\n",
        "        std::string file_name = sdf->Get<std::string>(\"csv_file_name\");\n"
        "        ROS_INFO_STREAM(\"[MoSimLivoxLoadEnter] sensor=\" << _parent->Name()\n"
        "                        << \" parent=\" << _parent->ParentName()\n"
        "                        << \" world=\" << _parent->WorldName()\n"
        "                        << \" gazebo_topic=\" << _parent->Topic());\n",
        1,
    )

old_ros_init = "        ros::init(argc, argv, curr_scan_topic);\n        rosNode.reset(new ros::NodeHandle(this->robot_namespace));"
if old_ros_init in text:
    text = text.replace(
        old_ros_init,
        "        if (!ros::isInitialized())\n"
        "        {\n"
        "            ros::init(argc, argv, curr_scan_topic, ros::init_options::NoSigintHandler);\n"
        "        }\n"
        "        rosNode.reset(new ros::NodeHandle(this->robot_namespace));",
        1,
    )

path.write_text(text, encoding="utf-8")
PY

CMAKELISTS="${DST_PKG}/CMakeLists.txt"

if ! grep -q "find_package(Protobuf REQUIRED)" "${CMAKELISTS}"; then
  sed -i '/find_package(PCL REQUIRED)/a find_package(Protobuf REQUIRED)' "${CMAKELISTS}"
fi

if ! grep -q "Protobuf_INCLUDE_DIRS" "${CMAKELISTS}"; then
  sed -i 's/${PCL_INCLUDE_DIRS}/${PCL_INCLUDE_DIRS}\n        ${Protobuf_INCLUDE_DIRS}/' "${CMAKELISTS}"
fi

sed -i 's/target_link_libraries(livox_laser_simulation libprotobuf.so.9)/target_link_libraries(livox_laser_simulation ${Protobuf_LIBRARIES})/' "${CMAKELISTS}"

{
  echo "LIVOX_PLUGIN_WS=${LIVOX_PLUGIN_WS}"
  echo "SUNRAY_WS=${SUNRAY_WS}"
  echo "SRC_PKG=${SRC_PKG}"
  echo "DST_PKG=${DST_PKG}"
  export PATH=/opt/ros/noetic/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/usr/lib/wsl/lib
  set +u
  source /usr/share/gazebo/setup.sh
  source /opt/ros/noetic/setup.bash
  set -u
  cd "${LIVOX_PLUGIN_WS}"
  catkin_make -DCMAKE_BUILD_TYPE=Release
  test -f "${LIVOX_PLUGIN_WS}/devel/lib/liblivox_laser_simulation.so"
  touch "${PATCH_STAMP}"
  ldd "${LIVOX_PLUGIN_WS}/devel/lib/liblivox_laser_simulation.so" | grep -E "protobuf|gazebo|roscpp" || true
} > "${LOG_PATH}" 2>&1

echo "${LIVOX_PLUGIN_WS}"
