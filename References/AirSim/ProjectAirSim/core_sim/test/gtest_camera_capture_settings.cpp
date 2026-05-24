// Copyright (C) Microsoft Corporation.  
// Copyright (C) 2025 IAMAI CONSULTING CORP
//
// MIT License. All rights reserved.
// Tests for Camera Capture Settings

#include "core_sim/config_json.hpp"
#include "core_sim/logger.hpp"
#include "core_sim/sensors/camera.hpp"
#include "core_sim/sensors/sensor.hpp"
#include "core_sim/service_manager.hpp"
#include "gtest/gtest.h"
#include "state_manager.hpp"
#include "topic_manager.hpp"

using json = nlohmann::json;

namespace microsoft {
namespace projectairsim {

class Robot {  // : public ::testing::Test {
               // protected:
 public:
  static Camera MakeDefaultCamera() {
    const std::string& id = "TestCamID";
    const bool& is_enabled = true;
    const std::string& parent_link = "ParentLink1";
    auto logger_callback = [](const std::string& component, LogLevel level,
                              const std::string& message) {};
    Logger logger(logger_callback);
    const std::string& parent_topic_path = "/camera_test_topic";
    return Camera(id, is_enabled, parent_link, logger, TopicManager(logger),
                  parent_topic_path, ServiceManager(logger),
                  StateManager(logger));
  }

  static void LoadCamera(Camera& camera, ConfigJson config_json) {
    camera.Load(config_json);
  }

  static json GetDefaultCameraConfig() {
    json config = R"({
        "id": "ID123",
        "type": "camera",
        "enabled": true,
        "parent-link": "ParentLink",
        "capture-interval": 1.23,
        "capture-settings": [],
        "noise-settings": [],
        "gimbal": {},
        "origin": {}
    })"_json;
    return config;
  }
};

}  // namespace projectairsim
}  // namespace microsoft

namespace projectairsim = microsoft::projectairsim;

TEST(CameraCaptureSettings, SetsCaptureInterval) {
  // General description:
  // Verifies sets capture interval for CameraCaptureSettings.
  // Arrange: prepare context for `auto camera = projectairsim::Robot::MakeDefaultCamera();`.
  auto camera = projectairsim::Robot::MakeDefaultCamera();
  auto camera_settings = projectairsim::Robot::GetDefaultCameraConfig();
  projectairsim::Robot::LoadCamera(camera, camera_settings);
  // Act: run `const auto& actual_camera_settings = camera.GetCameraSettings();`.
  const auto& actual_camera_settings = camera.GetCameraSettings();
  // Assert: check result from `EXPECT_FLOAT_EQ(actual_camera_settings.capture_interval, 1.23);`.
  EXPECT_FLOAT_EQ(actual_camera_settings.capture_interval, 1.23);
}

TEST(CameraCaptureSettings, EnablesCapture) {
  // General description:
  // Verifies enables capture for CameraCaptureSettings.
  // Arrange: prepare context for `auto camera = projectairsim::Robot::MakeDefaultCamera();`.
  auto camera = projectairsim::Robot::MakeDefaultCamera();
  auto camera_settings = projectairsim::Robot::GetDefaultCameraConfig();
  projectairsim::Robot::LoadCamera(camera, camera_settings);
  const auto& actual_camera_settings = camera.GetCameraSettings();
  // Act: run `auto actual_capture_settings = actual_camera_settings.capture_settings;`.
  auto actual_capture_settings = actual_camera_settings.capture_settings;
  // Assert: check result from `EXPECT_FLOAT_EQ(actual_capture_settings.at(2).capture_enabled, false);`.
  EXPECT_FLOAT_EQ(actual_capture_settings.at(2).capture_enabled, false);

  json capture_settings = R"( [ {
          "capture-enabled": true,
          "image-type": 2
      } ]
  )"_json;
  camera_settings["capture-settings"] = capture_settings;
  projectairsim::Robot::LoadCamera(camera, camera_settings);
  const auto& new_actual_camera_settings = camera.GetCameraSettings();
  actual_capture_settings = new_actual_camera_settings.capture_settings;
  EXPECT_FLOAT_EQ(actual_capture_settings.at(2).capture_enabled, true);
}

