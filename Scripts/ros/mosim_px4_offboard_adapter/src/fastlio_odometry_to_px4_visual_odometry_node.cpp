#include <array>
#include <cmath>
#include <cstdint>
#include <limits>
#include <string>

#include "nav_msgs/msg/odometry.hpp"
#include "px4_msgs/msg/vehicle_odometry.hpp"
#include "rclcpp/rclcpp.hpp"

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

std::array<double, 4> normalize_quat(double w, double x, double y, double z) {
  const double norm = std::sqrt(w * w + x * x + y * y + z * z);
  if (!std::isfinite(norm) || norm <= 1e-9) {
    return {1.0, 0.0, 0.0, 0.0};
  }
  return {w / norm, x / norm, y / norm, z / norm};
}

std::array<double, 3> quat_to_rpy(const std::array<double, 4>& q) {
  const double w = q[0];
  const double x = q[1];
  const double y = q[2];
  const double z = q[3];

  const double sinr_cosp = 2.0 * (w * x + y * z);
  const double cosr_cosp = 1.0 - 2.0 * (x * x + y * y);
  const double roll = std::atan2(sinr_cosp, cosr_cosp);

  const double sinp = 2.0 * (w * y - z * x);
  const double pitch = std::abs(sinp) >= 1.0 ? std::copysign(kPi / 2.0, sinp) : std::asin(sinp);

  const double siny_cosp = 2.0 * (w * z + x * y);
  const double cosy_cosp = 1.0 - 2.0 * (y * y + z * z);
  const double yaw = std::atan2(siny_cosp, cosy_cosp);
  return {roll, pitch, yaw};
}

std::array<double, 4> rpy_to_quat(double roll, double pitch, double yaw) {
  const double cr = std::cos(roll * 0.5);
  const double sr = std::sin(roll * 0.5);
  const double cp = std::cos(pitch * 0.5);
  const double sp = std::sin(pitch * 0.5);
  const double cy = std::cos(yaw * 0.5);
  const double sy = std::sin(yaw * 0.5);
  return normalize_quat(
      cr * cp * cy + sr * sp * sy,
      sr * cp * cy - cr * sp * sy,
      cr * sp * cy + sr * cp * sy,
      cr * cp * sy - sr * sp * cy);
}

std::array<float, 4> enu_quat_to_ned_quat(const geometry_msgs::msg::Quaternion& input) {
  const auto enu = normalize_quat(input.w, input.x, input.y, input.z);
  const auto rpy = quat_to_rpy(enu);
  const auto ned = rpy_to_quat(rpy[1], rpy[0], wrap_pi((kPi / 2.0) - rpy[2]));
  return {
      static_cast<float>(ned[0]),
      static_cast<float>(ned[1]),
      static_cast<float>(ned[2]),
      static_cast<float>(ned[3]),
  };
}

float covariance_or_default(const std::array<double, 36>& covariance, int index, float fallback) {
  const double value = covariance[static_cast<std::size_t>(index)];
  if (std::isfinite(value) && value > 0.0) {
    return static_cast<float>(value);
  }
  return fallback;
}

}  // namespace

class FastlioOdometryToPx4VisualOdometryNode final : public rclcpp::Node {
 public:
  FastlioOdometryToPx4VisualOdometryNode() : Node("mosim_fastlio_odometry_to_px4_visual_odometry_node") {
    input_topic_ = declare_parameter<std::string>("input_topic", "/odometry");
    output_topic_ = declare_parameter<std::string>("output_topic", "/fmu/in/vehicle_visual_odometry");
    expected_frame_ = declare_parameter<std::string>("expected_frame", "map");
    pose_frame_ = static_cast<std::uint8_t>(declare_parameter<int>("pose_frame", px4_msgs::msg::VehicleOdometry::POSE_FRAME_NED));
    velocity_frame_ = static_cast<std::uint8_t>(declare_parameter<int>("velocity_frame", px4_msgs::msg::VehicleOdometry::VELOCITY_FRAME_NED));
    publish_orientation_ = declare_parameter<bool>("publish_orientation", false);
    publish_velocity_ = declare_parameter<bool>("publish_velocity", true);
    position_variance_ = declare_parameter<double>("position_variance", 0.0025);
    velocity_variance_ = declare_parameter<double>("velocity_variance", 0.01);
    orientation_variance_ = declare_parameter<double>("orientation_variance", 0.05);
    quality_ = static_cast<int8_t>(declare_parameter<int>("quality", 100));

    visual_odom_pub_ = create_publisher<px4_msgs::msg::VehicleOdometry>(output_topic_, rclcpp::QoS(rclcpp::KeepLast(10)).best_effort());
    fastlio_odom_sub_ = create_subscription<nav_msgs::msg::Odometry>(
        input_topic_,
        rclcpp::QoS(rclcpp::KeepLast(10)).best_effort(),
        [this](nav_msgs::msg::Odometry::SharedPtr message) { on_odometry(*message); });
  }

