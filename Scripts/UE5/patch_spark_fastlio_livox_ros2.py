#!/usr/bin/env python3
"""Patch the staged spark-fast-lio candidate for ROS2 Livox CustomMsg.

The patch target is the ignored candidate tree under Results/tmp. This script
does not edit upstream references or system ROS files. It makes the local
candidate internally consistent with the project-local minimal
Scripts/ros/livox_ros_driver2 message package, then the static readiness gate
must pass before build/runtime checks continue.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CANDIDATE = ROOT / "Results/tmp/fastlio_ros2_candidates/spark-fast-lio/spark_fast_lio"


def project_path(path: str | Path) -> Path:
    raw = Path(path)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text and new in text:
        return text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected exactly one {label}, found {count}")
    return text.replace(old, new, 1)


def write_if_changed(path: Path, text: str) -> bool:
    old = path.read_text(encoding="utf-8")
    if old == text:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def remove_regex_block(text: str, pattern: str) -> str:
    """Remove every previous copy of a generated patch block."""
    return re.sub(pattern, "", text, flags=re.DOTALL)


def patch_package_xml(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if "<depend>livox_ros_driver2</depend>" not in text:
        text = text.replace(
            "  <depend>pcl_conversions</depend>\n",
            "  <depend>pcl_conversions</depend>\n  <depend>livox_ros_driver2</depend>\n",
        )
    return write_if_changed(path, text)


def patch_cmake(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    text = replace_once(
        text,
        "# Optional: Livox driver\nfind_package(livox_ros_driver QUIET)\n",
        "# Project-local minimal Livox ROS2 message package.\nfind_package(livox_ros_driver2 REQUIRED)\n",
        "ROS1 Livox find_package block",
    )
    old_optional_block = """# If Livox found, link it here
if(livox_ros_driver_FOUND)
  target_link_libraries(spark_lio_component
    ${livox_ros_driver_LIBRARIES}
  )
  target_include_directories(spark_lio_component PRIVATE
    ${livox_ros_driver_INCLUDE_DIRS}
  )
  target_compile_definitions(spark_lio_component PRIVATE
    -DLIVOX_ROS_DRIVER_FOUND=${livox_ros_driver_FOUND}
  )
else()
  message(STATUS "Missing livox driver! AVIA Lidar will be disabled!")
