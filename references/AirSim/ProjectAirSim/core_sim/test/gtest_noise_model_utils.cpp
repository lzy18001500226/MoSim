// Copyright (C) 2025 IAMAI CONSULTING CORP
//
// MIT License. All rights reserved.

#include <cmath>
#include <limits>

#include "core_sim/physics_common_types.hpp"
#include "core_sim/sensors/noise_model_utils.hpp"
#include "gtest/gtest.h"

namespace projectairsim = microsoft::projectairsim;

TEST(RandomGenerator, ResetProducesDeterministicSequence) {
  // General description:
  // Verifies that reset() restarts the scalar Gaussian sequence.
  // Arrange: prepare context for `projectairsim::RandomGeneratorGaussianF gen(0.0f, 1.0f);`.
  projectairsim::RandomGeneratorGaussianF gen(0.0f, 1.0f);

  const float a1 = gen.next();
  const float a2 = gen.next();
  const float a3 = gen.next();

  // Act: run `gen.reset();`.
  gen.reset();

  const float b1 = gen.next();
  const float b2 = gen.next();
  const float b3 = gen.next();

  // Assert: check result from `EXPECT_FLOAT_EQ(a1, b1);`.
  EXPECT_FLOAT_EQ(a1, b1);
  EXPECT_FLOAT_EQ(a2, b2);
  EXPECT_FLOAT_EQ(a3, b3);
}

TEST(RandomVectorGaussian, ResetProducesDeterministicSequence) {
  // General description:
  // Verifies reset-based determinism in vector Gaussian generator.
  // Arrange: prepare context for `const projectairsim::Vector3 mean(1.0, 2.0, 3.0);`.
  const projectairsim::Vector3 mean(1.0, 2.0, 3.0);
  const projectairsim::Vector3 stddev(0.1, 0.2, 0.3);
  projectairsim::RandomVectorGaussianR generator(mean, stddev);

  const auto v1 = generator.next();
  const auto v2 = generator.next();

  // Act: run `generator.reset();`.
  generator.reset();

  const auto w1 = generator.next();
  const auto w2 = generator.next();

  // Assert: check result from `EXPECT_DOUBLE_EQ(v1.x(), w1.x());`.
  EXPECT_DOUBLE_EQ(v1.x(), w1.x());
  EXPECT_DOUBLE_EQ(v1.y(), w1.y());
  EXPECT_DOUBLE_EQ(v1.z(), w1.z());
  EXPECT_DOUBLE_EQ(v2.x(), w2.x());
  EXPECT_DOUBLE_EQ(v2.y(), w2.y());
  EXPECT_DOUBLE_EQ(v2.z(), w2.z());
}

TEST(GaussianMarkov, ResetRestoresInitialOutput) {
  // General description:
  // Verifies that GaussianMarkov returns to initial output after Reset().
  // Arrange: prepare context for `projectairsim::GaussianMarkov markov(0.2f, 0.5f, 1.25f);`.
  projectairsim::GaussianMarkov markov(0.2f, 0.5f, 1.25f);

  EXPECT_FLOAT_EQ(markov.getOutput(), 1.25f);

  // Act: run `markov.Update(0.1);`.
  markov.Update(0.1);
  EXPECT_NE(markov.getOutput(), 1.25f);

  // Assert: check result from `markov.Reset();`.
  markov.Reset();
  EXPECT_FLOAT_EQ(markov.getOutput(), 1.25f);
}

TEST(GaussianMarkov, HandlesNaNInitialOutputWithFiniteState) {
  // General description:
  // Verifies robustness with NaN initial output while keeping finite state.
  // Arrange: prepare context for `projectairsim::GaussianMarkov markov;`.
  projectairsim::GaussianMarkov markov;
  markov.Initialize(0.2f, 0.5f, std::numeric_limits<float>::quiet_NaN());

  // Act: run `EXPECT_TRUE(std::isfinite(markov.getOutput()));`.
  // Assert: check result from `EXPECT_TRUE(std::isfinite(markov.getOutput()));`.
  EXPECT_TRUE(std::isfinite(markov.getOutput()));

  markov.Update(0.05);
  EXPECT_TRUE(std::isfinite(markov.getOutput()));
}
