#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <limits>
#include <stdexcept>
#include <string>

extern "C" {
#include "AWFF_PositionOuterLoop_Sysblock.h"
#include "AWFF_PositionOuterLoop_Sysblock_private.h"
}

#include "mosim_msgs/msg/planner_setpoint.hpp"
#include "px4_msgs/msg/offboard_control_mode.hpp"
#include "px4_msgs/msg/vehicle_attitude_setpoint.hpp"
#include "px4_msgs/msg/vehicle_command.hpp"
#include "px4_msgs/msg/vehicle_local_position.hpp"
#include "rclcpp/rclcpp.hpp"

using namespace std::chrono_literals;

namespace {

constexpr double kPi = 3.14159265358979323846;

double clamp(double value, double low, double high) {
  return std::max(low, std::min(high, value));
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

std::array<float, 4> euler_to_quat(double roll, double pitch, double yaw) {
  const double cr = std::cos(roll * 0.5);
  const double sr = std::sin(roll * 0.5);
  const double cp = std::cos(pitch * 0.5);
  const double sp = std::sin(pitch * 0.5);
  const double cy = std::cos(yaw * 0.5);
  const double sy = std::sin(yaw * 0.5);
  return {
      static_cast<float>(cr * cp * cy + sr * sp * sy),
      static_cast<float>(sr * cp * cy - cr * sp * sy),
      static_cast<float>(cr * sp * cy + sr * cp * sy),
      static_cast<float>(cr * cp * sy - sr * sp * cy),
  };
}

}  // namespace

class PositionOuterLoopToPx4AttitudeNode final : public rclcpp::Node {
 public:
  PositionOuterLoopToPx4AttitudeNode() : Node("mosim_position_outer_loop_to_px4_attitude_node") {
    setpoint_topic_ = declare_parameter<std::string>("setpoint_topic", "/mosim/planner/setpoint");
    local_position_topic_ = declare_parameter<std::string>("local_position_topic", "/fmu/out/vehicle_local_position");
    attitude_setpoint_topic_ = declare_parameter<std::string>("attitude_setpoint_topic", "/fmu/in/vehicle_attitude_setpoint_v1");
    expected_frame_ = declare_parameter<std::string>("expected_frame", "map");
    publish_rate_hz_ = declare_parameter<double>("publish_rate_hz", 20.0);
    stale_timeout_s_ = declare_parameter<double>("stale_timeout_s", 0.5);
    max_tilt_rad_ = declare_parameter<double>("max_tilt_rad", 0.35);
    hover_thrust_ = declare_parameter<double>("hover_thrust", 0.55);
    thrust_scale_ = declare_parameter<double>("thrust_scale", 0.20);
    min_thrust_ = declare_parameter<double>("min_thrust", 0.10);
    max_thrust_ = declare_parameter<double>("max_thrust", 0.85);
    x_error_sign_ = declare_parameter<double>("x_error_sign", 1.0);
    y_error_sign_ = declare_parameter<double>("y_error_sign", 1.0);
    xy_velocity_damping_s_ = declare_parameter<double>("xy_velocity_damping_s", 0.0);
    z_velocity_damping_s_ = declare_parameter<double>("z_velocity_damping_s", 0.0);
    roll_output_sign_ = declare_parameter<double>("roll_output_sign", -1.0);
    pitch_output_sign_ = declare_parameter<double>("pitch_output_sign", 1.0);
    auto_arm_ = declare_parameter<bool>("auto_arm", false);
    auto_offboard_ = declare_parameter<bool>("auto_offboard", false);
    arm_first_ = declare_parameter<bool>("arm_first", true);
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
    if (min_thrust_ < 0.0 || max_thrust_ > 1.0 || min_thrust_ >= max_thrust_) {
      throw std::runtime_error("thrust limits must satisfy 0 <= min < max <= 1");
    }
    if (warmup_setpoint_count_ < 10) {
      throw std::runtime_error("warmup_setpoint_count must be at least 10");
    }

    Init();

    auto qos = rclcpp::QoS(rclcpp::KeepLast(10)).best_effort();
    offboard_pub_ = create_publisher<px4_msgs::msg::OffboardControlMode>("/fmu/in/offboard_control_mode", qos);
    attitude_pub_ = create_publisher<px4_msgs::msg::VehicleAttitudeSetpoint>(attitude_setpoint_topic_, qos);
    command_pub_ = create_publisher<px4_msgs::msg::VehicleCommand>("/fmu/in/vehicle_command", qos);

    setpoint_sub_ = create_subscription<mosim_msgs::msg::PlannerSetpoint>(
        setpoint_topic_,
        rclcpp::QoS(rclcpp::KeepLast(16)).reliable(),
        [this](mosim_msgs::msg::PlannerSetpoint::SharedPtr message) { on_setpoint(*message); });
    local_position_sub_ = create_subscription<px4_msgs::msg::VehicleLocalPosition>(
        local_position_topic_,
        qos,
        [this](px4_msgs::msg::VehicleLocalPosition::SharedPtr message) { on_local_position(*message); });

    const auto period = std::chrono::duration<double>(1.0 / publish_rate_hz_);
    timer_ = create_wall_timer(std::chrono::duration_cast<std::chrono::nanoseconds>(period), [this]() { on_timer(); });
  }

