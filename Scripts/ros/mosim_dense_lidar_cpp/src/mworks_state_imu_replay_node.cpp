#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <fstream>
#include <iostream>
#include <map>
#include <memory>
#include <sstream>
#include <string>
#include <vector>

#include "geometry_msgs/msg/transform_stamped.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/imu.hpp"
#include "tf2_ros/transform_broadcaster.h"

namespace {

struct Row {
  double time{0.0};
  double x{0.0};
  double y{0.0};
  double z{0.0};
  double roll{0.0};
  double pitch{0.0};
  double yaw{0.0};
};

std::vector<std::string> split_csv_line(const std::string& line) {
  std::vector<std::string> out;
  std::stringstream stream(line);
  std::string item;
  while (std::getline(stream, item, ',')) {
    out.push_back(item);
  }
  return out;
}

std::vector<Row> read_rows(const std::string& path, const int max_rows) {
  std::ifstream input(path);
  if (!input) {
    throw std::runtime_error("unable to open MWORKS CSV: " + path);
  }
  std::string header_line;
  if (!std::getline(input, header_line)) {
    throw std::runtime_error("empty MWORKS CSV: " + path);
  }
  const auto headers = split_csv_line(header_line);
  std::map<std::string, size_t> index;
  for (size_t i = 0; i < headers.size(); ++i) {
    index[headers[i]] = i;
  }
  for (const char* key : {"time", "x", "y", "z", "roll", "pitch", "yaw"}) {
    if (index.find(key) == index.end()) {
      throw std::runtime_error(std::string("MWORKS CSV missing column: ") + key);
    }
  }
  std::vector<Row> rows;
  std::string line;
  while (std::getline(input, line)) {
    if (line.empty()) {
      continue;
    }
    const auto fields = split_csv_line(line);
    auto get = [&](const std::string& key) -> double {
      const size_t pos = index.at(key);
      if (pos >= fields.size() || fields[pos].empty()) {
        return 0.0;
      }
      return std::stod(fields[pos]);
    };
    rows.push_back({get("time"), get("x"), get("y"), get("z"), get("roll"), get("pitch"), get("yaw")});
    if (max_rows > 0 && static_cast<int>(rows.size()) >= max_rows) {
      break;
    }
  }
  if (rows.size() < 2) {
    throw std::runtime_error("MWORKS CSV needs at least two data rows: " + path);
  }
  return rows;
}

std::array<double, 4> quaternion_from_rpy(const double roll, const double pitch, const double yaw) {
  const double cy = std::cos(yaw * 0.5);
  const double sy = std::sin(yaw * 0.5);
  const double cp = std::cos(pitch * 0.5);
  const double sp = std::sin(pitch * 0.5);
  const double cr = std::cos(roll * 0.5);
  const double sr = std::sin(roll * 0.5);
  return {
    sr * cp * cy - cr * sp * sy,
    cr * sp * cy + sr * cp * sy,
    cr * cp * sy - sr * sp * cy,
    cr * cp * cy + sr * sp * sy,
  };
}

Row interpolate(const Row& left, const Row& right, double alpha) {
  alpha = std::max(0.0, std::min(1.0, alpha));
  const double beta = 1.0 - alpha;
  return {
    left.time * beta + right.time * alpha,
    left.x * beta + right.x * alpha,
    left.y * beta + right.y * alpha,
    left.z * beta + right.z * alpha,
    left.roll * beta + right.roll * alpha,
    left.pitch * beta + right.pitch * alpha,
    left.yaw * beta + right.yaw * alpha,
  };
}

double finite_diff(const std::vector<Row>& rows, const size_t index, double Row::*field) {
  size_t left_index = 0;
  size_t right_index = 1;
  if (index == 0) {
    left_index = 0;
    right_index = 1;
  } else if (index >= rows.size() - 1) {
    left_index = rows.size() - 2;
    right_index = rows.size() - 1;
  } else {
    left_index = index - 1;
    right_index = index + 1;
  }
  const double dt = rows[right_index].time - rows[left_index].time;
  if (std::abs(dt) < 1.0e-9) {
    return 0.0;
  }
  return (rows[right_index].*field - rows[left_index].*field) / dt;
}

double second_finite_diff(const std::vector<Row>& rows, const size_t index, double Row::*field) {
  if (rows.size() < 3) {
    return 0.0;
  }
  const size_t center = std::min(index, rows.size() - 1);
  const size_t left_index = (center == 0) ? 0 : center - 1;
  const size_t right_index = (center >= rows.size() - 1) ? rows.size() - 1 : center + 1;
  if (left_index == center || right_index == center) {
    return 0.0;
  }
  const double dt_left = rows[center].time - rows[left_index].time;
  const double dt_right = rows[right_index].time - rows[center].time;
  const double dt_span = rows[right_index].time - rows[left_index].time;
  if (std::abs(dt_left) < 1.0e-9 || std::abs(dt_right) < 1.0e-9 || std::abs(dt_span) < 1.0e-9) {
    return 0.0;
  }
  const double v_left = (rows[center].*field - rows[left_index].*field) / dt_left;
  const double v_right = (rows[right_index].*field - rows[center].*field) / dt_right;
  return 2.0 * (v_right - v_left) / dt_span;
}

}  // namespace

