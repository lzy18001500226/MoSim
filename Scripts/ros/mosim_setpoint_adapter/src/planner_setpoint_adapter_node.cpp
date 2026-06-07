#include <array>
#include <algorithm>
#include <chrono>
#include <cmath>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>

#include "mosim_msgs/msg/planner_setpoint.hpp"
#include "mosim_msgs/msg/setpoint_adapter_status.hpp"
#include "rclcpp/rclcpp.hpp"

namespace {

bool finite_array(const std::array<double, 3>& values) {
  return std::isfinite(values[0]) && std::isfinite(values[1]) && std::isfinite(values[2]);
}

}  // namespace

class PlannerSetpointAdapterNode final : public rclcpp::Node {
 public:
  PlannerSetpointAdapterNode() : Node("mosim_planner_setpoint_adapter_node") {
    input_topic_ = declare_parameter<std::string>("input_topic", "/mosim/planner/position_cmd");
    output_topic_ = declare_parameter<std::string>("output_topic", "/mosim/planner/setpoint");
    status_topic_ = declare_parameter<std::string>("status_topic", "/mosim/planner/setpoint_adapter_status");
    expected_frame_ = declare_parameter<std::string>("expected_frame", "map");
    rate_hz_ = declare_parameter<double>("rate_hz", 20.0);
    stale_timeout_s_ = declare_parameter<double>("stale_timeout_s", 0.15);
    if (rate_hz_ <= 0.0 || stale_timeout_s_ <= 0.0) {
      throw std::runtime_error("rate_hz and stale_timeout_s must be positive");
    }

    auto qos = rclcpp::QoS(rclcpp::KeepLast(16)).reliable();
    output_pub_ = create_publisher<mosim_msgs::msg::PlannerSetpoint>(output_topic_, qos);
    status_pub_ = create_publisher<mosim_msgs::msg::SetpointAdapterStatus>(status_topic_, qos);
    input_sub_ = create_subscription<mosim_msgs::msg::PlannerSetpoint>(
        input_topic_,
        qos,
        [this](mosim_msgs::msg::PlannerSetpoint::SharedPtr message) { on_command(*message); });

    const auto period = std::chrono::duration<double>(1.0 / rate_hz_);
    timer_ = create_wall_timer(
        std::chrono::duration_cast<std::chrono::nanoseconds>(period),
        [this]() { publish_tick(); });
  }

 private:
  void on_command(const mosim_msgs::msg::PlannerSetpoint& message) {
    latest_status_.last_sequence = message.sequence;
    latest_status_.planner_id = message.planner_id;
    latest_status_.mode = "reject";
    latest_status_.accepted = false;
    latest_status_.stale = false;
    latest_status_.age_s = 0.0;

    if (message.frame_id != expected_frame_) {
      latest_status_.reject_reason = "frame_id_mismatch";
      return;
    }
    if (!finite_array(message.position_m) || !finite_array(message.velocity_mps) ||
        !finite_array(message.acceleration_mps2) || !std::isfinite(message.yaw_rad) ||
        !std::isfinite(message.yaw_rate_radps)) {
      latest_status_.reject_reason = "non_finite_setpoint";
      return;
    }
    if (has_latest_ && rclcpp::Time(message.header.stamp) <= rclcpp::Time(latest_command_.header.stamp)) {
      latest_status_.reject_reason = "non_monotonic_stamp";
      return;
    }
    if (has_latest_ && message.sequence <= latest_command_.sequence) {
      latest_status_.reject_reason = "non_monotonic_sequence";
      return;
    }

    latest_command_ = message;
    has_latest_ = true;
    latest_status_.accepted = true;
    latest_status_.mode = "track";
    latest_status_.reject_reason = "";
  }

  void publish_tick() {
    const auto now = this->now();
    mosim_msgs::msg::SetpointAdapterStatus status = latest_status_;
    status.header.stamp = now;
    status.header.frame_id = expected_frame_;

    if (!has_latest_) {
      status.accepted = false;
      status.stale = true;
      status.mode = "hold";
      status.reject_reason = "no_command";
      status.age_s = 0.0;
      status_pub_->publish(status);
      return;
    }

    const double age = (now - latest_command_.header.stamp).seconds();
    const bool stale = age > stale_timeout_s_;
    status.age_s = std::max(0.0, age);
    status.stale = stale;
    if (stale) {
      status.accepted = false;
      status.mode = "hold";
      status.reject_reason = "stale_command";
      status_pub_->publish(status);
      return;
    }

    mosim_msgs::msg::PlannerSetpoint setpoint = latest_command_;
    setpoint.header.stamp = now;
    setpoint.header.frame_id = expected_frame_;
    setpoint.frame_id = expected_frame_;
    output_pub_->publish(setpoint);

    status.accepted = true;
    status.mode = "track";
    status.reject_reason = "";
    status_pub_->publish(status);
  }

  std::string input_topic_;
  std::string output_topic_;
  std::string status_topic_;
  std::string expected_frame_;
  double rate_hz_{20.0};
  double stale_timeout_s_{0.15};

  bool has_latest_{false};
  mosim_msgs::msg::PlannerSetpoint latest_command_;
  mosim_msgs::msg::SetpointAdapterStatus latest_status_;
  rclcpp::Subscription<mosim_msgs::msg::PlannerSetpoint>::SharedPtr input_sub_;
  rclcpp::Publisher<mosim_msgs::msg::PlannerSetpoint>::SharedPtr output_pub_;
  rclcpp::Publisher<mosim_msgs::msg::SetpointAdapterStatus>::SharedPtr status_pub_;
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  try {
    rclcpp::spin(std::make_shared<PlannerSetpointAdapterNode>());
  } catch (const std::exception& exc) {
    std::cerr << "planner_setpoint_adapter_node failed: " << exc.what() << std::endl;
    rclcpp::shutdown();
    return 1;
  }
  rclcpp::shutdown();
  return 0;
}
