#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <iostream>
#include <set>
#include <string>

#include "livox_ros_driver2/msg/custom_msg.hpp"
#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/imu.hpp"

namespace {

double stamp_seconds(const builtin_interfaces::msg::Time& stamp) {
  return static_cast<double>(stamp.sec) + static_cast<double>(stamp.nanosec) * 1e-9;
}

double rate_from_count(const size_t count, const std::chrono::steady_clock::duration elapsed) {
  const double elapsed_s = std::chrono::duration<double>(elapsed).count();
  if (count < 2 || elapsed_s <= 0.0) {
    return 0.0;
  }
  return static_cast<double>(count - 1) / elapsed_s;
}

}  // namespace

class LivoxImuProbeNode final : public rclcpp::Node {
 public:
  LivoxImuProbeNode() : Node("mosim_livox_imu_probe_node") {
    livox_topic_ = declare_parameter<std::string>("livox_topic", "/mosim/livox/lidar");
    imu_topic_ = declare_parameter<std::string>("imu_topic", "/mosim/forward/imu");
    duration_s_ = declare_parameter<double>("duration_s", 5.0);
    min_points_ = declare_parameter<int>("min_points", 15000);
    min_livox_rate_hz_ = declare_parameter<double>("min_livox_rate_hz", 8.0);
    min_imu_rate_hz_ = declare_parameter<double>("min_imu_rate_hz", 150.0);
    max_latest_time_delta_s_ = declare_parameter<double>("max_latest_time_delta_s", 0.2);
    if (duration_s_ <= 0.0) {
      throw std::runtime_error("duration_s must be positive");
    }

    const auto qos = rclcpp::QoS(rclcpp::KeepLast(128)).reliable();
    livox_sub_ = create_subscription<livox_ros_driver2::msg::CustomMsg>(
      livox_topic_,
      qos,
      [this](livox_ros_driver2::msg::CustomMsg::ConstSharedPtr msg) {
        on_livox(*msg);
      });
    imu_sub_ = create_subscription<sensor_msgs::msg::Imu>(
      imu_topic_,
      qos,
      [this](sensor_msgs::msg::Imu::ConstSharedPtr msg) {
        on_imu(*msg);
      });
    start_time_ = std::chrono::steady_clock::now();
    timer_ = create_wall_timer(std::chrono::milliseconds(50), [this]() {
      if (std::chrono::duration<double>(std::chrono::steady_clock::now() - start_time_).count() >= duration_s_) {
        print_report();
        rclcpp::shutdown();
      }
    });
    RCLCPP_INFO(
      get_logger(),
      "probing Livox %s and IMU %s for %.2fs",
      livox_topic_.c_str(),
      imu_topic_.c_str(),
      duration_s_);
  }

  bool passed() const {
    return livox_count_ > 0
      && imu_count_ > 0
      && min_point_num_ >= static_cast<uint32_t>(std::max(0, min_points_))
      && bad_point_num_frames_ == 0
      && livox_stamps_monotonic_
      && imu_stamps_monotonic_
      && livox_rate_hz_ >= min_livox_rate_hz_
      && imu_rate_hz_ >= min_imu_rate_hz_
      && std::abs(latest_livox_stamp_s_ - latest_imu_stamp_s_) <= max_latest_time_delta_s_;
  }

 private:
  void on_livox(const livox_ros_driver2::msg::CustomMsg& msg) {
    if (livox_count_ == 0) {
      livox_start_time_ = std::chrono::steady_clock::now();
      min_point_num_ = msg.point_num;
      max_point_num_ = msg.point_num;
    } else if (stamp_seconds(msg.header.stamp) + 1.0e-9 < latest_livox_stamp_s_) {
      livox_stamps_monotonic_ = false;
    }
    latest_livox_stamp_s_ = stamp_seconds(msg.header.stamp);
    min_point_num_ = std::min<uint32_t>(min_point_num_, msg.point_num);
    max_point_num_ = std::max<uint32_t>(max_point_num_, msg.point_num);
    if (msg.point_num != msg.points.size()) {
      bad_point_num_frames_++;
    }
    if (!msg.points.empty()) {
      min_offset_us_ = std::min<uint32_t>(min_offset_us_, msg.points.front().offset_time);
      max_offset_us_ = std::max<uint32_t>(max_offset_us_, msg.points.back().offset_time);
      const size_t sample_count = std::min<size_t>(msg.points.size(), 4096);
      for (size_t i = 0; i < sample_count; ++i) {
        observed_lines_.insert(static_cast<int>(msg.points[i].line));
        observed_tags_.insert(static_cast<int>(msg.points[i].tag));
      }
    }
    livox_count_++;
  }

  void on_imu(const sensor_msgs::msg::Imu& msg) {
    if (imu_count_ == 0) {
      imu_start_time_ = std::chrono::steady_clock::now();
    } else if (stamp_seconds(msg.header.stamp) + 1.0e-9 < latest_imu_stamp_s_) {
      imu_stamps_monotonic_ = false;
    }
    latest_imu_stamp_s_ = stamp_seconds(msg.header.stamp);
    imu_count_++;
  }

