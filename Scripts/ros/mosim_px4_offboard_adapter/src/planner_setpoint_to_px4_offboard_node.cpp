#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <limits>
#include <stdexcept>
#include <string>

#include "mosim_msgs/msg/planner_setpoint.hpp"
#include "px4_msgs/msg/offboard_control_mode.hpp"
#include "px4_msgs/msg/trajectory_setpoint.hpp"
#include "px4_msgs/msg/vehicle_command.hpp"
#include "rclcpp/rclcpp.hpp"

using namespace std::chrono_literals;

namespace {

constexpr double kPi = 3.14159265358979323846;

float nanf() {
  return std::numeric_limits<float>::quiet_NaN();
}

double wrap_pi(double value) {
  while (value > kPi) {
    value -= 2.0 * kPi;
  }
  while (value < -kPi) {
    value += 2.0 * kPi;
  }
  return value;
}

struct Px4Setpoint {
  std::array<float, 3> position;
  std::array<float, 3> velocity;
  std::array<float, 3> acceleration;
  float yaw;
  float yaw_speed;
};

Px4Setpoint convert_setpoint(const mosim_msgs::msg::PlannerSetpoint& input, const std::string& frame_mode) {
  if (frame_mode == "local_ned") {
    return {
        {static_cast<float>(input.position_m[0]), static_cast<float>(input.position_m[1]), static_cast<float>(input.position_m[2])},
        {static_cast<float>(input.velocity_mps[0]), static_cast<float>(input.velocity_mps[1]), static_cast<float>(input.velocity_mps[2])},
        {static_cast<float>(input.acceleration_mps2[0]), static_cast<float>(input.acceleration_mps2[1]), static_cast<float>(input.acceleration_mps2[2])},
        static_cast<float>(wrap_pi(input.yaw_rad)),
        static_cast<float>(input.yaw_rate_radps),
    };
  }
  if (frame_mode == "enu_to_ned") {
    return {
        {static_cast<float>(input.position_m[1]), static_cast<float>(input.position_m[0]), static_cast<float>(-input.position_m[2])},
        {static_cast<float>(input.velocity_mps[1]), static_cast<float>(input.velocity_mps[0]), static_cast<float>(-input.velocity_mps[2])},
        {static_cast<float>(input.acceleration_mps2[1]), static_cast<float>(input.acceleration_mps2[0]), static_cast<float>(-input.acceleration_mps2[2])},
        static_cast<float>(wrap_pi((kPi / 2.0) - input.yaw_rad)),
        static_cast<float>(-input.yaw_rate_radps),
    };
  }
  throw std::runtime_error("frame_mode must be enu_to_ned or local_ned");
}

}  // namespace

class PlannerSetpointToPx4OffboardNode final : public rclcpp::Node {
 public:
  PlannerSetpointToPx4OffboardNode() : Node("mosim_planner_setpoint_to_px4_offboard_node") {
    input_topic_ = declare_parameter<std::string>("input_topic", "/mosim/planner/setpoint");
    expected_frame_ = declare_parameter<std::string>("expected_frame", "map");
    frame_mode_ = declare_parameter<std::string>("frame_mode", "enu_to_ned");
    planner_id_ = declare_parameter<std::string>("planner_id", "mosim_generated_controller");
    publish_rate_hz_ = declare_parameter<double>("publish_rate_hz", 20.0);
    stale_timeout_s_ = declare_parameter<double>("stale_timeout_s", 0.5);
    auto_arm_ = declare_parameter<bool>("auto_arm", false);
    auto_offboard_ = declare_parameter<bool>("auto_offboard", false);
    warmup_setpoint_count_ = declare_parameter<int>("warmup_setpoint_count", 20);
    target_system_ = static_cast<std::uint8_t>(declare_parameter<int>("target_system", 1));
    target_component_ = static_cast<std::uint8_t>(declare_parameter<int>("target_component", 1));
    source_system_ = static_cast<std::uint8_t>(declare_parameter<int>("source_system", 1));
    source_component_ = static_cast<std::uint16_t>(declare_parameter<int>("source_component", 1));

    if (publish_rate_hz_ < 5.0 || !std::isfinite(publish_rate_hz_)) {
      throw std::runtime_error("publish_rate_hz must be finite and >= 5Hz for PX4 Offboard margin");
    }
    if (stale_timeout_s_ <= 0.0 || !std::isfinite(stale_timeout_s_)) {
      throw std::runtime_error("stale_timeout_s must be finite and positive");
    }
    if (warmup_setpoint_count_ < 10) {
      throw std::runtime_error("warmup_setpoint_count must be at least 10");
    }
    (void)convert_setpoint(mosim_msgs::msg::PlannerSetpoint{}, frame_mode_);

    auto qos = rclcpp::QoS(rclcpp::KeepLast(10)).best_effort();
    offboard_pub_ = create_publisher<px4_msgs::msg::OffboardControlMode>("/fmu/in/offboard_control_mode", qos);
    setpoint_pub_ = create_publisher<px4_msgs::msg::TrajectorySetpoint>("/fmu/in/trajectory_setpoint", qos);
    command_pub_ = create_publisher<px4_msgs::msg::VehicleCommand>("/fmu/in/vehicle_command", qos);
    setpoint_sub_ = create_subscription<mosim_msgs::msg::PlannerSetpoint>(
        input_topic_,
        rclcpp::QoS(rclcpp::KeepLast(16)).reliable(),
        [this](mosim_msgs::msg::PlannerSetpoint::SharedPtr message) { on_setpoint(*message); });

    const auto period = std::chrono::duration<double>(1.0 / publish_rate_hz_);
    timer_ = create_wall_timer(std::chrono::duration_cast<std::chrono::nanoseconds>(period), [this]() { on_timer(); });
  }

