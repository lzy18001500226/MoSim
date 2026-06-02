#include <algorithm>
#include <chrono>
#include <cstdint>
#include <iostream>
#include <set>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/point_cloud2.hpp"

namespace {

double stamp_seconds(const builtin_interfaces::msg::Time& stamp) {
  return static_cast<double>(stamp.sec) + static_cast<double>(stamp.nanosec) * 1e-9;
}

bool has_livox_fields(const sensor_msgs::msg::PointCloud2& msg) {
  const std::set<std::string> required = {"offset_time", "x", "y", "z", "intensity", "tag", "line"};
  std::set<std::string> found;
  for (const auto& field : msg.fields) {
    found.insert(field.name);
  }
  return std::all_of(required.begin(), required.end(), [&found](const std::string& name) {
    return found.find(name) != found.end();
  });
}

}  // namespace

class DenseLidarSubscriberProbeNode final : public rclcpp::Node {
 public:
  DenseLidarSubscriberProbeNode() : Node("mosim_dense_lidar_subscriber_probe_node") {
    topic_ = declare_parameter<std::string>("topic", "/mosim/lidar_points");
    max_messages_ = declare_parameter<int>("max_messages", 50);
    min_rate_hz_ = declare_parameter<double>("min_rate_hz", 0.0);
    require_livox_fields_ = declare_parameter<bool>("require_livox_fields", true);
    if (max_messages_ <= 0) {
      throw std::runtime_error("max_messages must be positive");
    }
    subscription_ = create_subscription<sensor_msgs::msg::PointCloud2>(
      topic_,
      rclcpp::SensorDataQoS(),
      [this](sensor_msgs::msg::PointCloud2::ConstSharedPtr msg) {
        on_message(*msg);
      });
    RCLCPP_INFO(get_logger(), "subscribing to %s for %d messages", topic_.c_str(), max_messages_);
  }

  bool passed() const {
    if (message_count_ <= 0) {
      return false;
    }
    if (require_livox_fields_ && !livox_fields_ok_) {
      return false;
    }
    if (!stamps_monotonic_) {
      return false;
    }
    if (min_rate_hz_ > 0.0 && measured_rate_hz_ < min_rate_hz_) {
      return false;
    }
    return true;
  }

 private:
  void on_message(const sensor_msgs::msg::PointCloud2& msg) {
    const auto now = std::chrono::steady_clock::now();
    if (message_count_ == 0) {
      start_time_ = now;
      first_stamp_s_ = stamp_seconds(msg.header.stamp);
      min_points_ = msg.width * msg.height;
      max_points_ = msg.width * msg.height;
      livox_fields_ok_ = has_livox_fields(msg);
      point_step_ = msg.point_step;
    } else {
      const double current_stamp_s = stamp_seconds(msg.header.stamp);
      if (current_stamp_s + 1e-9 < last_stamp_s_) {
        stamps_monotonic_ = false;
      }
      min_points_ = std::min<uint32_t>(min_points_, msg.width * msg.height);
      max_points_ = std::max<uint32_t>(max_points_, msg.width * msg.height);
      livox_fields_ok_ = livox_fields_ok_ && has_livox_fields(msg);
    }
    last_stamp_s_ = stamp_seconds(msg.header.stamp);
    message_count_++;
    if (message_count_ >= static_cast<size_t>(max_messages_)) {
      const double elapsed_s = std::chrono::duration<double>(now - start_time_).count();
      measured_rate_hz_ = message_count_ > 1 && elapsed_s > 0.0
        ? static_cast<double>(message_count_ - 1) / elapsed_s
        : 0.0;
      std::cout
        << "{\"schema\":\"mosim.dense_lidar_subscriber_probe.v1\""
        << ",\"topic\":\"" << topic_ << "\""
        << ",\"messages\":" << message_count_
        << ",\"measured_rate_hz\":" << measured_rate_hz_
        << ",\"min_points\":" << min_points_
        << ",\"max_points\":" << max_points_
        << ",\"point_step\":" << point_step_
        << ",\"livox_fields_ok\":" << (livox_fields_ok_ ? "true" : "false")
        << ",\"stamps_monotonic\":" << (stamps_monotonic_ ? "true" : "false")
        << ",\"first_stamp_s\":" << first_stamp_s_
        << ",\"last_stamp_s\":" << last_stamp_s_
        << ",\"claim\":\"subscriber-side PointCloud2 contract and throughput probe; not FAST-LIO evidence\""
        << "}" << std::endl;
      rclcpp::shutdown();
    }
  }

  std::string topic_;
  int max_messages_{50};
  double min_rate_hz_{0.0};
  bool require_livox_fields_{true};
  bool livox_fields_ok_{true};
  bool stamps_monotonic_{true};
  double first_stamp_s_{0.0};
  double last_stamp_s_{0.0};
  double measured_rate_hz_{0.0};
  uint32_t min_points_{0};
  uint32_t max_points_{0};
  uint32_t point_step_{0};
  size_t message_count_{0};
  std::chrono::steady_clock::time_point start_time_;
  rclcpp::Subscription<sensor_msgs::msg::PointCloud2>::SharedPtr subscription_;
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  std::shared_ptr<DenseLidarSubscriberProbeNode> node;
  try {
    node = std::make_shared<DenseLidarSubscriberProbeNode>();
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
  return ok ? 0 : 2;
}
