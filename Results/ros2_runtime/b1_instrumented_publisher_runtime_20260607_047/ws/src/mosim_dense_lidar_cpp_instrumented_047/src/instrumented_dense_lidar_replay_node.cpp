#include <chrono>
#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <memory>
#include <regex>
#include <sstream>
#include <string>
#include <vector>

#include "rclcpp/rclcpp.hpp"
#include "livox_ros_driver2/msg/custom_msg.hpp"
#include "livox_ros_driver2/msg/custom_point.hpp"
#include "sensor_msgs/msg/point_cloud2.hpp"
#include "sensor_msgs/msg/point_field.hpp"
#include "std_msgs/msg/header.hpp"

namespace {

struct Frame {
  int source_seq{0};
  double source_time{0.0};
  std::vector<std::array<float, 4>> points;
  sensor_msgs::msg::PointCloud2 message;
  livox_ros_driver2::msg::CustomMsg livox_message;
};

std::string json_escape(const std::string& value) {
  std::ostringstream out;
  for (const char c : value) {
    switch (c) {
      case '\\':
        out << "\\\\";
        break;
      case '"':
        out << "\\\"";
        break;
      case '\n':
        out << "\\n";
        break;
      case '\r':
        out << "\\r";
        break;
      case '\t':
        out << "\\t";
        break;
      default:
        out << c;
        break;
    }
  }
  return out.str();
}

int parse_int_field(const std::string& line, const std::string& key, const int fallback) {
  const std::regex pattern(std::string("\"") + key + R"("\s*:\s*(-?\d+))");
  std::smatch match;
  return std::regex_search(line, match, pattern) ? std::stoi(match[1].str()) : fallback;
}

double parse_double_field(const std::string& line, const std::string& key, const double fallback) {
  const std::regex pattern(std::string("\"") + key + R"("\s*:\s*(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?))");
  std::smatch match;
  return std::regex_search(line, match, pattern) ? std::stod(match[1].str()) : fallback;
}

int64_t steady_ns(const std::chrono::steady_clock::time_point& value) {
  return std::chrono::duration_cast<std::chrono::nanoseconds>(value.time_since_epoch()).count();
}

int64_t stamp_ns(const builtin_interfaces::msg::Time& stamp) {
  return static_cast<int64_t>(stamp.sec) * 1000000000LL + static_cast<int64_t>(stamp.nanosec);
}

std::string stamp_json(const builtin_interfaces::msg::Time& stamp) {
  std::ostringstream out;
  out << "{\"sec\":" << stamp.sec
      << ",\"nanosec\":" << stamp.nanosec
      << ",\"seconds\":" << (static_cast<double>(stamp.sec) + static_cast<double>(stamp.nanosec) * 1.0e-9)
      << "}";
  return out.str();
}

builtin_interfaces::msg::Time time_to_msg(const rclcpp::Time& time) {
  const int64_t ns = time.nanoseconds();
  builtin_interfaces::msg::Time out;
  out.sec = static_cast<int32_t>(ns / 1000000000LL);
  out.nanosec = static_cast<uint32_t>(ns % 1000000000LL);
  return out;
}

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
      frame.points.push_back({x, y, z, 100.0F});
    }
    frame.source_seq = parse_int_field(line, "seq", static_cast<int>(frames.size()));
    frame.source_time = parse_double_field(line, "time", static_cast<double>(frames.size()));
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

void append_uint32(std::vector<uint8_t>& data, const uint32_t value) {
  const auto* bytes = reinterpret_cast<const uint8_t*>(&value);
  data.insert(data.end(), bytes, bytes + sizeof(uint32_t));
}

void append_uint8(std::vector<uint8_t>& data, const uint8_t value) {
  data.push_back(value);
}

