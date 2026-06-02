#include <chrono>
#include <cstdint>
#include <fstream>
#include <memory>
#include <regex>
#include <string>
#include <vector>

#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/point_cloud2.hpp"
#include "sensor_msgs/msg/point_field.hpp"
#include "std_msgs/msg/header.hpp"

namespace {

struct Frame {
  std::vector<std::array<float, 6>> points;
  sensor_msgs::msg::PointCloud2 message;
};

std::vector<Frame> read_frames(const std::string& path, const int max_frames) {
  std::ifstream input(path);
  if (!input) {
    throw std::runtime_error("unable to open lidar JSONL: " + path);
  }
  std::regex point_pattern(R"(\[\s*(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\s*,\s*(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\s*,\s*(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\s*\])");
  std::vector<Frame> frames;
  std::string line;
  while (std::getline(input, line)) {
    if (line.find("\"points_m\"") == std::string::npos) {
      continue;
    }
    const auto key_pos = line.find("\"points_m\"");
    const auto array_start = line.find('[', key_pos);
    const auto attrs_pos = line.find("\"point_attributes\"", key_pos);
    const auto array_end = attrs_pos == std::string::npos ? line.rfind(']') : line.rfind(']', attrs_pos);
    if (array_start == std::string::npos || array_end == std::string::npos || array_end <= array_start) {
      throw std::runtime_error("invalid points_m array in " + path);
    }
    const std::string points_text = line.substr(array_start, array_end - array_start + 1);
    Frame frame;
    for (std::sregex_iterator it(points_text.begin(), points_text.end(), point_pattern), end; it != end; ++it) {
      const auto& match = *it;
      const float x = std::stof(match[1].str());
      const float y = std::stof(match[2].str());
      const float z = std::stof(match[3].str());
      const float index = static_cast<float>(frame.points.size());
      frame.points.push_back({x, y, z, 100.0F, index, std::fmod(index, 4.0F)});
    }
    frames.push_back(std::move(frame));
    if (max_frames > 0 && static_cast<int>(frames.size()) >= max_frames) {
      break;
    }
  }
  if (frames.empty()) {
    throw std::runtime_error("no frames parsed from " + path);
  }
  return frames;
}

void append_float(std::vector<uint8_t>& data, const float value) {
  const auto* bytes = reinterpret_cast<const uint8_t*>(&value);
  data.insert(data.end(), bytes, bytes + sizeof(float));
}

sensor_msgs::msg::PointCloud2 make_cloud_template(const Frame& frame, const std::string& frame_id) {
  sensor_msgs::msg::PointCloud2 msg;
  msg.header.frame_id = frame_id;
  msg.height = 1;
  msg.width = static_cast<uint32_t>(frame.points.size());
  msg.is_bigendian = false;
  msg.is_dense = true;
  msg.point_step = 24;
  msg.row_step = msg.point_step * msg.width;
  msg.fields.resize(6);
  const std::array<std::string, 6> names = {"x", "y", "z", "intensity", "time", "ring"};
  for (size_t i = 0; i < names.size(); ++i) {
    msg.fields[i].name = names[i];
    msg.fields[i].offset = static_cast<uint32_t>(i * 4);
    msg.fields[i].datatype = sensor_msgs::msg::PointField::FLOAT32;
    msg.fields[i].count = 1;
  }
  msg.data.reserve(static_cast<size_t>(msg.row_step));
  for (const auto& point : frame.points) {
    for (float value : point) {
      append_float(msg.data, value);
    }
  }
  return msg;
}

}  // namespace

class DenseLidarReplayNode final : public rclcpp::Node {
 public:
  DenseLidarReplayNode() : Node("mosim_dense_lidar_replay_node") {
    const std::string lidar_jsonl = declare_parameter<std::string>("lidar_jsonl", "");
    topic_ = declare_parameter<std::string>("topic", "/mosim/lidar_points");
    frame_id_ = declare_parameter<std::string>("frame_id", "base/velodyne_link");
    rate_hz_ = declare_parameter<double>("rate_hz", 10.0);
    stats_interval_s_ = declare_parameter<double>("stats_interval_s", 5.0);
    const int max_frames = declare_parameter<int>("max_frames", 0);
    if (lidar_jsonl.empty()) {
      throw std::runtime_error("parameter lidar_jsonl is required");
    }
    if (rate_hz_ <= 0.0) {
      throw std::runtime_error("rate_hz must be positive");
    }
    frames_ = read_frames(lidar_jsonl, max_frames);
    for (auto& frame : frames_) {
      frame.message = make_cloud_template(frame, frame_id_);
    }
    publisher_ = create_publisher<sensor_msgs::msg::PointCloud2>(topic_, rclcpp::SensorDataQoS());
    const auto period = std::chrono::duration<double>(1.0 / rate_hz_);
    stats_start_ = std::chrono::steady_clock::now();
    timer_ = create_wall_timer(std::chrono::duration_cast<std::chrono::nanoseconds>(period), [this]() {
      const Frame& frame = frames_[index_ % frames_.size()];
      auto msg = frame.message;
      msg.header.stamp = now();
      const auto before = std::chrono::steady_clock::now();
      publisher_->publish(msg);
      const auto after = std::chrono::steady_clock::now();
      publish_count_++;
      publish_time_total_us_ += std::chrono::duration<double, std::micro>(after - before).count();
      index_++;
      maybe_log_stats(after);
    });
    RCLCPP_INFO(
      get_logger(),
      "publishing %zu dense LiDAR frames to %s at %.2f Hz; first frame has %zu points",
      frames_.size(),
      topic_.c_str(),
      rate_hz_,
      frames_.front().points.size());
  }

 private:
  void maybe_log_stats(const std::chrono::steady_clock::time_point& now_time) {
    if (stats_interval_s_ <= 0.0) {
      return;
    }
    const double elapsed_s = std::chrono::duration<double>(now_time - stats_start_).count();
    if (elapsed_s < stats_interval_s_) {
      return;
    }
    const double rate = static_cast<double>(publish_count_) / elapsed_s;
    const double mean_publish_us = publish_time_total_us_ / std::max<size_t>(1, publish_count_);
    RCLCPP_INFO(
      get_logger(),
      "dense_lidar_stats publishes=%zu elapsed_s=%.3f rate_hz=%.3f mean_publish_us=%.1f",
      publish_count_,
      elapsed_s,
      rate,
      mean_publish_us);
    publish_count_ = 0;
    publish_time_total_us_ = 0.0;
    stats_start_ = now_time;
  }

  std::string topic_;
  std::string frame_id_;
  double rate_hz_{10.0};
  double stats_interval_s_{5.0};
  size_t index_{0};
  size_t publish_count_{0};
  double publish_time_total_us_{0.0};
  std::chrono::steady_clock::time_point stats_start_;
  std::vector<Frame> frames_;
  rclcpp::Publisher<sensor_msgs::msg::PointCloud2>::SharedPtr publisher_;
  rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  try {
    rclcpp::spin(std::make_shared<DenseLidarReplayNode>());
  } catch (const std::exception& exc) {
    std::cerr << exc.what() << std::endl;
    rclcpp::shutdown();
    return 1;
  }
  rclcpp::shutdown();
  return 0;
}