class MworksStateImuReplayNode final : public rclcpp::Node {
 public:
  MworksStateImuReplayNode() : Node("mosim_mworks_state_imu_replay_node") {
    const std::string csv_path = declare_parameter<std::string>("mworks_raw_csv", "");
    world_frame_ = declare_parameter<std::string>("world_frame", "ue_world");
    body_frame_ = declare_parameter<std::string>("body_frame", "base_link");
    imu_frame_ = declare_parameter<std::string>("imu_frame", "base/forward_imu_optical_frame");
    imu_topic_ = declare_parameter<std::string>("imu_topic", "/mosim/forward/imu");
    odom_topic_ = declare_parameter<std::string>("truth_odom_topic", "/mosim/truth/odometry");
    imu_rate_hz_ = declare_parameter<double>("imu_rate_hz", 200.0);
    truth_rate_hz_ = declare_parameter<double>("truth_rate_hz", 20.0);
    const int max_rows = declare_parameter<int>("max_rows", 0);
    stats_interval_s_ = declare_parameter<double>("stats_interval_s", 5.0);
    if (csv_path.empty()) {
      throw std::runtime_error("parameter mworks_raw_csv is required");
    }
    if (imu_rate_hz_ <= 0.0 || truth_rate_hz_ <= 0.0) {
      throw std::runtime_error("imu_rate_hz and truth_rate_hz must be positive");
    }
    rows_ = read_rows(csv_path, max_rows);
    truth_stride_ = std::max<size_t>(1, static_cast<size_t>(std::llround(imu_rate_hz_ / truth_rate_hz_)));
    auto qos = rclcpp::QoS(rclcpp::KeepLast(64)).reliable();
    imu_pub_ = create_publisher<sensor_msgs::msg::Imu>(imu_topic_, qos);
    odom_pub_ = create_publisher<nav_msgs::msg::Odometry>(odom_topic_, qos);
    tf_broadcaster_ = std::make_unique<tf2_ros::TransformBroadcaster>(*this);
    stats_start_ = std::chrono::steady_clock::now();
    const auto period = std::chrono::duration<double>(1.0 / imu_rate_hz_);
    timer_ = create_wall_timer(std::chrono::duration_cast<std::chrono::nanoseconds>(period), [this]() { tick(); });
    RCLCPP_INFO(
      get_logger(),
      "publishing MWORKS state IMU from %zu rows to %s at %.2f Hz, truth odom to %s at %.2f Hz",
      rows_.size(),
      imu_topic_.c_str(),
      imu_rate_hz_,
      odom_topic_.c_str(),
      truth_rate_hz_);
  }

 private:
  void tick() {
    const size_t base_index = std::min(tick_count_ / truth_stride_, rows_.size() - 1);
    const size_t next_index = std::min(base_index + 1, rows_.size() - 1);
    const double alpha = static_cast<double>(tick_count_ % truth_stride_) / static_cast<double>(truth_stride_);
    const Row row = interpolate(rows_[base_index], rows_[next_index], alpha);
    const auto stamp = now();
    imu_pub_->publish(make_imu(row, base_index, stamp));
    imu_count_++;
    if ((tick_count_ % truth_stride_) == 0) {
      publish_tf(row, stamp);
      odom_pub_->publish(make_odom(row, base_index, stamp));
      odom_count_++;
    }
    tick_count_++;
    maybe_log_stats(std::chrono::steady_clock::now());
  }