sensor_msgs::msg::PointCloud2 make_cloud_template(const Frame& frame, const std::string& frame_id) {
  sensor_msgs::msg::PointCloud2 msg;
  msg.header.frame_id = frame_id;
  msg.height = 1;
  msg.width = static_cast<uint32_t>(frame.points.size());
  msg.is_bigendian = false;
  msg.is_dense = true;
  msg.point_step = 22;
  msg.row_step = msg.point_step * msg.width;
  msg.fields.resize(7);
  msg.fields[0].name = "offset_time";
  msg.fields[0].offset = 0;
  msg.fields[0].datatype = sensor_msgs::msg::PointField::UINT32;
  msg.fields[0].count = 1;
  msg.fields[1].name = "x";
  msg.fields[1].offset = 4;
  msg.fields[1].datatype = sensor_msgs::msg::PointField::FLOAT32;
  msg.fields[1].count = 1;
  msg.fields[2].name = "y";
  msg.fields[2].offset = 8;
  msg.fields[2].datatype = sensor_msgs::msg::PointField::FLOAT32;
  msg.fields[2].count = 1;
  msg.fields[3].name = "z";
  msg.fields[3].offset = 12;
  msg.fields[3].datatype = sensor_msgs::msg::PointField::FLOAT32;
  msg.fields[3].count = 1;
  msg.fields[4].name = "intensity";
  msg.fields[4].offset = 16;
  msg.fields[4].datatype = sensor_msgs::msg::PointField::FLOAT32;
  msg.fields[4].count = 1;
  msg.fields[5].name = "tag";
  msg.fields[5].offset = 20;
  msg.fields[5].datatype = sensor_msgs::msg::PointField::UINT8;
  msg.fields[5].count = 1;
  msg.fields[6].name = "line";
  msg.fields[6].offset = 21;
  msg.fields[6].datatype = sensor_msgs::msg::PointField::UINT8;
  msg.fields[6].count = 1;
  msg.data.reserve(static_cast<size_t>(msg.row_step));
  const size_t count = std::max<size_t>(frame.points.size(), 1);
  for (size_t i = 0; i < frame.points.size(); ++i) {
    const auto& point = frame.points[i];
    const uint32_t offset_time = static_cast<uint32_t>(
      std::min<double>(4294967295.0, (static_cast<double>(i) / static_cast<double>(count)) * 100000000.0));
    append_uint32(msg.data, offset_time);
    append_float(msg.data, point[0]);
    append_float(msg.data, point[1]);
    append_float(msg.data, point[2]);
    append_float(msg.data, point[3]);
    append_uint8(msg.data, 0x10);
    append_uint8(msg.data, static_cast<uint8_t>(i % 4));
  }
  return msg;
}

livox_ros_driver2::msg::CustomMsg make_livox_template(
    const Frame& frame,
    const std::string& frame_id,
    const double scan_duration_s,
    const uint8_t lidar_id) {
  livox_ros_driver2::msg::CustomMsg msg;
  msg.header.frame_id = frame_id;
  msg.lidar_id = lidar_id;
  msg.point_num = static_cast<uint32_t>(frame.points.size());
  msg.rsvd = {0, 0, 0};
  msg.points.reserve(frame.points.size());
  const size_t count = std::max<size_t>(frame.points.size(), 1);
  const double scan_duration_us = std::max(1.0, scan_duration_s * 1.0e6);
  for (size_t i = 0; i < frame.points.size(); ++i) {
    const auto& point = frame.points[i];
    livox_ros_driver2::msg::CustomPoint out;
    out.offset_time = static_cast<uint32_t>(
      std::min<double>(4294967295.0, (static_cast<double>(i) / static_cast<double>(count)) * scan_duration_us));
    out.x = point[0];
    out.y = point[1];
    out.z = point[2];
    out.reflectivity = static_cast<uint8_t>(std::max<float>(0.0F, std::min<float>(255.0F, point[3])));
    out.tag = 0x10;
    out.line = static_cast<uint8_t>(i % 4);
    msg.points.push_back(out);
  }
  return msg;
}

}  // namespace