 private:
  void on_odometry(const nav_msgs::msg::Odometry& input) {
    if (!expected_frame_.empty() && input.header.frame_id != expected_frame_) {
      RCLCPP_WARN_THROTTLE(
          get_logger(),
          *get_clock(),
          2000,
          "Dropping FAST-LIO odometry frame '%s'; expected '%s'",
          input.header.frame_id.c_str(),
          expected_frame_.c_str());
      return;
    }

    px4_msgs::msg::VehicleOdometry output{};
    output.timestamp = timestamp_us();
    output.timestamp_sample = output.timestamp;
    output.pose_frame = pose_frame_;
    output.velocity_frame = velocity_frame_;

    output.position = {
        static_cast<float>(input.pose.pose.position.y),
        static_cast<float>(input.pose.pose.position.x),
        static_cast<float>(-input.pose.pose.position.z),
    };

    if (publish_orientation_) {
      output.q = enu_quat_to_ned_quat(input.pose.pose.orientation);
      output.orientation_variance = {
          covariance_or_default(input.pose.covariance, 21, static_cast<float>(orientation_variance_)),
          covariance_or_default(input.pose.covariance, 28, static_cast<float>(orientation_variance_)),
          covariance_or_default(input.pose.covariance, 35, static_cast<float>(orientation_variance_)),
      };
    } else {
      output.q = {nanf(), nanf(), nanf(), nanf()};
      output.orientation_variance = {
          static_cast<float>(orientation_variance_),
          static_cast<float>(orientation_variance_),
          static_cast<float>(orientation_variance_),
      };
    }

    if (publish_velocity_) {
      output.velocity = {
          static_cast<float>(input.twist.twist.linear.y),
          static_cast<float>(input.twist.twist.linear.x),
          static_cast<float>(-input.twist.twist.linear.z),
      };
      output.velocity_variance = {
          covariance_or_default(input.twist.covariance, 7, static_cast<float>(velocity_variance_)),
          covariance_or_default(input.twist.covariance, 0, static_cast<float>(velocity_variance_)),
          covariance_or_default(input.twist.covariance, 14, static_cast<float>(velocity_variance_)),
      };
    } else {
      output.velocity = {nanf(), nanf(), nanf()};
      output.velocity_variance = {
          static_cast<float>(velocity_variance_),
          static_cast<float>(velocity_variance_),
          static_cast<float>(velocity_variance_),
      };
    }

    output.angular_velocity = {nanf(), nanf(), nanf()};
    output.position_variance = {
        covariance_or_default(input.pose.covariance, 7, static_cast<float>(position_variance_)),
        covariance_or_default(input.pose.covariance, 0, static_cast<float>(position_variance_)),
        covariance_or_default(input.pose.covariance, 14, static_cast<float>(position_variance_)),
    };
    output.reset_counter = 0;
    output.quality = quality_;
    visual_odom_pub_->publish(output);
    ++published_count_;
    RCLCPP_DEBUG(get_logger(), "Published PX4 visual odometry sample %zu", published_count_);
  }

  std::uint64_t timestamp_us() {
    return static_cast<std::uint64_t>(get_clock()->now().nanoseconds() / 1000);
  }

  std::string input_topic_;
  std::string output_topic_;
  std::string expected_frame_;
  std::uint8_t pose_frame_{px4_msgs::msg::VehicleOdometry::POSE_FRAME_NED};
  std::uint8_t velocity_frame_{px4_msgs::msg::VehicleOdometry::VELOCITY_FRAME_NED};
  bool publish_orientation_{false};
  bool publish_velocity_{true};
  double position_variance_{0.0025};
  double velocity_variance_{0.01};
  double orientation_variance_{0.05};
  int8_t quality_{100};
  std::size_t published_count_{0};
  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr fastlio_odom_sub_;
  rclcpp::Publisher<px4_msgs::msg::VehicleOdometry>::SharedPtr visual_odom_pub_;
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<FastlioOdometryToPx4VisualOdometryNode>());
  rclcpp::shutdown();
  return 0;
}
