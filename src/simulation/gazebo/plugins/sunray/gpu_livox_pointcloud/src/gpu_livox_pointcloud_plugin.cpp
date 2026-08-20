#include <algorithm>
#include <atomic>
#include <chrono>
#include <cstdint>
#include <cmath>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <memory>
#include <string>
#include <vector>

#include <gazebo/plugins/GpuRayPlugin.hh>
#include <gazebo/sensors/GpuRaySensor.hh>
#include <pcl/point_cloud.h>
#include <pcl/point_types.h>
#include <pcl_conversions/pcl_conversions.h>
#include <ros/ros.h>
#include <sensor_msgs/PointCloud2.h>
#include <sensor_msgs/PointField.h>

namespace gazebo {
namespace {

std::string StripSlashes(std::string value) {
  while (!value.empty() && value.front() == '/') {
    value.erase(value.begin());
  }
  while (!value.empty() && value.back() == '/') {
    value.pop_back();
  }
  return value;
}

std::string ParentRobotName(const sensors::SensorPtr& sensor) {
  const std::string parent_name = sensor ? sensor->ParentName() : "";
  const std::size_t separator = parent_name.find("::");
  return parent_name.substr(0, separator);
}

std::string SdfText(const sdf::ElementPtr& sdf, const std::string& name, const std::string& fallback) {
  if (sdf && sdf->HasElement(name)) {
    return sdf->Get<std::string>(name);
  }
  return fallback;
}

std::string EnvironmentText(const char* name, const std::string& fallback) {
  const char* value = std::getenv(name);
  return value && value[0] != '\0' ? value : fallback;
}

std::uint64_t EnvironmentUnsigned(const char* name, std::uint64_t fallback) {
  const char* value = std::getenv(name);
  if (!value || value[0] == '\0') {
    return fallback;
  }
  char* end = nullptr;
  const auto parsed = std::strtoull(value, &end, 10);
  return end && end[0] == '\0' ? parsed : fallback;
}

struct RayDirection {
  double x;
  double y;
  double z;
};

struct PointXYZPadding {
  float x;
  float y;
  float z;
  float padding;
};

static_assert(sizeof(PointXYZPadding) == 16U, "PointCloud2 point_step must remain 16 bytes");

struct ProfileSample {
  double setup_us{0.0};
  double projection_us{0.0};
  double serialization_us{0.0};
  double publish_us{0.0};
  double total_us{0.0};
  std::size_t valid_points{0U};
};

double ElapsedMicroseconds(const std::chrono::steady_clock::time_point& start,
                           const std::chrono::steady_clock::time_point& end) {
  return std::chrono::duration<double, std::micro>(end - start).count();
}

}  // namespace

class MoSimGpuLivoxPointCloudPlugin final : public GpuRayPlugin {
 public:
  void Load(sensors::SensorPtr sensor, sdf::ElementPtr sdf) {
    GpuRayPlugin::Load(sensor, sdf);
    if (!this->parentSensor) {
      gzerr << "MoSimGpuLivoxPointCloudPlugin requires a gpu_ray parent sensor.\n";
      return;
    }

    const std::string robot_name = ParentRobotName(sensor);
    const std::string configured_namespace = SdfText(sdf, "robotNamespace", "");
    if (configured_namespace.empty()) {
      this->robot_namespace_ = robot_name.empty() ? "" : "/" + robot_name;
    } else {
      this->robot_namespace_ = configured_namespace;
    }
    if (!this->robot_namespace_.empty() && this->robot_namespace_.front() != '/') {
      this->robot_namespace_.insert(this->robot_namespace_.begin(), '/');
    }

    this->topic_name_ = SdfText(sdf, "ros_topic", "livox/lidar");
    this->frame_name_ = SdfText(sdf, "frameName", "base_link");
    if (this->frame_name_.find('/') == std::string::npos && !robot_name.empty()) {
      this->frame_name_ = robot_name + "/" + this->frame_name_;
    }
    this->frame_name_ = StripSlashes(this->frame_name_);

    if (!ros::isInitialized()) {
      int argc = 0;
      char** argv = nullptr;
      ros::init(argc, argv, "mosim_gpu_livox_pointcloud", ros::init_options::NoSigintHandler);
    }
    this->ros_node_ = std::make_unique<ros::NodeHandle>(this->robot_namespace_);
    this->publisher_ = this->ros_node_->advertise<sensor_msgs::PointCloud2>(this->topic_name_, 3);
    this->range_min_ = this->parentSensor->RangeMin();
    this->range_max_ = this->parentSensor->RangeMax();
    this->output_mode_ = EnvironmentText("MOSIM_GPU_LIVOX_OUTPUT_MODE", "pcl");
    if (this->output_mode_ != "pcl" && this->output_mode_ != "direct") {
      gzerr << "MoSimGpuLivoxPointCloudPlugin ignores unsupported "
            << "MOSIM_GPU_LIVOX_OUTPUT_MODE=" << this->output_mode_ << "; using pcl.\n";
      this->output_mode_ = "pcl";
    }
    this->profile_interval_frames_ =
        EnvironmentUnsigned("MOSIM_GPU_LIVOX_PROFILE_INTERVAL_FRAMES", 0U);
    this->profile_output_path_ = EnvironmentText("MOSIM_GPU_LIVOX_PROFILE_OUTPUT", "");
    if (this->profile_interval_frames_ > 0U && !this->profile_output_path_.empty()) {
      this->profile_output_.open(this->profile_output_path_, std::ios::out | std::ios::app);
      if (!this->profile_output_) {
        gzerr << "MoSimGpuLivoxPointCloudPlugin cannot write profile output: "
              << this->profile_output_path_ << "\n";
      }
    }
    this->ConfigureDirectOutput();

    gzmsg << "[MoSimGpuLivoxLoad] sensor=" << sensor->Name()
          << " topic=" << this->publisher_.getTopic()
          << " frame=" << this->frame_name_
          << " range=" << this->range_min_ << "," << this->range_max_
          << " output_mode=" << this->output_mode_
          << " profile_interval_frames=" << this->profile_interval_frames_
          << " profile_output=" << this->profile_output_path_ << "\n";
  }