class InstrumentedDenseLidarReplayNode final : public rclcpp::Node {
 public:
  InstrumentedDenseLidarReplayNode() : Node("mosim_instrumented_dense_lidar_replay_node_047") {
    const std::string lidar_jsonl = declare_parameter<std::string>("lidar_jsonl", "");
    topic_ = declare_parameter<std::string>("topic", "/mosim/lidar_points");
    livox_topic_ = declare_parameter<std::string>("livox_topic", "");
    trace_path_ = declare_parameter<std::string>("trace_path", "");
    frame_id_ = declare_parameter<std::string>("frame_id", "base/velodyne_link");
    rate_hz_ = declare_parameter<double>("rate_hz", 10.0);
    scan_duration_s_ = declare_parameter<double>("scan_duration_s", 0.1);
    const int lidar_id = declare_parameter<int>("livox_lidar_id", 1);
    stats_interval_s_ = declare_parameter<double>("stats_interval_s", 5.0);
    const int max_frames = declare_parameter<int>("max_frames", 0);
    loop_ = declare_parameter<bool>("loop", true);
    exit_after_last_frame_ = declare_parameter<bool>("exit_after_last_frame", false);
    if (lidar_jsonl.empty()) {
      throw std::runtime_error("parameter lidar_jsonl is required");
    }
    if (rate_hz_ <= 0.0) {
      throw std::runtime_error("rate_hz must be positive");
    }
    if (scan_duration_s_ <= 0.0) {
      throw std::runtime_error("scan_duration_s must be positive");
    }
    if (trace_path_.empty()) {
      throw std::runtime_error("parameter trace_path is required for task 047 instrumentation");
    }
    trace_.open(trace_path_, std::ios::out | std::ios::trunc);
    if (!trace_) {
      throw std::runtime_error("unable to open trace_path: " + trace_path_);
    }
    frames_ = read_frames(lidar_jsonl, max_frames);
    for (auto& frame : frames_) {
      frame.message = make_cloud_template(frame, frame_id_);
      frame.livox_message = make_livox_template(
        frame,
        frame_id_,
        scan_duration_s_,
        static_cast<uint8_t>(std::max(0, std::min(255, lidar_id))));
    }
    publisher_ = create_publisher<sensor_msgs::msg::PointCloud2>(topic_, rclcpp::SensorDataQoS());
    if (!livox_topic_.empty()) {
      livox_publisher_ = create_publisher<livox_ros_driver2::msg::CustomMsg>(
        livox_topic_,
        rclcpp::QoS(rclcpp::KeepLast(20)).reliable());
    }
    const auto period = std::chrono::duration<double>(1.0 / rate_hz_);
    stats_start_ = std::chrono::steady_clock::now();
    timer_ = create_wall_timer(std::chrono::duration_cast<std::chrono::nanoseconds>(period), [this]() {
      if (!loop_ && index_ >= frames_.size()) {
        finish_non_looping_replay();
        return;
      }
      const Frame& frame = frames_[loop_ ? index_ % frames_.size() : index_];
      auto msg = frame.message;
      const auto steady_before_stamp = std::chrono::steady_clock::now();
      const size_t livox_matched_before_stamp = livox_publisher_ ? livox_publisher_->get_subscription_count() : 0;
      const auto stamp_assignment = now();
      msg.header.stamp = stamp_assignment;
      auto livox_msg = frame.livox_message;
      livox_msg.header.stamp = msg.header.stamp;
      livox_msg.timebase =
        static_cast<uint64_t>(livox_msg.header.stamp.sec) * 1000000000ULL
        + static_cast<uint64_t>(livox_msg.header.stamp.nanosec);
      const auto before = std::chrono::steady_clock::now();
      const size_t pointcloud_matched_before_publish = publisher_->get_subscription_count();
      const size_t livox_matched_before_publish = livox_publisher_ ? livox_publisher_->get_subscription_count() : 0;
      publisher_->publish(msg);
      const size_t pointcloud_emit_seq = pointcloud_emit_seq_++;
      if (livox_publisher_) {
        livox_publisher_->publish(livox_msg);
      }
      const size_t livox_emit_seq = livox_publisher_ ? livox_emit_seq_++ : 0;
      const auto after = std::chrono::steady_clock::now();
      const auto node_now_after_publish = time_to_msg(now());
      const size_t livox_matched_after_publish = livox_publisher_ ? livox_publisher_->get_subscription_count() : 0;
      publish_count_++;
      publish_time_total_us_ += std::chrono::duration<double, std::micro>(after - before).count();
      write_trace(
        frame,
        index_,
        msg.header.stamp,
        livox_msg.timebase,
        steady_before_stamp,
        before,
        after,
        node_now_after_publish,
        livox_matched_before_stamp,
        livox_matched_before_publish,
        livox_matched_after_publish,
        pointcloud_matched_before_publish,
        pointcloud_emit_seq,
        livox_emit_seq);
      index_++;
      maybe_log_stats(after);
      if (!loop_ && index_ >= frames_.size()) {
        finish_non_looping_replay();
      }
    });
    RCLCPP_INFO(
      get_logger(),
      "publishing %zu dense LiDAR frames to %s at %.2f Hz; loop=%s; first frame has %zu points",
      frames_.size(),
      topic_.c_str(),
      rate_hz_,
      loop_ ? "true" : "false",
      frames_.front().points.size());
    if (livox_publisher_) {
      RCLCPP_INFO(get_logger(), "also publishing Livox CustomMsg to %s", livox_topic_.c_str());
    }
  }

