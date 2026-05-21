#include <gtest/gtest.h>
#include "core_sim/transforms/transform_utils.hpp"
#include "core_sim/math_utils.hpp"
#include <cmath>

using namespace microsoft::projectairsim;

class CoordinateIntegrationTest : public ::testing::Test {
protected:
    const float kEpsilon = 1e-5f;
};

// Test NED to NEU Linear Conversion (Z inversion)
// NED: X=North, Y=East, Z=Down
// NEU: X=North, Y=East, Z=Up
TEST_F(CoordinateIntegrationTest, NedToNeuLinearConversion) {
    // General description:
    // Verifies NED->NEU linear conversion with correct Z-axis inversion.
    // Arrange: prepare context for `Vector3 ned(10.0f, 5.0f, -2.0f); // 2 meters up in NED`.
    Vector3 ned(10.0f, 5.0f, -2.0f); // 2 meters up in NED

    // Act: run `Vector3 neu = TransformUtils::NedToNeuLinear(ned);`.
    Vector3 neu = TransformUtils::NedToNeuLinear(ned);
    
    // Assert: check result from `EXPECT_NEAR(neu.x(), 10.0f, kEpsilon);`.
    EXPECT_NEAR(neu.x(), 10.0f, kEpsilon);
    EXPECT_NEAR(neu.y(), 5.0f, kEpsilon);
    EXPECT_NEAR(neu.z(), 2.0f, kEpsilon); // Should be 2 meters up in NEU
}

// Test NEU to NED Linear Conversion
TEST_F(CoordinateIntegrationTest, NeuToNedLinearConversion) {
    // General description:
    // Verifies inverse NEU->NED conversion preserving X/Y and negating Z.
    // Arrange: prepare context for `Vector3 neu(10.0f, 5.0f, 2.0f);`.
    Vector3 neu(10.0f, 5.0f, 2.0f); 

    // Act: run `Vector3 ned = TransformUtils::NeuToNedLinear(neu);`.
    Vector3 ned = TransformUtils::NeuToNedLinear(neu);
    
    // Assert: check result from `EXPECT_NEAR(ned.x(), 10.0f, kEpsilon);`.
    EXPECT_NEAR(ned.x(), 10.0f, kEpsilon);
    EXPECT_NEAR(ned.y(), 5.0f, kEpsilon);
    EXPECT_NEAR(ned.z(), -2.0f, kEpsilon);
}

// Test Angular conversions (NED to NEU often involves sign changes in Pitch/Yaw or Roll depending on convention)
// Implementation: NedToNeuAngular = (-Roll, -Pitch, Yaw)
TEST_F(CoordinateIntegrationTest, NedToNeuAngularConversion) {
    // General description:
    // Verifies NED->NEU angular conversion according to implemented convention.
    // Arrange: prepare context for `Vector3 ned_angles(0.1f, 0.2f, 0.3f); // Roll, Pitch, Yaw in Rad`.
    Vector3 ned_angles(0.1f, 0.2f, 0.3f); // Roll, Pitch, Yaw in Rad

    // Act: run `Vector3 neu_angles = TransformUtils::NedToNeuAngular(ned_angles);`.
    Vector3 neu_angles = TransformUtils::NedToNeuAngular(ned_angles);
    
    // Check signs based on core_sim/src/transforms/transform_utils.cpp implementation
    // Assert: check result from `EXPECT_NEAR(neu_angles.x(), -ned_angles.x(), kEpsilon);`.
    EXPECT_NEAR(neu_angles.x(), -ned_angles.x(), kEpsilon);
    EXPECT_NEAR(neu_angles.y(), -ned_angles.y(), kEpsilon);
    EXPECT_NEAR(neu_angles.z(), ned_angles.z(), kEpsilon);
}

// Test Degrees/Radians utility
TEST_F(CoordinateIntegrationTest, DegreeRadianConversion) {
    // General description:
    // Verifies degree/radian round-trip conversion with negligible error.
    // Arrange: prepare context for `float deg = 180.0f;`.
    float deg = 180.0f;

    // Act: run `float rad = TransformUtils::ToRadians(deg);`.
    float rad = TransformUtils::ToRadians(deg);

    // Assert: check result from `EXPECT_NEAR(rad, M_PI, kEpsilon);`.
    EXPECT_NEAR(rad, M_PI, kEpsilon);
    
    // Act: run `float deg_back = TransformUtils::ToDegrees(rad);`.
    float deg_back = TransformUtils::ToDegrees(rad);

    // Assert: check result from `EXPECT_NEAR(deg_back, deg, kEpsilon);`.
    EXPECT_NEAR(deg_back, deg, kEpsilon);
}

// Test Zentimeters/Meters utility (Used for UE synchronization)
TEST_F(CoordinateIntegrationTest, DistanceUnitConversion) {
    // General description:
    // Verifies meter<->centimeter conversion used for UE synchronization.
    // Arrange: prepare context for `float meters = 1.5f;`.
    float meters = 1.5f;

    // Act: run `float cm = TransformUtils::ToCentimeters(meters);`.
    float cm = TransformUtils::ToCentimeters(meters);

    // Assert: check result from `EXPECT_NEAR(cm, 150.0f, kEpsilon);`.
    EXPECT_NEAR(cm, 150.0f, kEpsilon);
    
    // Act: run `float meters_back = TransformUtils::ToMeters(cm);`.
    float meters_back = TransformUtils::ToMeters(cm);

    // Assert: check result from `EXPECT_NEAR(meters_back, meters, kEpsilon);`.
    EXPECT_NEAR(meters_back, meters, kEpsilon);
}