  void OnNewLaserFrame(const float* image, unsigned int width, unsigned int height,
                       unsigned int depth, const std::string& format) override {
    if (!image || !this->parentSensor || !this->publisher_) {
      return;
    }
    if (width == 0U || height == 0U || depth == 0U) {
      gzerr << "MoSimGpuLivoxPointCloudPlugin received an empty GPU ray frame.\n";
      return;
    }

    if (!this->logged_first_frame_.exchange(true)) {
      gzmsg << "[MoSimGpuLivoxFrame] width=" << width << " height=" << height
            << " depth=" << depth << " format=" << format << "\n";
    }

    const auto callback_start = std::chrono::steady_clock::now();
    const auto setup_start = callback_start;
    if (this->output_mode_ == "direct") {
      this->EnsureRayDirections(width, height);
    }
    const auto setup_end = std::chrono::steady_clock::now();

    ProfileSample sample;
    sample.setup_us = ElapsedMicroseconds(setup_start, setup_end);
    if (this->output_mode_ == "direct") {
      sample = this->PublishDirect(image, width, height, depth, sample);
    } else {
      sample = this->PublishPcl(image, width, height, depth, sample);
    }
    sample.total_us = ElapsedMicroseconds(callback_start, std::chrono::steady_clock::now());
    this->RecordProfile(sample, width, height, depth);
  }

 private:
  void ConfigureDirectOutput() {
    this->direct_output_.height = 1U;
    this->direct_output_.is_bigendian = false;
    this->direct_output_.is_dense = true;
    this->direct_output_.point_step = sizeof(PointXYZPadding);
    this->direct_output_.fields.resize(3U);
    this->ConfigureFloatField(&this->direct_output_.fields[0], "x", 0U);
    this->ConfigureFloatField(&this->direct_output_.fields[1], "y", 4U);
    this->ConfigureFloatField(&this->direct_output_.fields[2], "z", 8U);
  }