 private:
  void write_trace(
      const Frame& frame,
      const size_t frame_index,
      const builtin_interfaces::msg::Time& emitted_stamp,
      const uint64_t livox_timebase,
      const std::chrono::steady_clock::time_point& steady_before_stamp,
      const std::chrono::steady_clock::time_point& steady_before_publish,
      const std::chrono::steady_clock::time_point& steady_after_publish,
      const builtin_interfaces::msg::Time& node_now_after_publish,
      const size_t livox_matched_before_stamp,
      const size_t livox_matched_before_publish,
      const size_t livox_matched_after_publish,
      const size_t pointcloud_matched_before_publish,
      const size_t pointcloud_emit_seq,
      const size_t livox_emit_seq) {
    if (!trace_) {
      return;
    }
    const double publish_duration_ms =
      std::chrono::duration<double, std::milli>(steady_after_publish - steady_before_publish).count();
    trace_
      << "{\"schema\":\"mosim.ros2_runtime.publisher_timestamp_trace_047.v1\""
      << ",\"frame_index\":" << frame_index
      << ",\"source_frame_seq\":" << frame.source_seq
      << ",\"source_frame_time\":" << frame.source_time
      << ",\"point_count\":" << frame.points.size()
      << ",\"steady_clock_before_stamp_ns\":" << steady_ns(steady_before_stamp)
      << ",\"node_now_at_stamp_assignment\":" << stamp_json(emitted_stamp)
      << ",\"publisher_emit_seq_pointcloud2\":" << pointcloud_emit_seq
      << ",\"publisher_emit_seq_livox\":" << livox_emit_seq
      << ",\"emitted_header_stamp\":" << stamp_json(emitted_stamp)
      << ",\"livox_timebase_nanoseconds\":" << livox_timebase
      << ",\"timebase_minus_header_ns\":" << (static_cast<int64_t>(livox_timebase) - stamp_ns(emitted_stamp))
      << ",\"steady_clock_before_publish_ns\":" << steady_ns(steady_before_publish)
      << ",\"livox_matched_subscriptions_before_stamp\":" << livox_matched_before_stamp
      << ",\"livox_matched_subscriptions_before_publish\":" << livox_matched_before_publish
      << ",\"pointcloud_matched_subscriptions_before_publish\":" << pointcloud_matched_before_publish
      << ",\"steady_clock_after_publish_ns\":" << steady_ns(steady_after_publish)
      << ",\"node_now_after_publish\":" << stamp_json(node_now_after_publish)
      << ",\"livox_matched_subscriptions_after_publish\":" << livox_matched_after_publish
      << ",\"publish_duration_ms\":" << publish_duration_ms
      << ",\"loop\":" << (loop_ ? "true" : "false")
      << ",\"topic\":\"" << json_escape(livox_topic_) << "\""
      << ",\"pointcloud_topic\":\"" << json_escape(topic_) << "\""
      << ",\"qos_profile\":\"livox reliable KeepLast(20); pointcloud SensorDataQoS\""
      << ",\"clock_type\":\"RCL_SYSTEM_TIME\""
      << "}\n";
    trace_.flush();
  }

  void finish_non_looping_replay() {
    if (non_looping_replay_finished_) {
      return;
    }
    non_looping_replay_finished_ = true;
    if (timer_) {
      timer_->cancel();
    }
    RCLCPP_INFO(
      get_logger(),
      "completed non-looping dense LiDAR replay after %zu/%zu frames; exit_after_last_frame=%s",
      index_,
      frames_.size(),
      exit_after_last_frame_ ? "true" : "false");
    if (exit_after_last_frame_) {
      rclcpp::shutdown();
    }
  }

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
  std::string livox_topic_;
  std::string trace_path_;
  std::string frame_id_;
  double rate_hz_{10.0};
  double scan_duration_s_{0.1};
  double stats_interval_s_{5.0};
  bool loop_{true};
  bool exit_after_last_frame_{false};
  bool non_looping_replay_finished_{false};
  size_t index_{0};
  size_t publish_count_{0};
  size_t pointcloud_emit_seq_{0};
  size_t livox_emit_seq_{0};
  double publish_time_total_us_{0.0};
  std::chrono::steady_clock::time_point stats_start_;
  std::vector<Frame> frames_;
  rclcpp::Publisher<sensor_msgs::msg::PointCloud2>::SharedPtr publisher_;
  rclcpp::Publisher<livox_ros_driver2::msg::CustomMsg>::SharedPtr livox_publisher_;
  rclcpp::TimerBase::SharedPtr timer_;
  std::ofstream trace_;
};

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);
  try {
    rclcpp::spin(std::make_shared<InstrumentedDenseLidarReplayNode>());
  } catch (const std::exception& exc) {
    std::cerr << exc.what() << std::endl;
    rclcpp::shutdown();
    return 1;
  }
  rclcpp::shutdown();
  return 0;
}