 private:
  void on_setpoint(const mosim_msgs::msg::PlannerSetpoint& message) {
    const std::string frame = message.frame_id.empty() ? message.header.frame_id : message.frame_id;
    if (!expected_frame_.empty() && frame != expected_frame_) {
      RCLCPP_WARN_THROTTLE(get_logger(), *get_clock(), 2000, "Dropping setpoint frame '%s'; expected '%s'", frame.c_str(), expected_frame_.c_str());
      return;
    }
    latest_setpoint_ = message;
    latest_setpoint_time_ = now();
    have_setpoint_ = true;
  }

  void on_local_position(const px4_msgs::msg::VehicleLocalPosition& message) {
    if (!message.xy_valid || !message.z_valid) {
      return;
    }
    latest_position_ = message;
    latest_position_time_ = now();
    have_position_ = true;
  }

  void on_timer() {
    publish_offboard_control_mode();
    if (!have_setpoint_ || !have_position_) {
      return;
    }
    const double setpoint_age_s = (now() - latest_setpoint_time_).seconds();
    const double position_age_s = (now() - latest_position_time_).seconds();
    if (setpoint_age_s > stale_timeout_s_ || position_age_s > stale_timeout_s_) {
      RCLCPP_WARN_THROTTLE(
          get_logger(),
          *get_clock(),
          2000,
          "Holding Offboard heartbeat but dropping stale attitude setpoint; setpoint age %.3fs, position age %.3fs",
          setpoint_age_s,
          position_age_s);
      return;
    }

    const double vx_enu = static_cast<double>(latest_position_.vy);
    const double vy_enu = static_cast<double>(latest_position_.vx);
    const double vz_enu = static_cast<double>(-latest_position_.vz);
    const double x_error = latest_setpoint_.position_m[0] - static_cast<double>(latest_position_.y);
    const double y_error = latest_setpoint_.position_m[1] - static_cast<double>(latest_position_.x);
    const double z_error = latest_setpoint_.position_m[2] - static_cast<double>(-latest_position_.z);
    lockGbIn.x_error = x_error_sign_ * (x_error - xy_velocity_damping_s_ * vx_enu);
    lockGbIn.y_error = y_error_sign_ * (y_error - xy_velocity_damping_s_ * vy_enu);
    lockGbIn.z_error = z_error - z_velocity_damping_s_ * vz_enu;
    lockGbIn.z_ref_rate = latest_setpoint_.velocity_mps[2];
    Step();

    const double pitch_ref = clamp(blockGbOut.pitch_ref, -max_tilt_rad_, max_tilt_rad_);
    const double roll_ref = clamp(blockGbOut.roll_ref, -max_tilt_rad_, max_tilt_rad_);
    const double yaw_ned = wrap_pi((kPi / 2.0) - latest_setpoint_.yaw_rad);
    const double thrust = clamp(hover_thrust_ + thrust_scale_ * blockGbOut.thrust_ref, min_thrust_, max_thrust_);

    px4_msgs::msg::VehicleAttitudeSetpoint attitude{};
    attitude.timestamp = timestamp_us();
    attitude.yaw_sp_move_rate = static_cast<float>(-latest_setpoint_.yaw_rate_radps);
    attitude.q_d = euler_to_quat(roll_output_sign_ * roll_ref, pitch_output_sign_ * pitch_ref, yaw_ned);
    attitude.thrust_body = {0.0F, 0.0F, static_cast<float>(-thrust)};
    attitude_pub_->publish(attitude);
    ++published_setpoint_count_;

    if (published_setpoint_count_ >= static_cast<std::uint64_t>(warmup_setpoint_count_)) {
      if (arm_first_) {
        if (!arm_command_sent_ && auto_arm_) {
          publish_vehicle_command(px4_msgs::msg::VehicleCommand::VEHICLE_CMD_COMPONENT_ARM_DISARM, 1.0F);
          arm_command_sent_ = true;
        }
        if (!mode_command_sent_ && auto_offboard_ && (!auto_arm_ || arm_command_sent_)) {
          publish_vehicle_command(px4_msgs::msg::VehicleCommand::VEHICLE_CMD_DO_SET_MODE, 1.0F, 6.0F);
          mode_command_sent_ = true;
        }
      } else {
        if (!mode_command_sent_ && auto_offboard_) {
          publish_vehicle_command(px4_msgs::msg::VehicleCommand::VEHICLE_CMD_DO_SET_MODE, 1.0F, 6.0F);
          mode_command_sent_ = true;
        }
        if (!arm_command_sent_ && auto_arm_ && mode_command_sent_) {
          publish_vehicle_command(px4_msgs::msg::VehicleCommand::VEHICLE_CMD_COMPONENT_ARM_DISARM, 1.0F);
          arm_command_sent_ = true;
        }
      }
    }
  }