  static void ConfigureFloatField(sensor_msgs::PointField* field, const char* name,
                                  std::uint32_t offset) {
    field->name = name;
    field->offset = offset;
    field->datatype = sensor_msgs::PointField::FLOAT32;
    field->count = 1U;
  }

  void EnsureRayDirections(unsigned int width, unsigned int height) {
    if (width == this->direction_width_ && height == this->direction_height_) {
      return;
    }

    const double horizontal_min = this->parentSensor->AngleMin().Radian();
    const double horizontal_max = this->parentSensor->AngleMax().Radian();
    const double vertical_min = this->parentSensor->VerticalAngleMin().Radian();
    const double vertical_max = this->parentSensor->VerticalAngleMax().Radian();
    const double horizontal_step =
        width > 1U ? (horizontal_max - horizontal_min) / static_cast<double>(width - 1U) : 0.0;
    const double vertical_step =
        height > 1U ? (vertical_max - vertical_min) / static_cast<double>(height - 1U) : 0.0;

    this->ray_directions_.resize(static_cast<std::size_t>(width) * static_cast<std::size_t>(height));
    for (unsigned int vertical_index = 0; vertical_index < height; ++vertical_index) {
      const double vertical = vertical_min + static_cast<double>(vertical_index) * vertical_step;
      const double cos_vertical = std::cos(vertical);
      const double sin_vertical = std::sin(vertical);
      for (unsigned int horizontal_index = 0; horizontal_index < width; ++horizontal_index) {
        const double horizontal = horizontal_min + static_cast<double>(horizontal_index) * horizontal_step;
        const std::size_t direction_index =
            static_cast<std::size_t>(vertical_index) * width + horizontal_index;
        this->ray_directions_[direction_index] = {
            cos_vertical * std::cos(horizontal),
            cos_vertical * std::sin(horizontal),
            sin_vertical,
        };
      }
    }
    this->direction_width_ = width;
    this->direction_height_ = height;
    this->direct_output_.data.reserve(
        this->ray_directions_.size() * static_cast<std::size_t>(this->direct_output_.point_step));
    gzmsg << "[MoSimGpuLivoxDirectionCache] width=" << width << " height=" << height
          << " directions=" << this->ray_directions_.size() << "\n";
  }

  ProfileSample PublishPcl(const float* image, unsigned int width, unsigned int height,
                           unsigned int depth, ProfileSample sample) {
    const auto projection_start = std::chrono::steady_clock::now();
    const double horizontal_min = this->parentSensor->AngleMin().Radian();
    const double horizontal_max = this->parentSensor->AngleMax().Radian();
    const double vertical_min = this->parentSensor->VerticalAngleMin().Radian();
    const double vertical_max = this->parentSensor->VerticalAngleMax().Radian();
    const double horizontal_step =
        width > 1U ? (horizontal_max - horizontal_min) / static_cast<double>(width - 1U) : 0.0;
    const double vertical_step =
        height > 1U ? (vertical_max - vertical_min) / static_cast<double>(height - 1U) : 0.0;

    pcl::PointCloud<pcl::PointXYZ> cloud;
    cloud.reserve(static_cast<std::size_t>(width) * static_cast<std::size_t>(height));
    const std::size_t stride = static_cast<std::size_t>(depth);
    for (unsigned int vertical_index = 0; vertical_index < height; ++vertical_index) {
      const double vertical = vertical_min + static_cast<double>(vertical_index) * vertical_step;
      const double cos_vertical = std::cos(vertical);
      const double sin_vertical = std::sin(vertical);
      for (unsigned int horizontal_index = 0; horizontal_index < width; ++horizontal_index) {
        const std::size_t pixel_index =
            (static_cast<std::size_t>(vertical_index) * width + horizontal_index) * stride;
        const float range = image[pixel_index];
        if (!this->ValidRange(range)) {
          continue;
        }
        const double horizontal = horizontal_min + static_cast<double>(horizontal_index) * horizontal_step;
        pcl::PointXYZ point;
        point.x = range * cos_vertical * std::cos(horizontal);
        point.y = range * cos_vertical * std::sin(horizontal);
        point.z = range * sin_vertical;
        cloud.push_back(point);
      }
    }
    cloud.width = static_cast<std::uint32_t>(cloud.size());
    cloud.height = 1U;
    cloud.is_dense = true;
    sample.valid_points = cloud.size();
    const auto projection_end = std::chrono::steady_clock::now();

    sensor_msgs::PointCloud2 output;
    pcl::toROSMsg(cloud, output);
    output.header.stamp = ros::Time::now();
    output.header.frame_id = this->frame_name_;
    const auto serialization_end = std::chrono::steady_clock::now();
    this->publisher_.publish(output);
    const auto publish_end = std::chrono::steady_clock::now();
    sample.projection_us = ElapsedMicroseconds(projection_start, projection_end);
    sample.serialization_us = ElapsedMicroseconds(projection_end, serialization_end);
    sample.publish_us = ElapsedMicroseconds(serialization_end, publish_end);
    return sample;
  }

