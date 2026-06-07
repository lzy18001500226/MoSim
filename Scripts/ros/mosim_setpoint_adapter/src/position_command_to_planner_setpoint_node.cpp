#include <algorithm>
#include <cstdint>
#include <string>

#include "mosim_msgs/msg/planner_setpoint.hpp"
#include "mosim_msgs/msg/position_command.hpp"
#include "rclcpp/rclcpp.hpp"

class PositionCommandToPlannerSetpointNode final : public rclcpp::Node {
 public:
  PositionCommandToPlannerSetpointNode() : Node("mosim_position_command_to_planner_setpoint_node") {
    input_topic_ = declare_parameter<std::string>("input_topic", "/position_cmd");
    output_topic_ = declare_parameter<std::string>("output_topic", "/mosim/planner/position_cmd");
    expected_frame_ = declare_parameter<std::string>("expected_frame", "map");
    source_frame_alias_ = declare_parameter<std::string>("source_frame_alias", "world");
    planner_id_ = declare_parameter<std::string>("planner_id", "ego_position_cmd");

    auto qos = rclcpp::QoS(rclcpp::KeepLast(16)).reliable();
    output_pub_ = create_publisher<mosim_msgs::msg::PlannerSetpoint>(output_topic_, qos);
    input_sub_ = create_subscription<mosim_msgs::msg::PositionCommand>(
        input_topic_,
        qos,
        [this](mosim_msgs::msg::PositionCommand::SharedPtr message) { on_command(*message); });
  }

 private:
  void on_command(const mosim_msgs::msg::PositionCommand& command) {
    const std::string source_frame = command.header.frame_id.empty() ? expected_frame_ : command.header.frame_id;
    if (source_frame != expected_frame_ && source_frame != source_frame_alias_) {
      RCLCPP_WARN_THROTTLE(
          get_logger(),
          *get_clock(),
          2000,
          "Dropping PositionCommand with frame_id '%s'; expected '%s' or alias '%s'",
          source_frame.c_str(),
          expected_frame_.c_str(),
          source_frame_alias_.c_str());
      return;
    }

    mosim_msgs::msg::PlannerSetpoint setpoint;
    setpoint.header = command.header;
    setpoint.header.frame_id = expected_frame_;
    setpoint.sequence = next_sequence(command.trajectory_id);
    setpoint.frame_id = expected_frame_;
    setpoint.position_m = {command.position.x, command.position.y, command.position.z};
    setpoint.velocity_mps = {command.velocity.x, command.velocity.y, command.velocity.z};
    setpoint.acceleration_mps2 = {command.acceleration.x, command.acceleration.y, command.acceleration.z};
    setpoint.yaw_rad = command.yaw;
    setpoint.yaw_rate_radps = command.yaw_dot;
    setpoint.trajectory_status = command.trajectory_flag;
    setpoint.planner_id = planner_id_;
    output_pub_->publish(setpoint);
  }

  std::uint32_t next_sequence(std::uint32_t trajectory_id) {
    if (trajectory_id > last_trajectory_id_) {
      last_trajectory_id_ = trajectory_id;
      last_sequence_ = std::max(last_sequence_ + 1, trajectory_id);
    } else {
      ++last_sequence_;
    }
    return last_sequence_;
  }

  std::string input_topic_;
  std::string output_topic_;
  std::string expected_frame_;
  std::string source_frame_alias_;
  std::string planner_id_;
  std::uint32_t last_trajectory_id_{0};
  std::uint32_t last_sequence_{0};
  rclcpp::Subscription<mosim_msgs::msg::PositionCommand>::SharedPtr input_sub_;
  rclcpp::Publisher<mosim_msgs::msg::PlannerSetpoint>::SharedPtr output_pub_;
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<PositionCommandToPlannerSetpointNode>());
  rclcpp::shutdown();
  return 0;
}