TEST(CameraCaptureSettings, EnablesAutoExposureMethodParam) {
  // General description:
  // Verifies enables auto exposure method param for CameraCaptureSettings.
  // Arrange: prepare context for `auto camera = projectairsim::Robot::MakeDefaultCamera();`.
  auto camera = projectairsim::Robot::MakeDefaultCamera();
  auto camera_settings = projectairsim::Robot::GetDefaultCameraConfig();
  projectairsim::Robot::LoadCamera(camera, camera_settings);
  const auto& actual_camera_settings = camera.GetCameraSettings();
  // Act: run `auto actual_capture_settings = actual_camera_settings.capture_settings;`.
  auto actual_capture_settings = actual_camera_settings.capture_settings;
  // Assert: check result from `EXPECT_FLOAT_EQ(actual_capture_settings.at(2).auto_exposure_method, 0);`.
  EXPECT_FLOAT_EQ(actual_capture_settings.at(2).auto_exposure_method, 0);

  json capture_settings = R"( [ {
          "image-type": 2,
          "auto-exposure-method": 1
      } ]
  )"_json;
  camera_settings["capture-settings"] = capture_settings;
  projectairsim::Robot::LoadCamera(camera, camera_settings);
  const auto& new_actual_camera_settings = camera.GetCameraSettings();
  actual_capture_settings = new_actual_camera_settings.capture_settings;
  EXPECT_FLOAT_EQ(actual_capture_settings.at(2).auto_exposure_method, 1);
}

TEST(CameraCaptureSettings, EnablesWidthParam) {
  // General description:
  // Verifies enables width param for CameraCaptureSettings.
  // Arrange: prepare context for `auto camera = projectairsim::Robot::MakeDefaultCamera();`.
  auto camera = projectairsim::Robot::MakeDefaultCamera();
  auto camera_settings = projectairsim::Robot::GetDefaultCameraConfig();
  json capture_settings = R"( [ {
          "image-type": 2,
          "width": 123
      } ]
  )"_json;
  camera_settings["capture-settings"] = capture_settings;
  projectairsim::Robot::LoadCamera(camera, camera_settings);
  const auto& actual_camera_settings = camera.GetCameraSettings();
  // Act: run `auto actual_capture_settings = actual_camera_settings.capture_settings;`.
  auto actual_capture_settings = actual_camera_settings.capture_settings;
  // Assert: check result from `EXPECT_FLOAT_EQ(actual_capture_settings.at(2).width, 123);`.
  EXPECT_FLOAT_EQ(actual_capture_settings.at(2).width, 123);
}

TEST(CameraCaptureSettings, EnablesHeightParam) {
  // General description:
  // Verifies enables height param for CameraCaptureSettings.
  // Arrange: prepare context for `auto camera = projectairsim::Robot::MakeDefaultCamera();`.
  auto camera = projectairsim::Robot::MakeDefaultCamera();
  auto camera_settings = projectairsim::Robot::GetDefaultCameraConfig();
  json capture_settings = R"( [ {
          "image-type": 2,
          "height": 123
      } ]
  )"_json;
  camera_settings["capture-settings"] = capture_settings;
  projectairsim::Robot::LoadCamera(camera, camera_settings);
  const auto& actual_camera_settings = camera.GetCameraSettings();
  // Act: run `auto actual_capture_settings = actual_camera_settings.capture_settings;`.
  auto actual_capture_settings = actual_camera_settings.capture_settings;
  // Assert: check result from `EXPECT_FLOAT_EQ(actual_capture_settings.at(2).height, 123);`.
  EXPECT_FLOAT_EQ(actual_capture_settings.at(2).height, 123);
}

