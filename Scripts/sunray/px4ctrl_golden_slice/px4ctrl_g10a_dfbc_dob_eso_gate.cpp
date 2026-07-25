#include "px4ctrl_core.h"

#include <algorithm>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <string>

using mosim_px4ctrl::ControllerInput;
using mosim_px4ctrl::ControllerOutput;
using mosim_px4ctrl::CoreParams;
using mosim_px4ctrl::CoreState;
using mosim_px4ctrl::Quat;
using mosim_px4ctrl::Vec3;

namespace
{

constexpr double kTol = 1.0e-9;

struct GateStats
{
    int failures{0};
    double hover_thrust_error{0.0};
    double no_dob_accel_x{0.0};
    double dob_disturbance_x{0.0};
    double dob_compensated_accel_x{0.0};
    double dob_clamped_disturbance_x{0.0};
    double repeated_stamp_accel_x{0.0};
};

double quat_min_norm(const Quat &a, const Quat &b)
{
    const double same = std::sqrt(
        (a.w - b.w) * (a.w - b.w) +
        (a.x - b.x) * (a.x - b.x) +
        (a.y - b.y) * (a.y - b.y) +
        (a.z - b.z) * (a.z - b.z));
    const double neg = std::sqrt(
        (a.w + b.w) * (a.w + b.w) +
        (a.x + b.x) * (a.x + b.x) +
        (a.y + b.y) * (a.y + b.y) +
        (a.z + b.z) * (a.z + b.z));
    return std::min(same, neg);
}

void fail(GateStats &stats, const std::string &name, const std::string &message)
{
    ++stats.failures;
    std::cerr << "FAILED_CASE " << name << " " << message << "\n";
}

ControllerInput base_input()
{
    ControllerInput in;
    in.dt = 0.01;
    in.position = Vec3{0.0, 0.0, 1.0};
    in.velocity = Vec3{0.0, 0.0, 0.0};
    in.attitude = Quat{};
    in.imu_attitude = Quat{};
    in.reference_position = Vec3{0.0, 0.0, 1.0};
    in.reference_velocity = Vec3{0.0, 0.0, 0.0};
    in.reference_acceleration = Vec3{0.0, 0.0, 0.0};
    in.reference_jerk = Vec3{0.0, 0.0, 0.0};
    in.reference_snap = Vec3{0.0, 0.0, 0.0};
    in.reference_yaw = 0.0;
    in.reference_yaw_rate = 0.0;
    in.reference_yaw_acceleration = 0.0;
    return in;
}

CoreParams dob_test_params()
{
    CoreParams params;
    params.hover_percentage = 0.37;
    params.tilt_limit_rad = 1.2;
    params.kp[0] = 0.0;
    params.kv[0] = 0.0;
    params.smooth_feedback_gain[0] = 0.0;
    params.smooth_feedback_bound[0] = 0.0;
    params.indi_accel_lpf_alpha = 1.0;
    params.indi_measured_accel_limit[0] = 20.0;
    return params;
}

void run_hover_case(GateStats &stats)
{
    CoreParams params;
    params.hover_percentage = 0.37;
    params.tilt_limit_rad = 0.8;
    CoreState state;
    mosim_px4ctrl::reset_thrust_mapping(params, state);

    const ControllerOutput out = mosim_px4ctrl::calculate_dfbc_smooth_robust_core(params, state, base_input());
    stats.hover_thrust_error = std::fabs(out.normalized_thrust - params.hover_percentage);
    if (stats.hover_thrust_error > 1.0e-12 ||
        quat_min_norm(out.desired_attitude, Quat{}) > 1.0e-12 ||
        mosim_px4ctrl::norm(out.disturbance_estimate) > 1.0e-12)
    {
        fail(stats, "hover_identity", "G10-A DOB route must be neutral at hover with zero residual");
    }
}

void run_no_dob_ablation_case(GateStats &stats)
{
    CoreParams params = dob_test_params();
    params.disturbance_observer_gain[0] = 0.0;
    params.disturbance_compensation_limit[0] = 10.0;
    CoreState state;
    mosim_px4ctrl::reset_thrust_mapping(params, state);

    auto in = base_input();
    in.reference_acceleration = Vec3{1.0, 0.0, 0.0};
    (void)mosim_px4ctrl::calculate_dfbc_smooth_robust_core(params, state, in);

    const ControllerOutput out = mosim_px4ctrl::calculate_dfbc_smooth_robust_core(params, state, in);
    stats.no_dob_accel_x = out.desired_acceleration.x;
    if (std::fabs(out.disturbance_estimate.x) > kTol ||
        std::fabs(stats.no_dob_accel_x - 1.0) > kTol)
    {
        fail(stats, "no_dob_ablation", "DOB disabled ablation must keep residual estimate and compensation at zero");
    }
}

void run_dob_compensation_case(GateStats &stats)
{
    CoreParams params = dob_test_params();
    params.disturbance_observer_gain[0] = 1.0;
    params.disturbance_compensation_limit[0] = 10.0;
    CoreState state;
    mosim_px4ctrl::reset_thrust_mapping(params, state);

    auto in = base_input();
    in.reference_acceleration = Vec3{1.0, 0.0, 0.0};
    (void)mosim_px4ctrl::calculate_dfbc_smooth_robust_core(params, state, in);

    const ControllerOutput out = mosim_px4ctrl::calculate_dfbc_smooth_robust_core(params, state, in);
    stats.dob_disturbance_x = out.disturbance_estimate.x;
    stats.dob_compensated_accel_x = out.desired_acceleration.x;
    if (std::fabs(stats.dob_disturbance_x + 1.0) > kTol ||
        std::fabs(stats.dob_compensated_accel_x - 2.0) > kTol)
    {
        fail(stats, "dob_compensation", "DOB must estimate acceleration residual and compensate the nominal acceleration in the opposite direction");
    }
}

void run_dob_clamp_case(GateStats &stats)
{
    CoreParams params = dob_test_params();
    params.disturbance_observer_gain[0] = 1.0;
    params.disturbance_compensation_limit[0] = 0.35;
    CoreState state;
    mosim_px4ctrl::reset_thrust_mapping(params, state);

    auto in = base_input();
    in.reference_acceleration = Vec3{1.0, 0.0, 0.0};
    (void)mosim_px4ctrl::calculate_dfbc_smooth_robust_core(params, state, in);

    const ControllerOutput out = mosim_px4ctrl::calculate_dfbc_smooth_robust_core(params, state, in);
    stats.dob_clamped_disturbance_x = out.disturbance_estimate.x;
    if (std::fabs(stats.dob_clamped_disturbance_x + 0.35) > kTol ||
        std::fabs(out.desired_acceleration.x - 1.35) > kTol)
    {
        fail(stats, "dob_clamp", "DOB compensation must respect the configured acceleration limit");
    }
}

void run_measurement_stamp_case(GateStats &stats)
{
    CoreParams params = dob_test_params();
    params.disturbance_observer_gain[0] = 1.0;
    params.disturbance_compensation_limit[0] = 10.0;
    CoreState state;
    mosim_px4ctrl::reset_thrust_mapping(params, state);

    auto in = base_input();
    in.reference_acceleration = Vec3{1.0, 0.0, 0.0};
    in.measurement_stamp_valid = true;
    in.measurement_stamp_s = 12.0;
    (void)mosim_px4ctrl::calculate_dfbc_smooth_robust_core(params, state, in);

    in.measurement_stamp_s = 12.0;
    const ControllerOutput out = mosim_px4ctrl::calculate_dfbc_smooth_robust_core(params, state, in);
    stats.repeated_stamp_accel_x = out.desired_acceleration.x;
    if (std::fabs(out.disturbance_estimate.x) > kTol ||
        std::fabs(stats.repeated_stamp_accel_x - 1.0) > kTol)
    {
        fail(stats, "repeated_stamp_no_update", "Repeated measurement stamps must not update DOB residual state");
    }
}

} // namespace

