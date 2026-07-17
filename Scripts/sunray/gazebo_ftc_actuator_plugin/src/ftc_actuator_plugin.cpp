#include <algorithm>
#include <array>
#include <cmath>
#include <functional>
#include <memory>
#include <mutex>
#include <string>

#include <gazebo/common/Plugin.hh>
#include <gazebo/gazebo.hh>
#include <gazebo/physics/physics.hh>
#include <ros/ros.h>
#include <std_msgs/Float64MultiArray.h>

namespace gazebo {

class MosimFtcActuatorPlugin final : public ModelPlugin {
 public:
  void Load(physics::ModelPtr model, sdf::ElementPtr sdf) override {
    model_ = std::move(model);
    if (!ros::isInitialized()) {
      gzerr << "[mosim_ftc_actuator] ROS is not initialized\n";
      return;
    }

    const std::string robot_namespace =
        sdf->HasElement("robotNamespace")
            ? sdf->Get<std::string>("robotNamespace")
            : std::string("/uav1");
    command_topic_ = sdf->HasElement("commandTopic")
                         ? sdf->Get<std::string>("commandTopic")
                         : robot_namespace + "/mosim/ftc_actuator_command";
    telemetry_topic_ = sdf->HasElement("telemetryTopic")
                           ? sdf->Get<std::string>("telemetryTopic")
                           : robot_namespace + "/mosim/ftc_actuator_telemetry";
    max_rot_velocity_ = sdf->HasElement("maxRotVelocity")
                            ? sdf->Get<double>("maxRotVelocity")
                            : 1500.0;
    slowdown_ = sdf->HasElement("rotorVelocitySlowdownSim")
                    ? sdf->Get<double>("rotorVelocitySlowdownSim")
                    : 10.0;

    for (std::size_t rotor = 0; rotor < joints_.size(); ++rotor) {
      joints_[rotor] = model_->GetJoint("rotor_" + std::to_string(rotor) + "_joint");
      if (!joints_[rotor]) {
        gzerr << "[mosim_ftc_actuator] missing rotor joint " << rotor << "\n";
        return;
      }
    }

    node_.reset(new ros::NodeHandle(robot_namespace));
    command_sub_ = node_->subscribe(command_topic_, 5,
                                    &MosimFtcActuatorPlugin::CommandCallback, this);
    telemetry_pub_ = node_->advertise<std_msgs::Float64MultiArray>(telemetry_topic_, 10);
    spinner_.reset(new ros::AsyncSpinner(1));
    spinner_->start();
    update_connection_ = event::Events::ConnectWorldUpdateEnd(
        std::bind(&MosimFtcActuatorPlugin::OnUpdate, this));
    loaded_ = true;
  }

 private:
  void CommandCallback(const std_msgs::Float64MultiArray::ConstPtr& msg) {
    if (msg->data.size() != 9) {
      ROS_ERROR_THROTTLE(1.0, "FTC actuator command must contain 9 values");
      return;
    }
    std::lock_guard<std::mutex> lock(command_mutex_);
    override_enabled_ = msg->data[0] >= 0.5;
    for (std::size_t rotor = 0; rotor < 4; ++rotor) {
      effectiveness_[rotor] = Clamp(msg->data[1 + rotor], 0.0, 1.0);
      override_command_[rotor] = Clamp(msg->data[5 + rotor], 0.0, 1.0);
    }
  }

  void OnUpdate() {
    if (!loaded_) return;
    std::array<double, 4> eta;
    std::array<double, 4> override_command;
    bool override_enabled;
    {
      std::lock_guard<std::mutex> lock(command_mutex_);
      eta = effectiveness_;
      override_command = override_command_;
      override_enabled = override_enabled_;
    }

    std_msgs::Float64MultiArray telemetry;
    telemetry.data.resize(18, 0.0);
    telemetry.data[0] = model_->GetWorld()->SimTime().Double();
    for (std::size_t rotor = 0; rotor < 4; ++rotor) {
      const double raw_joint_velocity = joints_[rotor]->GetVelocity(0);
      const double sign = raw_joint_velocity < 0.0 ? -1.0 : 1.0;
      const double raw_command = Clamp(std::abs(raw_joint_velocity) * slowdown_ /
                                           max_rot_velocity_,
                                       0.0, 1.0);
      const double selected_command = override_enabled ? override_command[rotor]
                                                       : raw_command;
      const double physical_speed = selected_command * std::sqrt(eta[rotor]);
      joints_[rotor]->SetVelocity(
          0, sign * physical_speed * max_rot_velocity_ / slowdown_);
      telemetry.data[1 + rotor] = raw_command;
      telemetry.data[5 + rotor] = physical_speed;
      telemetry.data[9 + rotor] = selected_command * eta[rotor];
      telemetry.data[13 + rotor] = eta[rotor];
    }
    telemetry.data[17] = override_enabled ? 1.0 : 0.0;
    telemetry_pub_.publish(telemetry);
  }

  static double Clamp(double value, double lower, double upper) {
    return std::max(lower, std::min(value, upper));
  }

  physics::ModelPtr model_;
  std::array<physics::JointPtr, 4> joints_{};
  event::ConnectionPtr update_connection_;
  std::unique_ptr<ros::NodeHandle> node_;
  ros::Subscriber command_sub_;
  ros::Publisher telemetry_pub_;
  std::unique_ptr<ros::AsyncSpinner> spinner_;
  std::mutex command_mutex_;
  std::array<double, 4> effectiveness_{{1.0, 1.0, 1.0, 1.0}};
  std::array<double, 4> override_command_{{0.0, 0.0, 0.0, 0.0}};
  bool override_enabled_{false};
  bool loaded_{false};
  double max_rot_velocity_{1500.0};
  double slowdown_{10.0};
  std::string command_topic_;
  std::string telemetry_topic_;
};

GZ_REGISTER_MODEL_PLUGIN(MosimFtcActuatorPlugin)
}  // namespace gazebo