endif()
"""
    text = replace_once(
        text,
        old_optional_block,
        "target_compile_definitions(spark_lio_component PRIVATE -DLIVOX_ROS_DRIVER_FOUND=1)\n",
        "ROS1 Livox optional link block",
    )
    if "\n  livox_ros_driver2\n" not in text:
        text = text.replace(
            "  pcl_conversions\n)",
            "  pcl_conversions\n  livox_ros_driver2\n)",
        )
    return write_if_changed(path, text)


def patch_preprocess_h(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    text = text.replace("#include <livox_ros_driver/CustomMsg.h>", "#include <livox_ros_driver2/msg/custom_msg.hpp>")
    text = text.replace("livox_ros_driver::CustomMsg::ConstPtr", "livox_ros_driver2::msg::CustomMsg")
    text = text.replace("livox_ros_driver::CustomMsg", "livox_ros_driver2::msg::CustomMsg")
    return write_if_changed(path, text)


def patch_preprocess_cpp(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if "#include <algorithm>" not in text:
        text = text.replace("#include \"preprocess.h\"\n", "#include \"preprocess.h\"\n\n#include <algorithm>\n#include <limits>\n")
    if "#include <limits>" not in text:
        text = text.replace("#include <algorithm>\n", "#include <algorithm>\n#include <limits>\n")
    text = text.replace("livox_ros_driver::CustomMsg", "livox_ros_driver2::msg::CustomMsg")
    text = text.replace("msg.points[i].offset_time /\n            static_cast<float>(1000000)", "msg.points[i].offset_time /\n            static_cast<float>(1000000)")
    text = text.replace("ROS_DEBUG(", "RCLCPP_DEBUG(rclcpp::get_logger(\"Preprocess\"), ")
    text = text.replace(
        "  int plsize = msg.point_num;\n  //   cout<<\"plsie: \"<<plsize<<endl;",
        "  int plsize = static_cast<int>(std::min<size_t>(msg.point_num, msg.points.size()));\n  //   cout<<\"plsie: \"<<plsize<<endl;",
    )
    if "Livox avia_handler entry:" not in text:
        text = text.replace(
            "  //   cout<<\"plsie: \"<<plsize<<endl;\n\n  pl_corn.reserve(plsize);",
            "  //   cout<<\"plsie: \"<<plsize<<endl;\n  RCLCPP_INFO(rclcpp::get_logger(\"Preprocess\"), \"Livox avia_handler entry: point_num=%u points_size=%zu plsize=%d\", msg.point_num, msg.points.size(), plsize);\n\n  pl_corn.reserve(plsize);",
        )
    text = text.replace(
        "  pl_corn.reserve(plsize);\n  pl_surf.reserve(plsize);",
        "  if (feature_enabled) {\n    pl_corn.reserve(plsize);\n    pl_surf.reserve(plsize);\n  }",
    )
    text = text.replace(
        "  if (!feature_enabled) {\n    pl_surf.reserve(plsize);\n  } else {\n    pl_corn.reserve(plsize);\n    pl_surf.reserve(plsize);\n  }",
        "  if (feature_enabled) {\n    pl_corn.reserve(plsize);\n    pl_surf.reserve(plsize);\n  }",
    )
    text = text.replace(
        """  pl_corn.reserve(plsize);
  pl_surf.reserve(plsize);
  pl_full.resize(plsize);

  for (int i = 0; i < N_SCANS; i++) {
    pl_buff[i].clear();
    pl_buff[i].reserve(plsize);
  }
  uint valid_num = 0;""",
        """  pl_corn.reserve(plsize);
  pl_surf.reserve(plsize);
  if (feature_enabled) {
    pl_full.resize(plsize);
    for (int i = 0; i < N_SCANS; i++) {
      pl_buff[i].clear();
      pl_buff[i].reserve(plsize);
    }
  }
  uint valid_num = 0;""",
    )
    old_blind_filter = """          if ((abs(pl_full[i].x - pl_full[i - 1].x) > 1e-7) ||
              (abs(pl_full[i].y - pl_full[i - 1].y) > 1e-7) ||
              (abs(pl_full[i].z - pl_full[i - 1].z) > 1e-7) &&
                  (pl_full[i].x * pl_full[i].x + pl_full[i].y * pl_full[i].y +
                       pl_full[i].z * pl_full[i].z >
                   (blind * blind))) {
            pl_surf.push_back(pl_full[i]);
          }"""
    new_blind_filter = """          const bool point_changed =
              (std::abs(pl_full[i].x - pl_full[i - 1].x) > 1e-7) ||
              (std::abs(pl_full[i].y - pl_full[i - 1].y) > 1e-7) ||
              (std::abs(pl_full[i].z - pl_full[i - 1].z) > 1e-7);
          const bool outside_blind =
              (pl_full[i].x * pl_full[i].x + pl_full[i].y * pl_full[i].y +
                   pl_full[i].z * pl_full[i].z >
               (blind * blind));
          if (point_changed && outside_blind) {
            pl_surf.push_back(pl_full[i]);
          }"""
    text = text.replace(old_blind_filter, new_blind_filter)
    old_non_feature_loop = """    for (uint i = 1; i < plsize; i++) {
      if ((msg.points[i].line < N_SCANS) &&
          ((msg.points[i].tag & 0x30) == 0x10 || (msg.points[i].tag & 0x30) == 0x00)) {
        valid_num++;
        if (valid_num % point_filter_num == 0) {
          pl_full[i].x         = msg.points[i].x;
          pl_full[i].y         = msg.points[i].y;
          pl_full[i].z         = msg.points[i].z;
          pl_full[i].intensity = msg.points[i].reflectivity;
          pl_full[i].curvature =
              msg.points[i].offset_time /
              static_cast<float>(
                  1000000);  // use curvature as time of each laser points, curvature unit: ms

          const bool point_changed =
              (std::abs(pl_full[i].x - pl_full[i - 1].x) > 1e-7) ||
              (std::abs(pl_full[i].y - pl_full[i - 1].y) > 1e-7) ||
              (std::abs(pl_full[i].z - pl_full[i - 1].z) > 1e-7);
          const bool outside_blind =
              (pl_full[i].x * pl_full[i].x + pl_full[i].y * pl_full[i].y +
                   pl_full[i].z * pl_full[i].z >
               (blind * blind));
          if (point_changed && outside_blind) {
            pl_surf.push_back(pl_full[i]);
          }
        }
      }
    }"""
    new_non_feature_loop = """    PointType previous_point;
    previous_point.x = std::numeric_limits<float>::quiet_NaN();
    previous_point.y = std::numeric_limits<float>::quiet_NaN();
    previous_point.z = std::numeric_limits<float>::quiet_NaN();
    for (int i = 0; i < plsize; i++) {
      const auto &src = msg.points[i];
      if (src.line >= N_SCANS) continue;
      if (((src.tag & 0x30) != 0x10) && ((src.tag & 0x30) != 0x00)) continue;
      valid_num++;
      if (point_filter_num <= 0 || valid_num % point_filter_num != 0) continue;

      PointType point;
      point.x = src.x;
      point.y = src.y;
      point.z = src.z;
      point.intensity = src.reflectivity;
      point.normal_x = 0.0;
      point.normal_y = 0.0;
      point.normal_z = 0.0;
      point.curvature = src.offset_time / static_cast<float>(1000000);

      const bool outside_blind =
          (point.x * point.x + point.y * point.y + point.z * point.z) > (blind * blind);
      const bool point_changed =
          std::isnan(previous_point.x) ||
          (std::abs(point.x - previous_point.x) > 1e-7) ||
          (std::abs(point.y - previous_point.y) > 1e-7) ||
          (std::abs(point.z - previous_point.z) > 1e-7);
      previous_point = point;
      if (point_changed && outside_blind) {
        pl_surf.push_back(point);
      }
    }"""
    if old_non_feature_loop in text:
        text = text.replace(old_non_feature_loop, new_non_feature_loop)
    text = remove_regex_block(
        text,
        r"\n  RCLCPP_INFO\(\n      rclcpp::get_logger\(\"Preprocess\"\),\n      \"Livox preprocess: points=%[du] valid=%u surf=%zu N_SCANS=%d filter=%d blind=%.3f first_offset=%u last_offset=%u\",.*?msg\.points\.empty\(\) \? 0u : msg\.points\.back\(\)\.offset_time\);\n",
    )
    summary_replacement = """  }
  RCLCPP_INFO(
      rclcpp::get_logger("Preprocess"),
      "Livox preprocess: points=%u valid=%u surf=%zu N_SCANS=%d filter=%d blind=%.3f first_offset=%u last_offset=%u",
      msg.point_num,
      valid_num,
      pl_surf.size(),
      N_SCANS,
      point_filter_num,
      blind,
      msg.points.empty() ? 0u : msg.points.front().offset_time,
      msg.points.empty() ? 0u : msg.points.back().offset_time);
}
#endif