  void publish_offboard_control_mode() {
    px4_msgs::msg::OffboardControlMode message{};
    message.timestamp = timestamp_us();
    message.position = false;
    message.velocity = false;
    message.acceleration = false;
    message.attitude = true;
    message.body_rate = false;
    message.thrust_and_torque = false;
    message.direct_actuator = false;
    offboard_pub_->publish(message);
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

  std::string setpoint_topic_;
  std::string local_position_topic_;
  std::string attitude_setpoint_topic_;
  std::string expected_frame_;
  double publish_rate_hz_{20.0};
  double stale_timeout_s_{0.5};
  double max_tilt_rad_{0.35};
  double hover_thrust_{0.55};
  double thrust_scale_{0.20};
  double min_thrust_{0.10};
  double max_thrust_{0.85};
  double x_error_sign_{1.0};
  double y_error_sign_{1.0};
  double xy_velocity_damping_s_{0.0};
  double z_velocity_damping_s_{0.0};
  double roll_output_sign_{-1.0};
  double pitch_output_sign_{1.0};
  bool auto_arm_{false};
  bool auto_offboard_{false};
  bool arm_first_{true};
  int warmup_setpoint_count_{20};
  std::uint8_t target_system_{1};
  std::uint8_t target_component_{1};
  std::uint8_t source_system_{1};
  std::uint16_t source_component_{1};
  bool have_setpoint_{false};
  bool have_position_{false};
  bool mode_command_sent_{false};
  bool arm_command_sent_{false};
  std::uint64_t published_setpoint_count_{0};
  rclcpp::Time latest_setpoint_time_{0, 0, RCL_ROS_TIME};
  rclcpp::Time latest_position_time_{0, 0, RCL_ROS_TIME};
  mosim_msgs::msg::PlannerSetpoint latest_setpoint_{};
  px4_msgs::msg::VehicleLocalPosition latest_position_{};
  rclcpp::Subscription<mosim_msgs::msg::PlannerSetpoint>::SharedPtr setpoint_sub_;
  rclcpp::Subscription<px4_msgs::msg::VehicleLocalPosition>::SharedPtr local_position_sub_;
  rclcpp::Publisher<px4_msgs::msg::OffboardControlMode>::SharedPtr offboard_pub_;
  rclcpp::Publisher<px4_msgs::msg::VehicleAttitudeSetpoint>::SharedPtr attitude_pub_;
  rclcpp::Publisher<px4_msgs::msg::VehicleCommand>::SharedPtr command_pub_;
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<PositionOuterLoopToPx4AttitudeNode>());
  rclcpp::shutdown();
  return 0;
}