int main()
{
    GateStats stats;

    run_hover_case(stats);
    run_no_dob_ablation_case(stats);
    run_dob_compensation_case(stats);
    run_dob_clamp_case(stats);
    run_measurement_stamp_case(stats);

    std::cout << std::setprecision(17);
    std::cout << "{\n";
    std::cout << "  \"schema\": \"mosim.g10a_dfbc_dob_eso_static_gate.v1\",\n";
    std::cout << "  \"status\": \"" << (stats.failures == 0 ? "passed" : "failed") << "\",\n";
    std::cout << "  \"claim_boundary\": \"Static G10-A DOB/ESO gate only. It proves the DFBC smooth bounded core has a separately ablatable low-frequency acceleration-residual disturbance observer, bounded compensation, and repeated-stamp protection. It does not prove ROS/Gazebo wind robustness, MWORKS code generation, PX4-native deployment, or runtime improvement without paired A/B metrics.\",\n";
    std::cout << "  \"failure_count\": " << stats.failures << ",\n";
    std::cout << "  \"hover_thrust_error\": " << stats.hover_thrust_error << ",\n";
    std::cout << "  \"no_dob_accel_x\": " << stats.no_dob_accel_x << ",\n";
    std::cout << "  \"dob_disturbance_x\": " << stats.dob_disturbance_x << ",\n";
    std::cout << "  \"dob_compensated_accel_x\": " << stats.dob_compensated_accel_x << ",\n";
    std::cout << "  \"dob_clamped_disturbance_x\": " << stats.dob_clamped_disturbance_x << ",\n";
    std::cout << "  \"repeated_stamp_accel_x\": " << stats.repeated_stamp_accel_x << "\n";
    std::cout << "}\n";

    return stats.failures == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