  ProfileSample PublishDirect(const float* image, unsigned int width, unsigned int height,
                              unsigned int depth, ProfileSample sample) {
    const auto projection_start = std::chrono::steady_clock::now();
    const std::size_t pixel_count = static_cast<std::size_t>(width) * static_cast<std::size_t>(height);
    const std::size_t stride = static_cast<std::size_t>(depth);
    const std::size_t max_data_bytes =
        pixel_count * static_cast<std::size_t>(this->direct_output_.point_step);
    this->direct_output_.data.resize(max_data_bytes);
    std::size_t valid_points = 0U;
    for (std::size_t pixel_index = 0U; pixel_index < pixel_count; ++pixel_index) {
      const float range = image[pixel_index * stride];
      if (!this->ValidRange(range)) {
        continue;
      }
      const RayDirection& direction = this->ray_directions_[pixel_index];
      const PointXYZPadding point{
          static_cast<float>(range * direction.x),
          static_cast<float>(range * direction.y),
          static_cast<float>(range * direction.z),
          1.0F,
      };
      std::memcpy(
          this->direct_output_.data.data() + valid_points * this->direct_output_.point_step,
          &point,
          sizeof(point));
      ++valid_points;
    }
    sample.valid_points = valid_points;
    const auto projection_end = std::chrono::steady_clock::now();

    this->direct_output_.data.resize(valid_points * this->direct_output_.point_step);
    this->direct_output_.width = static_cast<std::uint32_t>(valid_points);
    this->direct_output_.row_step = this->direct_output_.width * this->direct_output_.point_step;
    this->direct_output_.header.stamp = ros::Time::now();
    this->direct_output_.header.frame_id = this->frame_name_;
    const auto serialization_end = std::chrono::steady_clock::now();
    this->publisher_.publish(this->direct_output_);
    const auto publish_end = std::chrono::steady_clock::now();
    sample.projection_us = ElapsedMicroseconds(projection_start, projection_end);
    sample.serialization_us = ElapsedMicroseconds(projection_end, serialization_end);
    sample.publish_us = ElapsedMicroseconds(serialization_end, publish_end);
    return sample;
  }

  bool ValidRange(float range) const {
    return std::isfinite(range) && range > this->range_min_ && range < this->range_max_;
  }

