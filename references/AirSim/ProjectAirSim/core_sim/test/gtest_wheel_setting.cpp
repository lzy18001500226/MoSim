// Copyright (C) 2025 IAMAI CONSULTING CORP
//
// MIT License. All rights reserved.

#include "core_sim/actuators/wheel.hpp"
#include "gtest/gtest.h"

namespace projectairsim = microsoft::projectairsim;

TEST(WheelSetting, CalculatesTorqueForceAndAccelerationFromFriction) {
  // General description:
  // Verifies force/torque/acceleration calculation from friction and radius.
  // Arrange: prepare context for `projectairsim::WheelSetting wheel;`.
  projectairsim::WheelSetting wheel;
  wheel.coeff_of_friction = 2000.0f;
  wheel.radius_ = 0.3f;

  // Act: run `wheel.CalcMaxTorqueAndForce();`.
  wheel.CalcMaxTorqueAndForce();

  // Assert: check result from `EXPECT_FLOAT_EQ(wheel.max_force, 2000.0f);`.
  EXPECT_FLOAT_EQ(wheel.max_force, 2000.0f);
  EXPECT_FLOAT_EQ(wheel.max_torque, 600.0f);
  EXPECT_FLOAT_EQ(wheel.max_acceleration, 2000.0f);
}

TEST(WheelSetting, WheelTypeConventionsRemainStable) {
  // General description:
  // Verifies stable wheel-type convention (rear/front).
  // Arrange: prepare context for `projectairsim::WheelSetting rear;`.
  projectairsim::WheelSetting rear;
  rear.wheel_type = 0.0f;

  projectairsim::WheelSetting front;
  // Act: run `front.wheel_type = 1.0f;`.
  front.wheel_type = 1.0f;

  // Assert: check result from `EXPECT_FLOAT_EQ(rear.wheel_type, 0.0f);`.
  EXPECT_FLOAT_EQ(rear.wheel_type, 0.0f);
  EXPECT_FLOAT_EQ(front.wheel_type, 1.0f);
}