  void print_report() {
    const auto now = std::chrono::steady_clock::now();
    livox_rate_hz_ = rate_from_count(livox_count_, now - livox_start_time_);
    imu_rate_hz_ = rate_from_count(imu_count_, now - imu_start_time_);
    std::cout
      << "{\"schema\":\"mosim.livox_imu_probe.v1\""
      << ",\"duration_seconds\":" << duration_s_
      << ",\"topics\":{\"livox\":\"" << livox_topic_ << "\",\"imu\":\"" << imu_topic_ << "\"}"
      << ",\"counts\":{\"livox\":" << livox_count_ << ",\"imu\":" << imu_count_ << "}"
      << ",\"rates_hz\":{\"livox\":" << livox_rate_hz_ << ",\"imu\":" << imu_rate_hz_ << "}"
      << ",\"time_quality\":{\"livox_stamps_monotonic\":" << (livox_stamps_monotonic_ ? "true" : "false")
      << ",\"imu_stamps_monotonic\":" << (imu_stamps_monotonic_ ? "true" : "false")
      << ",\"latest_livox_minus_imu_s\":" << (latest_livox_stamp_s_ - latest_imu_stamp_s_) << "}"
      << ",\"livox\":{\"point_num\":{\"min\":" << min_point_num_
      << ",\"max\":" << max_point_num_
      << "},\"bad_point_num_frames\":" << bad_point_num_frames_
      << ",\"offset_min_us\":" << min_offset_us_
      << ",\"offset_max_us\":" << max_offset_us_
      << ",\"observed_lines\":[";
    bool first = true;
    for (const int line : observed_lines_) {
      std::cout << (first ? "" : ",") << line;
      first = false;
    }
    std::cout << "],\"observed_tags\":[";
    first = true;
    for (const int tag : observed_tags_) {
      std::cout << (first ? "" : ",") << tag;
      first = false;
    }
    std::cout << "]}"
      << ",\"acceptance\":{\"livox_nonzero\":" << (livox_count_ > 0 ? "true" : "false")
      << ",\"imu_nonzero\":" << (imu_count_ > 0 ? "true" : "false")
      << ",\"livox_rate_ok\":" << (livox_rate_hz_ >= min_livox_rate_hz_ ? "true" : "false")
      << ",\"imu_rate_ok\":" << (imu_rate_hz_ >= min_imu_rate_hz_ ? "true" : "false")
      << ",\"time_delta_ok\":"
      << (std::abs(latest_livox_stamp_s_ - latest_imu_stamp_s_) <= max_latest_time_delta_s_ ? "true" : "false")
      << ",\"point_num_ok\":" << (min_point_num_ >= static_cast<uint32_t>(std::max(0, min_points_)) ? "true" : "false")
      << ",\"point_num_matches\":" << (bad_point_num_frames_ == 0 ? "true" : "false")
      << "}"
      << ",\"claim\":\"subscriber-side Livox CustomMsg plus IMU input gate; not FAST-LIO localization evidence\""
      << "}" << std::endl;
  }

  std::string livox_topic_;
  std::string imu_topic_;
  double duration_s_{5.0};
  int min_points_{15000};
  double min_livox_rate_hz_{8.0};
  double min_imu_rate_hz_{150.0};
  double max_latest_time_delta_s_{0.2};
  size_t livox_count_{0};
  size_t imu_count_{0};
  double latest_livox_stamp_s_{0.0};
  double latest_imu_stamp_s_{0.0};
  double livox_rate_hz_{0.0};
  double imu_rate_hz_{0.0};
  uint32_t min_point_num_{0};
  uint32_t max_point_num_{0};
  uint32_t min_offset_us_{UINT32_MAX};
  uint32_t max_offset_us_{0};
  size_t bad_point_num_frames_{0};
  bool livox_stamps_monotonic_{true};
  bool imu_stamps_monotonic_{true};
  std::set<int> observed_lines_;
  std::set<int> observed_tags_;
  std::chrono::steady_clock::time_point start_time_;
  std::chrono::steady_clock::time_point livox_start_time_;
  std::chrono::steady_clock::time_point imu_start_time_;
  rclcpp::Subscription<livox_ros_driver2::msg::CustomMsg>::SharedPtr livox_sub_;
  rclcpp::Subscription<sensor_msgs::msg::Imu>::SharedPtr imu_sub_;
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  std::shared_ptr<LivoxImuProbeNode> node;
  try {
    node = std::make_shared<LivoxImuProbeNode>();
    rclcpp::spin(node);
  } catch (const std::exception& exc) {
    std::cerr << exc.what() << std::endl;
    if (rclcpp::ok()) {
      rclcpp::shutdown();
    }
    return 1;
  }
  const bool ok = node && node->passed();
  if (rclcpp::ok()) {
    rclcpp::shutdown();
  }
  return ok ? 0 : 3;
}