TEST(CameraCaptureSettings, EnablesFovDegreesParam) {
  // General description:
  // Verifies enables fov degrees param for CameraCaptureSettings.
  // Arrange: prepare context for `auto camera = projectairsim::Robot::MakeDefaultCamera();`.
  auto camera = projectairsim::Robot::MakeDefaultCamera();
  auto camera_settings = projectairsim::Robot::GetDefaultCameraConfig();
  json capture_settings = R"( [ {
          "image-type": 2,
          "fov-degrees": 123
      } ]
  )"_json;
  camera_settings["capture-settings"] = capture_settings;
  projectairsim::Robot::LoadCamera(camera, camera_settings);
  const auto& actual_camera_settings = camera.GetCameraSettings();
  // Act: run `auto actual_capture_settings = actual_camera_settings.capture_settings;`.
  auto actual_capture_settings = actual_camera_settings.capture_settings;
  // Assert: check result from `EXPECT_FLOAT_EQ(actual_capture_settings.at(2).fov_degrees, 123);`.
  EXPECT_FLOAT_EQ(actual_capture_settings.at(2).fov_degrees, 123);
}

TEST(CameraCaptureSettings, EnablesAutoExposureSpeedParam) {
  // General description:
  // Verifies enables auto exposure speed param for CameraCaptureSettings.
  // Arrange: prepare context for `auto camera = projectairsim::Robot::MakeDefaultCamera();`.
  auto camera = projectairsim::Robot::MakeDefaultCamera();
  auto camera_settings = projectairsim::Robot::GetDefaultCameraConfig();
  json capture_settings = R"( [ {
          "image-type": 2,
          "auto-exposure-speed": 1.23
      } ]
  )"_json;
  camera_settings["capture-settings"] = capture_settings;
  projectairsim::Robot::LoadCamera(camera, camera_settings);
  const auto& actual_camera_settings = camera.GetCameraSettings();
  // Act: run `auto actual_capture_settings = actual_camera_settings.capture_settings;`.
  auto actual_capture_settings = actual_camera_settings.capture_settings;
  // Assert: check result from `EXPECT_FLOAT_EQ(actual_capture_settings.at(2).auto_exposure_speed, 1.23);`.
  EXPECT_FLOAT_EQ(actual_capture_settings.at(2).auto_exposure_speed, 1.23);
}

TEST(CameraCaptureSettings, EnablesAutoExposureBiasParam) {
  // General description:
  // Verifies enables auto exposure bias param for CameraCaptureSettings.
  // Arrange: prepare context for `auto camera = projectairsim::Robot::MakeDefaultCamera();`.
  auto camera = projectairsim::Robot::MakeDefaultCamera();
  auto camera_settings = projectairsim::Robot::GetDefaultCameraConfig();
  json capture_settings = R"( [ {
          "image-type": 2,
          "auto-exposure-bias": 0.123
      } ]
  )"_json;
  camera_settings["capture-settings"] = capture_settings;
  projectairsim::Robot::LoadCamera(camera, camera_settings);
  const auto& actual_camera_settings = camera.GetCameraSettings();
  // Act: run `auto actual_capture_settings = actual_camera_settings.capture_settings;`.
  auto actual_capture_settings = actual_camera_settings.capture_settings;
  // Assert: check result from `EXPECT_FLOAT_EQ(actual_capture_settings.at(2).auto_exposure_bias, 0.123);`.
  EXPECT_FLOAT_EQ(actual_capture_settings.at(2).auto_exposure_bias, 0.123);
}