 private:
  void on_setpoint(const mosim_msgs::msg::PlannerSetpoint& message) {
    const std::string frame = message.frame_id.empty() ? message.header.frame_id : message.frame_id;
    if (!expected_frame_.empty() && frame != expected_frame_) {
      RCLCPP_WARN_THROTTLE(
          get_logger(),
          *get_clock(),
          2000,
          "Dropping PlannerSetpoint frame '%s'; expected '%s'",
          frame.c_str(),
          expected_frame_.c_str());
      return;
    }
    latest_px4_setpoint_ = convert_setpoint(message, frame_mode_);
    latest_setpoint_time_ = now();
    latest_sequence_ = message.sequence;
    have_setpoint_ = true;
  }

  void on_timer() {
    publish_offboard_control_mode();
    if (!have_setpoint_) {
      return;
    }
    const double age_s = (now() - latest_setpoint_time_).seconds();
    if (age_s > stale_timeout_s_) {
      RCLCPP_WARN_THROTTLE(get_logger(), *get_clock(), 2000, "Holding Offboard heartbeat but dropping stale setpoint age %.3fs", age_s);
      return;
    }
    publish_trajectory_setpoint();
    ++published_setpoint_count_;

    if (!mode_command_sent_ && auto_offboard_ && published_setpoint_count_ >= static_cast<std::uint64_t>(warmup_setpoint_count_)) {
      publish_vehicle_command(px4_msgs::msg::VehicleCommand::VEHICLE_CMD_DO_SET_MODE, 1.0F, 6.0F);
      mode_command_sent_ = true;
    }
    if (!arm_command_sent_ && auto_arm_ && mode_command_sent_) {
      publish_vehicle_command(px4_msgs::msg::VehicleCommand::VEHICLE_CMD_COMPONENT_ARM_DISARM, 1.0F);
      arm_command_sent_ = true;
    }
  }

  void publish_offboard_control_mode() {
    px4_msgs::msg::OffboardControlMode message{};
    message.timestamp = timestamp_us();
    message.position = true;
    message.velocity = false;
    message.acceleration = false;
    message.attitude = false;
    message.body_rate = false;
    message.thrust_and_torque = false;
    message.direct_actuator = false;
    offboard_pub_->publish(message);
  }

  void publish_trajectory_setpoint() {
    px4_msgs::msg::TrajectorySetpoint message{};
    message.timestamp = timestamp_us();
    message.position = latest_px4_setpoint_.position;
    message.velocity = latest_px4_setpoint_.velocity;
    message.acceleration = latest_px4_setpoint_.acceleration;
    message.jerk = {nanf(), nanf(), nanf()};
    message.yaw = latest_px4_setpoint_.yaw;
    message.yawspeed = latest_px4_setpoint_.yaw_speed;
    setpoint_pub_->publish(message);
    RCLCPP_DEBUG(get_logger(), "Published PX4 TrajectorySetpoint from MoSim sequence %u", latest_sequence_);
  }

  void publish_vehicle_command(std::uint32_t command, float param1 = 0.0F, float param2 = 0.0F) {
    px4_msgs::msg::VehicleCommand message{};
    message.timestamp = timestamp_us();
    message.param1 = param1;
    message.param2 = param2;
    message.command = command;
    message.target_system = target_system_;
    message.target_component = target_component_;
    message.source_system = source_system_;
    message.source_component = source_component_;
    message.from_external = true;
    command_pub_->publish(message);
  }

  std::uint64_t timestamp_us() {
    return static_cast<std::uint64_t>(get_clock()->now().nanoseconds() / 1000);
  }

  std::string input_topic_;
  std::string expected_frame_;
  std::string frame_mode_;
  std::string planner_id_;
  double publish_rate_hz_{20.0};
  double stale_timeout_s_{0.5};
  bool auto_arm_{false};
  bool auto_offboard_{false};
  int warmup_setpoint_count_{20};
  std::uint8_t target_system_{1};
  std::uint8_t target_component_{1};
  std::uint8_t source_system_{1};
  std::uint16_t source_component_{1};
  bool have_setpoint_{false};
  bool mode_command_sent_{false};
  bool arm_command_sent_{false};
  std::uint32_t latest_sequence_{0};
  std::uint64_t published_setpoint_count_{0};
  rclcpp::Time latest_setpoint_time_{0, 0, RCL_ROS_TIME};
  Px4Setpoint latest_px4_setpoint_{{nanf(), nanf(), nanf()}, {nanf(), nanf(), nanf()}, {nanf(), nanf(), nanf()}, nanf(), nanf()};
  rclcpp::Subscription<mosim_msgs::msg::PlannerSetpoint>::SharedPtr setpoint_sub_;
  rclcpp::Publisher<px4_msgs::msg::OffboardControlMode>::SharedPtr offboard_pub_;
  rclcpp::Publisher<px4_msgs::msg::TrajectorySetpoint>::SharedPtr setpoint_pub_;
  rclcpp::Publisher<px4_msgs::msg::VehicleCommand>::SharedPtr command_pub_;
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<PlannerSetpointToPx4OffboardNode>());
  rclcpp::shutdown();
  return 0;
}