  void RecordProfile(const ProfileSample& sample, unsigned int width, unsigned int height,
                     unsigned int depth) {
    if (this->profile_interval_frames_ == 0U) {
      return;
    }
    ++this->profile_frames_;
    this->profile_width_ = width;
    this->profile_height_ = height;
    this->profile_depth_ = depth;
    this->profile_setup_us_ += sample.setup_us;
    this->profile_projection_us_ += sample.projection_us;
    this->profile_serialization_us_ += sample.serialization_us;
    this->profile_publish_us_ += sample.publish_us;
    this->profile_total_us_ += sample.total_us;
    this->profile_valid_points_ += sample.valid_points;
    if (this->profile_frames_ < this->profile_interval_frames_) {
      return;
    }

    const double count = static_cast<double>(this->profile_frames_);
    const double avg_valid_points = static_cast<double>(this->profile_valid_points_) / count;
    const double avg_setup_ms = this->profile_setup_us_ / count / 1000.0;
    const double avg_projection_ms = this->profile_projection_us_ / count / 1000.0;
    const double avg_serialization_ms = this->profile_serialization_us_ / count / 1000.0;
    const double avg_publish_ms = this->profile_publish_us_ / count / 1000.0;
    const double avg_callback_ms = this->profile_total_us_ / count / 1000.0;
    gzmsg << "[MoSimGpuLivoxProfile] mode=" << this->output_mode_
          << " frames=" << this->profile_frames_
          << " avg_valid_points=" << avg_valid_points
          << " avg_setup_ms=" << avg_setup_ms
          << " avg_projection_ms=" << avg_projection_ms
          << " avg_serialization_ms=" << avg_serialization_ms
          << " avg_publish_ms=" << avg_publish_ms
          << " avg_callback_ms=" << avg_callback_ms << "\n";
    if (this->profile_output_) {
      this->profile_output_ << "{\"schema\":\"mosim.gpu_livox_profile.v1\""
                            << ",\"mode\":\"" << this->output_mode_ << "\""
                            << ",\"frames\":" << this->profile_frames_
                            << ",\"width\":" << this->profile_width_
                            << ",\"height\":" << this->profile_height_
                            << ",\"depth\":" << this->profile_depth_
                            << ",\"avg_valid_points\":" << avg_valid_points
                            << ",\"avg_setup_ms\":" << avg_setup_ms
                            << ",\"avg_projection_ms\":" << avg_projection_ms
                            << ",\"avg_serialization_ms\":" << avg_serialization_ms
                            << ",\"avg_publish_ms\":" << avg_publish_ms
                            << ",\"avg_callback_ms\":" << avg_callback_ms << "}\n";
      this->profile_output_.flush();
    }
    this->profile_frames_ = 0U;
    this->profile_setup_us_ = 0.0;
    this->profile_projection_us_ = 0.0;
    this->profile_serialization_us_ = 0.0;
    this->profile_publish_us_ = 0.0;
    this->profile_total_us_ = 0.0;
    this->profile_valid_points_ = 0U;
  }

  std::unique_ptr<ros::NodeHandle> ros_node_;
  ros::Publisher publisher_;
  std::atomic<bool> logged_first_frame_{false};
  sensor_msgs::PointCloud2 direct_output_;
  std::vector<RayDirection> ray_directions_;
  std::string robot_namespace_;
  std::string topic_name_;
  std::string frame_name_;
  std::string output_mode_;
  std::string profile_output_path_;
  std::ofstream profile_output_;
  unsigned int direction_width_{0U};
  unsigned int direction_height_{0U};
  unsigned int profile_width_{0U};
  unsigned int profile_height_{0U};
  unsigned int profile_depth_{0U};
  std::uint64_t profile_interval_frames_{0U};
  std::uint64_t profile_frames_{0U};
  std::size_t profile_valid_points_{0U};
  double profile_setup_us_{0.0};
  double profile_projection_us_{0.0};
  double profile_serialization_us_{0.0};
  double profile_publish_us_{0.0};
  double profile_total_us_{0.0};
  double range_min_{0.0};
  double range_max_{0.0};
};

GZ_REGISTER_SENSOR_PLUGIN(MoSimGpuLivoxPointCloudPlugin)

}  // namespace gazebo