TEST(CameraCaptureSettings, EnablesAutoExposureMaxBrightnessParam) {
  // General description:
  // Verifies enables auto exposure max brightness param for CameraCaptureSettings.
  // Arrange: prepare context for `auto camera = projectairsim::Robot::MakeDefaultCamera();`.
  auto camera = projectairsim::Robot::MakeDefaultCamera();
  auto camera_settings = projectairsim::Robot::GetDefaultCameraConfig();
  json capture_settings = R"( [ {
          "image-type": 2,
          "auto-exposure-max-brightness": 1.23
      } ]
  )"_json;
  camera_settings["capture-settings"] = capture_settings;
  projectairsim::Robot::LoadCamera(camera, camera_settings);
  const auto& actual_camera_settings = camera.GetCameraSettings();
  // Act: run `auto actual_capture_settings = actual_camera_settings.capture_settings;`.
  auto actual_capture_settings = actual_camera_settings.capture_settings;
  // Assert: check result from `EXPECT_FLOAT_EQ(actual_capture_settings.at(2).auto_exposure_max_brightness,`.
  EXPECT_FLOAT_EQ(actual_capture_settings.at(2).auto_exposure_max_brightness,
                  1.23);
}

TEST(CameraCaptureSettings, EnablesAutoExposureMinBrightnessParam) {
  // General description:
  // Verifies enables auto exposure min brightness param for CameraCaptureSettings.
  // Arrange: prepare context for `auto camera = projectairsim::Robot::MakeDefaultCamera();`.
  auto camera = projectairsim::Robot::MakeDefaultCamera();
  auto camera_settings = projectairsim::Robot::GetDefaultCameraConfig();
  json capture_settings = R"( [ {
          "image-type": 2,
          "auto-exposure-min-brightness": 0.123
      } ]
  )"_json;
  camera_settings["capture-settings"] = capture_settings;
  projectairsim::Robot::LoadCamera(camera, camera_settings);
  const auto& actual_camera_settings = camera.GetCameraSettings();
  // Act: run `auto actual_capture_settings = actual_camera_settings.capture_settings;`.
  auto actual_capture_settings = actual_camera_settings.capture_settings;
  // Assert: check result from `EXPECT_FLOAT_EQ(actual_capture_settings.at(2).auto_exposure_min_brightness,`.
  EXPECT_FLOAT_EQ(actual_capture_settings.at(2).auto_exposure_min_brightness,
                  0.123);
}

TEST(CameraCaptureSettings, EnablesAutoExposureLowPercentParam) {
  // General description:
  // Verifies enables auto exposure low percent param for CameraCaptureSettings.
  // Arrange: prepare context for `auto camera = projectairsim::Robot::MakeDefaultCamera();`.
  auto camera = projectairsim::Robot::MakeDefaultCamera();
  auto camera_settings = projectairsim::Robot::GetDefaultCameraConfig();
  json capture_settings = R"( [ {
          "image-type": 2,
          "auto-exposure-low-percent": 0.123
      } ]
  )"_json;
  camera_settings["capture-settings"] = capture_settings;
  projectairsim::Robot::LoadCamera(camera, camera_settings);
  const auto& actual_camera_settings = camera.GetCameraSettings();
  // Act: run `auto actual_capture_settings = actual_camera_settings.capture_settings;`.
  auto actual_capture_settings = actual_camera_settings.capture_settings;
  // Assert: check result from `EXPECT_FLOAT_EQ(actual_capture_settings.at(2).auto_exposure_low_percent,`.
  EXPECT_FLOAT_EQ(actual_capture_settings.at(2).auto_exposure_low_percent,
                  0.123);
}

TEST(CameraCaptureSettings, EnablesAutoExposureHighPercentParam) {
  // General description:
  // Verifies enables auto exposure high percent param for CameraCaptureSettings.
  // Arrange: prepare context for `auto camera = projectairsim::Robot::MakeDefaultCamera();`.
  auto camera = projectairsim::Robot::MakeDefaultCamera();
  auto camera_settings = projectairsim::Robot::GetDefaultCameraConfig();
  json capture_settings = R"( [ {
          "image-type": 2,
          "auto-exposure-high-percent": 0.99
      } ]
  )"_json;
  camera_settings["capture-settings"] = capture_settings;
  projectairsim::Robot::LoadCamera(camera, camera_settings);
  const auto& actual_camera_settings = camera.GetCameraSettings();
  // Act: run `auto actual_capture_settings = actual_camera_settings.capture_settings;`.
  auto actual_capture_settings = actual_camera_settings.capture_settings;
  // Assert: check result from `EXPECT_FLOAT_EQ(actual_capture_settings.at(2).auto_exposure_high_percent,`.
  EXPECT_FLOAT_EQ(actual_capture_settings.at(2).auto_exposure_high_percent,
                  0.99);
}