void Preprocess::oust64_handler"""
    summary_anchors = (
        """  }
}
#endif

void Preprocess::oust64_handler""",
        """  }}
#endif

void Preprocess::oust64_handler""",
    )
    for anchor in summary_anchors:
        if anchor in text:
            text = text.replace(anchor, summary_replacement, 1)
            break
    else:
        raise SystemExit("failed to patch Livox preprocess summary block")
    return write_if_changed(path, text)


def patch_spark_cpp(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    text = text.replace("LIVOXROS_DRIVER_FOUND", "LIVOX_ROS_DRIVER_FOUND")
    text = text.replace("livoxLidarCallback", "livoxLiDARCallback")
    text = text.replace("!imu_buffer.empty()", "!imu_buffer_.empty()")
    text = text.replace("last_lidar_timestamp_.nanseconds()", "last_lidar_timestamp_.nanoseconds()")
    text = remove_regex_block(
        text,
        r"\n  RCLCPP_INFO\(\n      this->get_logger\(\),\n      \"MoSim startup params: lidar_type=%d scan_line=%d blind=%.3f scan_rate=%d point_filter_pre=%d point_filter=%d base_frame='%s' map_frame='%s' lidar_frame='%s' imu_frame='%s'\",.*?point_filter_num_ = 1;\n  }\n",
    )
    text = text.replace(
        """  main_loop_timer_ =
      create_wall_timer(std::chrono::milliseconds(1), std::bind(&SPARKFastLIO2::main, this));

  if ((preprocessor_->point_filter_num != 1 && point_filter_num_ > 1)) {""",
        """  RCLCPP_INFO(
      this->get_logger(),
      "MoSim startup params: lidar_type=%d scan_line=%d blind=%.3f scan_rate=%d point_filter_pre=%d point_filter=%d base_frame='%s' map_frame='%s' lidar_frame='%s' imu_frame='%s'",
      preprocessor_->lidar_type,
      preprocessor_->N_SCANS,
      preprocessor_->blind,
      preprocessor_->SCAN_RATE,
      preprocessor_->point_filter_num,
      point_filter_num_,
      base_frame_.c_str(),
      map_frame_.c_str(),
      lidar_frame_.c_str(),
      imu_frame_.c_str());

  if (preprocessor_->point_filter_num <= 0) {
    RCLCPP_WARN(this->get_logger(), "Invalid point_filter_num_for_preprocessing=%d; forcing 1.", preprocessor_->point_filter_num);
    preprocessor_->point_filter_num = 1;
  }
  if (point_filter_num_ <= 0) {
    RCLCPP_WARN(this->get_logger(), "Invalid point_filter_num=%d; forcing 1.", point_filter_num_);
    point_filter_num_ = 1;
  }

  main_loop_timer_ =
      create_wall_timer(std::chrono::milliseconds(1), std::bind(&SPARKFastLIO2::main, this));

  if ((preprocessor_->point_filter_num != 1 && point_filter_num_ > 1)) {""",
    )
    standard_pattern = re.compile(
        r"void SPARKFastLIO2::standardLiDARCallback\(const sensor_msgs::msg::PointCloud2 &msg\) \{.*?\n\}",
        re.DOTALL,
    )
    standard_replacement = """void SPARKFastLIO2::standardLiDARCallback(const sensor_msgs::msg::PointCloud2 &msg) {
  std::lock_guard<std::mutex> lk(buffer_mutex_);
  scan_count_++;
  rclcpp::Time msg_time = msg.header.stamp;

  if (msg_time < last_lidar_timestamp_) {
    RCLCPP_ERROR(get_logger(), "Lidar loopback detected, clearing buffers");
    lidar_buffer_.clear();
  }
  last_lidar_timestamp_ = msg_time;

  PointCloudXYZI::Ptr ptr(new PointCloudXYZI());
  preprocessor_->process(msg, ptr);
  RCLCPP_INFO_THROTTLE(
      this->get_logger(),
      *clock_,
      2000,
      "Standard LiDAR callback: stamp=%.6f input_width=%u preprocessed=%zu",
      msg_time.seconds(),
      msg.width,
      ptr->size());

  lidar_buffer_.push_back(ptr);
  time_buffer_.push_back(msg_time.seconds());

  sig_buffer_.notify_all();
}"""
    text, count = standard_pattern.subn(standard_replacement, text, count=1)
    if count != 1:
        raise SystemExit("failed to patch standardLiDARCallback block")

    livox_pattern = re.compile(
        r"void SPARKFastLIO2::livoxLiDARCallback\(\n"
        r"    const livox_ros_driver2::msg::CustomMsg::ConstSharedPtr msg\) \{.*?\n\}",
        re.DOTALL,
    )
    livox_replacement = """void SPARKFastLIO2::livoxLiDARCallback(
    const livox_ros_driver2::msg::CustomMsg::ConstSharedPtr msg) {
  static bool timediff_set_flg = false;

  std::lock_guard<std::mutex> lk(buffer_mutex_);
  scan_count_++;
  rclcpp::Time msg_time = msg->header.stamp;

  if (msg_time < last_lidar_timestamp_) {
    RCLCPP_ERROR(get_logger(), "Livox loopback, clearing buffers");
    lidar_buffer_.clear();
  }
  last_lidar_timestamp_ = msg_time;

  const auto diff_s = std::abs((last_imu_timestamp_ - last_lidar_timestamp_).seconds());
  if (!time_sync_en_ && diff_s > 10.0 && !imu_buffer_.empty() && !lidar_buffer_.empty()) {
    RCLCPP_WARN_STREAM(this->get_logger(),
                       "IMU and LiDAR not Synced, IMU time: "
                           << last_imu_timestamp_.nanoseconds()
                           << ", lidar header time: " << last_lidar_timestamp_.nanoseconds());
  }

  if (time_sync_en_ && !timediff_set_flg && diff_s > 1.0 && !imu_buffer_.empty()) {
    timediff_set_flg        = true;
    timediff_lidar_wrt_imu_ = last_lidar_timestamp_.nanoseconds() + static_cast<int64_t>(1.0e8) -
                              last_imu_timestamp_.nanoseconds();
    RCLCPP_INFO_STREAM(
        this->get_logger(),
        "Self sync IMU and LiDAR, time diff is " << timediff_lidar_wrt_imu_ << "[ns]");
  }

  PointCloudXYZI::Ptr ptr(new PointCloudXYZI());
  RCLCPP_INFO_THROTTLE(
      this->get_logger(),
      *clock_,
      1000,
      "Livox LiDAR callback entry: stamp=%.6f point_num=%u points_size=%zu",
      msg_time.seconds(),
      msg->point_num,
      msg->points.size());
  preprocessor_->process(*msg, ptr);
  RCLCPP_INFO_THROTTLE(
      this->get_logger(),
      *clock_,
      2000,
      "Livox LiDAR callback: stamp=%.6f point_num=%u preprocessed=%zu first_offset=%u last_offset=%u",
      msg_time.seconds(),
      msg->point_num,
      ptr->size(),
      msg->points.empty() ? 0u : msg->points.front().offset_time,
      msg->points.empty() ? 0u : msg->points.back().offset_time);

  lidar_buffer_.push_back(ptr);
  time_buffer_.push_back(msg_time.seconds());

  sig_buffer_.notify_all();
}"""
    text, count = livox_pattern.subn(livox_replacement, text, count=1)
    if count != 1:
        raise SystemExit("failed to patch livoxLiDARCallback block")
    text = text.replace(
        """  sub_lidar_      = create_subscription<sensor_msgs::msg::PointCloud2>(
      "lidar",
      lidar_qos,
      std::bind(&SPARKFastLIO2::standardLiDARCallback, this, std::placeholders::_1));

#if defined(LIVOX_ROS_DRIVER_FOUND) && LIVOX_ROS_DRIVER_FOUND
  sub_lidar_livox_ = create_subscription<livox_ros_driver2::msg::CustomMsg>(
      "lidar",
      lidar_qos,
      std::bind(&SPARKFastLIO2::livoxLiDARCallback, this, std::placeholders::_1));
#endif""",
        """#if defined(LIVOX_ROS_DRIVER_FOUND) && LIVOX_ROS_DRIVER_FOUND
  sub_lidar_livox_ = create_subscription<livox_ros_driver2::msg::CustomMsg>(
      "lidar",
      lidar_qos,
      std::bind(&SPARKFastLIO2::livoxLiDARCallback, this, std::placeholders::_1));
#else
  sub_lidar_      = create_subscription<sensor_msgs::msg::PointCloud2>(
      "lidar",
      lidar_qos,
      std::bind(&SPARKFastLIO2::standardLiDARCallback, this, std::placeholders::_1));
#endif""",
    )
    text = remove_regex_block(
        text,
        r"\n  RCLCPP_INFO_THROTTLE\(\n      this->get_logger\(\),\n      \*clock_,\n      2000,\n      \"Process LiDAR/IMU: input=%zu imu=%zu cloud_undistort=%zu point_filter=%d lidar_dt=%.6f\",.*?Measures\.lidar_end_time - Measures\.lidar_beg_time\);\n",
    )
    text = text.replace(
        "  imu_processor_->Process(Measures, kf_, cloud_undistort_);  feats_undistort_->reserve(cloud_undistort_->size() / point_filter_num_);",
        "  imu_processor_->Process(Measures, kf_, cloud_undistort_);\n  feats_undistort_->reserve(cloud_undistort_->size() / point_filter_num_);",
    )
    text = replace_once(
        text,
        """  imu_processor_->Process(Measures, kf_, cloud_undistort_);
  feats_undistort_->reserve(cloud_undistort_->size() / point_filter_num_);""",
        """  imu_processor_->Process(Measures, kf_, cloud_undistort_);
  RCLCPP_INFO_THROTTLE(
      this->get_logger(),
      *clock_,
      2000,
      "Process LiDAR/IMU: input=%zu imu=%zu cloud_undistort=%zu point_filter=%d lidar_dt=%.6f",
      Measures.lidar ? Measures.lidar->size() : 0,
      Measures.imu.size(),
      cloud_undistort_->size(),
      point_filter_num_,
      Measures.lidar_end_time - Measures.lidar_beg_time);
  feats_undistort_->reserve(cloud_undistort_->size() / point_filter_num_);""",
        "process LiDAR/IMU diagnostics block",
    )
    return write_if_changed(path, text)


def patch_candidate(candidate: Path) -> dict[str, object]:
    required = [
        candidate / "package.xml",
        candidate / "CMakeLists.txt",
        candidate / "include/preprocess.h",
        candidate / "src/preprocess.cpp",
        candidate / "src/spark_fast_lio.cpp",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit("missing spark-fast-lio files: " + ", ".join(missing))
    changes = {
        "package.xml": patch_package_xml(candidate / "package.xml"),
        "CMakeLists.txt": patch_cmake(candidate / "CMakeLists.txt"),
        "include/preprocess.h": patch_preprocess_h(candidate / "include/preprocess.h"),
        "src/preprocess.cpp": patch_preprocess_cpp(candidate / "src/preprocess.cpp"),
        "src/spark_fast_lio.cpp": patch_spark_cpp(candidate / "src/spark_fast_lio.cpp"),
    }
    return {
        "candidate": str(candidate.relative_to(ROOT)),
        "changed_files": [name for name, changed in changes.items() if changed],
        "unchanged_files": [name for name, changed in changes.items() if not changed],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, default=DEFAULT_CANDIDATE)
    args = parser.parse_args()
    result = patch_candidate(project_path(args.candidate))
    import json

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
