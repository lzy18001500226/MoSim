// Copyright (C) 2025 IAMAI CONSULTING CORP
//
// MIT License. All rights reserved.

#include "core_sim/actuators/rotor.hpp"
#include "gtest/gtest.h"

namespace projectairsim = microsoft::projectairsim;

TEST(RotorSetting, TurningDirectionEnumValuesAreStable) {
  // General description:
  // Verifies stability of numeric enum values for rotor turning direction.
  // Act: run `EXPECT_EQ(static_cast<int>(`.
  // Arrange: prepare context for `EXPECT_EQ(static_cast<int>(`.
  // Assert: check result from `EXPECT_EQ(static_cast<int>(`.
  EXPECT_EQ(static_cast<int>(
                projectairsim::RotorTurningDirection::kRotorTurningDirectionCCW),
            -1);
  EXPECT_EQ(static_cast<int>(
                projectairsim::RotorTurningDirection::kRotorTurningDirectionCW),
            1);
}

TEST(RotorSetting, CalculatesPositiveThrustTorqueAndSpeedSquare) {
  // General description:
  // Verifies that valid physical parameters produce positive magnitudes.
  // Arrange: prepare context for `projectairsim::RotorSetting rotor;`.
  projectairsim::RotorSetting rotor;
  rotor.max_rpm = 8000.0f;
  rotor.propeller_diameter = 0.254f;
  rotor.coeff_of_thrust = 0.109919f;
  rotor.coeff_of_torque = 0.040164f;

  // Act: run `rotor.CalcMaxThrustAndTorque();`.
  rotor.CalcMaxThrustAndTorque();

  // Assert: check result from `EXPECT_GT(rotor.max_speed_square, 0.0f);`.
  EXPECT_GT(rotor.max_speed_square, 0.0f);
  EXPECT_GT(rotor.max_thrust, 0.0f);
  EXPECT_GT(rotor.max_torque, 0.0f);
}

TEST(RotorSetting, HigherRpmProducesHigherThrustAndTorque) {
  // General description:
  // Verifies monotonic relationship between RPM and aerodynamic outputs.
  // Arrange: prepare context for `projectairsim::RotorSetting slow;`.
  projectairsim::RotorSetting slow;
  slow.max_rpm = 4000.0f;
  slow.propeller_diameter = 0.254f;
  slow.coeff_of_thrust = 0.109919f;
  slow.coeff_of_torque = 0.040164f;
  // Act: run `slow.CalcMaxThrustAndTorque();`.
  slow.CalcMaxThrustAndTorque();

  projectairsim::RotorSetting fast = slow;
  fast.max_rpm = 8000.0f;
  fast.CalcMaxThrustAndTorque();

  // Assert: check result from `EXPECT_GT(fast.max_speed_square, slow.max_speed_square);`.
  EXPECT_GT(fast.max_speed_square, slow.max_speed_square);
  EXPECT_GT(fast.max_thrust, slow.max_thrust);
  EXPECT_GT(fast.max_torque, slow.max_torque);
}