TEST(CameraCaptureSettings, EnablesAutoExposureHistogramLogMinParam) {
  // General description:
  // Verifies enables auto exposure histogram log min param for CameraCaptureSettings.
  // Arrange: prepare context for `auto camera = projectairsim::Robot::MakeDefaultCamera();`.
  auto camera = projectairsim::Robot::MakeDefaultCamera();
  auto camera_settings = projectairsim::Robot::GetDefaultCameraConfig();
  json capture_settings = R"( [ {
          "image-type": 2,
          "auto-exposure-histogram-log-min": -12.3
      } ]
  )"_json;
  camera_settings["capture-settings"] = capture_settings;
  projectairsim::Robot::LoadCamera(camera, camera_settings);
  const auto& actual_camera_settings = camera.GetCameraSettings();
  // Act: run `auto actual_capture_settings = actual_camera_settings.capture_settings;`.
  auto actual_capture_settings = actual_camera_settings.capture_settings;
  // Assert: check result from `EXPECT_FLOAT_EQ(actual_capture_settings.at(2).auto_exposure_histogram_log_min,`.
  EXPECT_FLOAT_EQ(actual_capture_settings.at(2).auto_exposure_histogram_log_min,
                  -12.3);
}

TEST(CameraCaptureSettings, EnablesAutoExposureHistogramLogMaxParam) {
  // General description:
  // Verifies enables auto exposure histogram log max param for CameraCaptureSettings.
  // Arrange: prepare context for `auto camera = projectairsim::Robot::MakeDefaultCamera();`.
  auto camera = projectairsim::Robot::MakeDefaultCamera();
  auto camera_settings = projectairsim::Robot::GetDefaultCameraConfig();
  json capture_settings = R"( [ {
          "image-type": 2,
          "auto-exposure-histogram-log-max": 12.3
      } ]
  )"_json;
  camera_settings["capture-settings"] = capture_settings;
  projectairsim::Robot::LoadCamera(camera, camera_settings);
  const auto& actual_camera_settings = camera.GetCameraSettings();
  // Act: run `auto actual_capture_settings = actual_camera_settings.capture_settings;`.
  auto actual_capture_settings = actual_camera_settings.capture_settings;
  // Assert: check result from `EXPECT_FLOAT_EQ(actual_capture_settings.at(2).auto_exposure_histogram_log_max,`.
  EXPECT_FLOAT_EQ(actual_capture_settings.at(2).auto_exposure_histogram_log_max,
                  12.3);
}

TEST(CameraCaptureSettings, EnablesMotionBlurParam) {
  // General description:
  // Verifies enables motion blur param for CameraCaptureSettings.
  // Arrange: prepare context for `auto camera = projectairsim::Robot::MakeDefaultCamera();`.
  auto camera = projectairsim::Robot::MakeDefaultCamera();
  auto camera_settings = projectairsim::Robot::GetDefaultCameraConfig();
  json capture_settings = R"( [ {
          "image-type": 2,
          "motion-blur-amount": 1.23
      } ]
  )"_json;
  camera_settings["capture-settings"] = capture_settings;
  projectairsim::Robot::LoadCamera(camera, camera_settings);
  const auto& actual_camera_settings = camera.GetCameraSettings();
  // Act: run `auto actual_capture_settings = actual_camera_settings.capture_settings;`.
  auto actual_capture_settings = actual_camera_settings.capture_settings;
  // Assert: check result from `EXPECT_FLOAT_EQ(actual_capture_settings.at(2).motion_blur_amount, 1.23);`.
  EXPECT_FLOAT_EQ(actual_capture_settings.at(2).motion_blur_amount, 1.23);
}