  sensor_msgs::msg::Imu make_imu(const Row& row, const size_t index, const rclcpp::Time& stamp) const {
    sensor_msgs::msg::Imu imu;
    imu.header.stamp = stamp;
    imu.header.frame_id = imu_frame_;
    const auto q = quaternion_from_rpy(row.roll, row.pitch, row.yaw);
    imu.orientation.x = q[0];
    imu.orientation.y = q[1];
    imu.orientation.z = q[2];
    imu.orientation.w = q[3];
    imu.angular_velocity.x = finite_diff(rows_, index, &Row::roll);
    imu.angular_velocity.y = finite_diff(rows_, index, &Row::pitch);
    imu.angular_velocity.z = finite_diff(rows_, index, &Row::yaw);
    imu.linear_acceleration.x = second_finite_diff(rows_, index, &Row::x);
    imu.linear_acceleration.y = second_finite_diff(rows_, index, &Row::y);
    imu.linear_acceleration.z = second_finite_diff(rows_, index, &Row::z) + 9.81;
    return imu;
  }

  nav_msgs::msg::Odometry make_odom(const Row& row, const size_t index, const rclcpp::Time& stamp) const {
    nav_msgs::msg::Odometry odom;
    odom.header.stamp = stamp;
    odom.header.frame_id = world_frame_;
    odom.child_frame_id = body_frame_;
    const auto q = quaternion_from_rpy(row.roll, row.pitch, row.yaw);
    odom.pose.pose.position.x = row.x;
    odom.pose.pose.position.y = row.y;
    odom.pose.pose.position.z = row.z;
    odom.pose.pose.orientation.x = q[0];
    odom.pose.pose.orientation.y = q[1];
    odom.pose.pose.orientation.z = q[2];
    odom.pose.pose.orientation.w = q[3];
    odom.twist.twist.linear.x = finite_diff(rows_, index, &Row::x);
    odom.twist.twist.linear.y = finite_diff(rows_, index, &Row::y);
    odom.twist.twist.linear.z = finite_diff(rows_, index, &Row::z);
    odom.twist.twist.angular.x = finite_diff(rows_, index, &Row::roll);
    odom.twist.twist.angular.y = finite_diff(rows_, index, &Row::pitch);
    odom.twist.twist.angular.z = finite_diff(rows_, index, &Row::yaw);
    return odom;
  }

  void publish_tf(const Row& row, const rclcpp::Time& stamp) {
    geometry_msgs::msg::TransformStamped transform;
    transform.header.stamp = stamp;
    transform.header.frame_id = world_frame_;
    transform.child_frame_id = body_frame_;
    const auto q = quaternion_from_rpy(row.roll, row.pitch, row.yaw);
    transform.transform.translation.x = row.x;
    transform.transform.translation.y = row.y;
    transform.transform.translation.z = row.z;
    transform.transform.rotation.x = q[0];
    transform.transform.rotation.y = q[1];
    transform.transform.rotation.z = q[2];
    transform.transform.rotation.w = q[3];
    tf_broadcaster_->sendTransform(transform);
  }

  void maybe_log_stats(const std::chrono::steady_clock::time_point& now_time) {
    if (stats_interval_s_ <= 0.0) {
      return;
    }
    const double elapsed_s = std::chrono::duration<double>(now_time - stats_start_).count();
    if (elapsed_s < stats_interval_s_) {
      return;
    }
    RCLCPP_INFO(
      get_logger(),
      "mworks_state_stats imu=%zu odom=%zu elapsed_s=%.3f imu_rate_hz=%.3f odom_rate_hz=%.3f",
      imu_count_,
      odom_count_,
      elapsed_s,
      static_cast<double>(imu_count_) / elapsed_s,
      static_cast<double>(odom_count_) / elapsed_s);
    imu_count_ = 0;
    odom_count_ = 0;
    stats_start_ = now_time;
  }

  std::string world_frame_;
  std::string body_frame_;
  std::string imu_frame_;
  std::string imu_topic_;
  std::string odom_topic_;
  double imu_rate_hz_{200.0};
  double truth_rate_hz_{20.0};
  double stats_interval_s_{5.0};
  size_t truth_stride_{10};
  size_t tick_count_{0};
  size_t imu_count_{0};
  size_t odom_count_{0};
  std::chrono::steady_clock::time_point stats_start_;
  std::vector<Row> rows_;
  rclcpp::Publisher<sensor_msgs::msg::Imu>::SharedPtr imu_pub_;
  rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr odom_pub_;
  std::unique_ptr<tf2_ros::TransformBroadcaster> tf_broadcaster_;
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  try {
    rclcpp::spin(std::make_shared<MworksStateImuReplayNode>());
  } catch (const std::exception& exc) {
    std::cerr << exc.what() << std::endl;
    rclcpp::shutdown();
    return 1;
  }
  rclcpp::shutdown();
  return 0;
}
