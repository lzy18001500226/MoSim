// Copyright (C) 2025 IAMAI CONSULTING CORP
//
// MIT License. All rights reserved.

#include "core_sim/actuators/control_mapper.hpp"
#include "gtest/gtest.h"

namespace projectairsim = microsoft::projectairsim;

TEST(ControlMapper, DefaultMappingIsIdentityInDefaultDomain) {
  // General description:
  // Verifies identity mapping in the default configuration.
  // Arrange: prepare context for `projectairsim::ControlMapper mapper;`.
  projectairsim::ControlMapper mapper;

  // Act: run `EXPECT_FLOAT_EQ(mapper(-1.0f), -1.0f);`.
  // Assert: check result from `EXPECT_FLOAT_EQ(mapper(-1.0f), -1.0f);`.
  EXPECT_FLOAT_EQ(mapper(-1.0f), -1.0f);
  EXPECT_FLOAT_EQ(mapper(0.0f), 0.0f);
  EXPECT_FLOAT_EQ(mapper(1.0f), 1.0f);
}

TEST(ControlMapper, InputIsClampedByDefault) {
  // General description:
  // Verifies default input clamping to the supported domain.
  // Arrange: prepare context for `projectairsim::ControlMapper mapper;`.
  projectairsim::ControlMapper mapper;

  // Act: run `EXPECT_FLOAT_EQ(mapper(-2.0f), -1.0f);`.
  // Assert: check result from `EXPECT_FLOAT_EQ(mapper(-2.0f), -1.0f);`.
  EXPECT_FLOAT_EQ(mapper(-2.0f), -1.0f);
  EXPECT_FLOAT_EQ(mapper(2.0f), 1.0f);
}

TEST(ControlMapper, CanDisableInputAndOutputClamping) {
  // General description:
  // Verifies that input and output clamping can be disabled.
  // Arrange: prepare context for `projectairsim::ControlMapper mapper;`.
  projectairsim::ControlMapper mapper;
  mapper.SetClampInput(false);
  mapper.SetClampOutput(false);

  // Act: run `EXPECT_FLOAT_EQ(mapper(-2.0f), -2.0f);`.
  // Assert: check result from `EXPECT_FLOAT_EQ(mapper(-2.0f), -2.0f);`.
  EXPECT_FLOAT_EQ(mapper(-2.0f), -2.0f);
  EXPECT_FLOAT_EQ(mapper(2.0f), 2.0f);
}

TEST(ControlMapper, DomainAndRangeCanBeUpdated) {
  // General description:
  // Verifies linear remapping after domain/range reconfiguration.
  // Arrange: prepare context for `projectairsim::ControlMapper mapper;`.
  projectairsim::ControlMapper mapper;
  mapper.SetDomain(1000.0f, 2000.0f);
  mapper.SetRange(0.0f, 1.0f);

  // Act: run `EXPECT_FLOAT_EQ(mapper(1000.0f), 0.0f);`.
  // Assert: check result from `EXPECT_FLOAT_EQ(mapper(1000.0f), 0.0f);`.
  EXPECT_FLOAT_EQ(mapper(1000.0f), 0.0f);
  EXPECT_FLOAT_EQ(mapper(1500.0f), 0.5f);
  EXPECT_FLOAT_EQ(mapper(2000.0f), 1.0f);
}

TEST(ControlMapper, GettersReturnConfiguredValues) {
  // General description:
  // Verifies that getters return exactly the configured values.
  // Arrange: prepare context for `projectairsim::ControlMapper mapper;`.
  projectairsim::ControlMapper mapper;
  mapper.SetClampInput(false);
  mapper.SetClampOutput(false);
  mapper.SetDomain(-10.0f, 10.0f);
  mapper.SetRange(-2.0f, 3.0f);
  mapper.SetScale(0.75f);

  bool clamp_input = true;
  bool clamp_output = true;
  float domain_min = 0.0f;
  float domain_max = 0.0f;
  float range_min = 0.0f;
  float range_max = 0.0f;
  float scale = 0.0f;

  // Act: run `mapper.GetClampInput(&clamp_input);`.
  mapper.GetClampInput(&clamp_input);
  mapper.GetClampOutput(&clamp_output);
  mapper.GetDomain(&domain_min, &domain_max);
  mapper.GetRange(&range_min, &range_max);
  mapper.GetScale(&scale);

  // Assert: check result from `EXPECT_FALSE(clamp_input);`.
  EXPECT_FALSE(clamp_input);
  EXPECT_FALSE(clamp_output);
  EXPECT_FLOAT_EQ(domain_min, -10.0f);
  EXPECT_FLOAT_EQ(domain_max, 10.0f);
  EXPECT_FLOAT_EQ(range_min, -2.0f);
  EXPECT_FLOAT_EQ(range_max, 3.0f);
  EXPECT_FLOAT_EQ(scale, 0.75f);
}
