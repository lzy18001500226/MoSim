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
    double first_cycle_increment_norm{0.0};
    double second_cycle_increment_x{0.0};
    double second_cycle_accel_x{0.0};
    double dob_nominal_disturbance_x{0.0};
    double dob_nominal_increment_x{0.0};
    double repeated_stamp_increment_x{0.0};
    double measured_stamp_dt_increment_x{0.0};
    double jerk_body_rate_x{0.0};
    double yaw_rate_body_rate_z{0.0};
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

void run_hover_case(GateStats &stats)
{
    CoreParams params;
    params.hover_percentage = 0.37;
    params.tilt_limit_rad = 0.8;
    CoreState state;
    mosim_px4ctrl::reset_thrust_mapping(params, state);

    const ControllerOutput out = mosim_px4ctrl::calculate_dfbc_smooth_robust_indi_core(params, state, base_input());
    stats.hover_thrust_error = std::fabs(out.normalized_thrust - params.hover_percentage);
    if (stats.hover_thrust_error > 1.0e-12 ||
        quat_min_norm(out.desired_attitude, Quat{}) > 1.0e-12 ||
        mosim_px4ctrl::norm(out.disturbance_estimate) > 1.0e-12 ||
        mosim_px4ctrl::norm(out.sliding_surface) > 1.0e-12)
    {
        fail(stats, "hover_identity", "DFBC smooth robust plus INDI must keep hover neutral on the first cycle");
    }
}

void run_indi_increment_case(GateStats &stats)
{
    CoreParams params;
    params.hover_percentage = 0.37;
    params.tilt_limit_rad = 1.2;
    params.smooth_feedback_gain[0] = 0.0;
    params.smooth_feedback_bound[0] = 0.8;
    params.kv[0] = 0.0;
    params.disturbance_observer_gain[0] = 0.0;
    params.indi_accel_lpf_alpha = 1.0;
    params.indi_gain[0] = 1.0;
    params.indi_increment_limit[0] = 0.25;
    params.indi_measured_accel_limit[0] = 10.0;
    CoreState state;
    mosim_px4ctrl::reset_thrust_mapping(params, state);

    auto in = base_input();
    in.reference_acceleration = Vec3{1.0, 0.0, 0.0};
    const ControllerOutput first = mosim_px4ctrl::calculate_dfbc_smooth_robust_indi_core(params, state, in);
    stats.first_cycle_increment_norm = mosim_px4ctrl::norm(first.sliding_surface);
    if (stats.first_cycle_increment_norm > kTol ||
        std::fabs(first.desired_acceleration.x - 1.0) > kTol)
    {
        fail(stats, "first_cycle_no_indi", "INDI increment must stay disabled until one previous velocity sample exists");
    }

    in.velocity = Vec3{0.0, 0.0, 0.0};
    const ControllerOutput second = mosim_px4ctrl::calculate_dfbc_smooth_robust_indi_core(params, state, in);
    stats.second_cycle_increment_x = second.desired_acceleration.x - 1.0;
    stats.second_cycle_accel_x = second.desired_acceleration.x;
    if (std::fabs(stats.second_cycle_increment_x + 0.25) > kTol ||
        std::fabs(stats.second_cycle_accel_x - 0.75) > kTol)
    {
        fail(stats, "bounded_indi_increment", "DFBC plus INDI must apply the configured bounded high-frequency residual when DOB is disabled");
    }
}

void run_dob_nominal_case(GateStats &stats)
{
    CoreParams params;
    params.hover_percentage = 0.37;
    params.tilt_limit_rad = 1.2;
    params.smooth_feedback_gain[0] = 0.0;
    params.smooth_feedback_bound[0] = 0.8;
    params.kv[0] = 0.0;
    params.disturbance_observer_gain[0] = 1.0;
    params.disturbance_compensation_limit[0] = 10.0;
    params.indi_accel_lpf_alpha = 1.0;
    params.indi_gain[0] = 1.0;
    params.indi_increment_limit[0] = 10.0;
    params.indi_measured_accel_limit[0] = 20.0;
    CoreState state;
    mosim_px4ctrl::reset_thrust_mapping(params, state);

    auto in = base_input();
    in.reference_acceleration = Vec3{1.0, 0.0, 0.0};
    (void)mosim_px4ctrl::calculate_dfbc_smooth_robust_indi_core(params, state, in);

    const ControllerOutput out = mosim_px4ctrl::calculate_dfbc_smooth_robust_indi_core(params, state, in);
    stats.dob_nominal_disturbance_x = out.disturbance_estimate.x;
    stats.dob_nominal_increment_x = out.desired_acceleration.x - (1.0 - out.disturbance_estimate.x);
    if (std::fabs(stats.dob_nominal_disturbance_x + 1.0) > kTol ||
        std::fabs(stats.dob_nominal_increment_x) > kTol)
    {
        fail(stats, "dob_nominal_compensation", "G10-C must keep G9.6 DOB as the nominal low-frequency residual compensation and reserve INDI for the remaining residual");
    }
}

void run_measurement_stamp_cases(GateStats &stats)
{
    CoreParams params;
    params.hover_percentage = 0.37;
    params.tilt_limit_rad = 1.2;
    params.smooth_feedback_gain[0] = 0.0;
    params.smooth_feedback_bound[0] = 0.8;
    params.kv[0] = 0.0;
    params.disturbance_observer_gain[0] = 0.0;
    params.indi_accel_lpf_alpha = 1.0;
    params.indi_gain[0] = 1.0;
    params.indi_increment_limit[0] = 10.0;
    params.indi_measured_accel_limit[0] = 20.0;
    CoreState state;
    mosim_px4ctrl::reset_thrust_mapping(params, state);

    auto in = base_input();
    in.reference_acceleration = Vec3{1.0, 0.0, 0.0};
    in.measurement_stamp_valid = true;
    in.measurement_stamp_s = 10.00;
    (void)mosim_px4ctrl::calculate_dfbc_smooth_robust_indi_core(params, state, in);

    in.measurement_stamp_s = 10.00;
    const ControllerOutput repeated = mosim_px4ctrl::calculate_dfbc_smooth_robust_indi_core(params, state, in);
    stats.repeated_stamp_increment_x = repeated.desired_acceleration.x - 1.0;
    if (std::fabs(stats.repeated_stamp_increment_x) > kTol)
    {
        fail(stats, "repeated_stamp_no_indi_update", "Repeated odom measurement stamps must not update INDI residual state");
    }

    in.velocity = Vec3{0.02, 0.0, 0.0};
    in.measurement_stamp_s = 10.02;
    const ControllerOutput updated = mosim_px4ctrl::calculate_dfbc_smooth_robust_indi_core(params, state, in);
    stats.measured_stamp_dt_increment_x = updated.desired_acceleration.x - 1.0;
    if (std::fabs(stats.measured_stamp_dt_increment_x) > kTol)
    {
        fail(stats, "measurement_stamp_dt", "A 0.02s odom stamp with 0.02m/s delta must estimate 1m/s^2 and produce zero INDI residual");
    }
}

void run_high_order_and_disabled_cases(GateStats &stats)
{
    CoreParams params;
    params.hover_percentage = 0.37;
    params.high_order_body_rate_limit[0] = 2.0;
    params.high_order_body_rate_limit[1] = 2.0;
    params.high_order_body_rate_limit[2] = 1.0;
    CoreState state;
    mosim_px4ctrl::reset_thrust_mapping(params, state);

    auto in = base_input();
    in.reference_jerk = Vec3{1.0, 0.0, 0.0};
    in.reference_yaw_rate = 0.25;
    const ControllerOutput out = mosim_px4ctrl::calculate_dfbc_smooth_robust_indi_core(params, state, in);
    stats.jerk_body_rate_x = out.desired_body_rate.x;
    stats.yaw_rate_body_rate_z = out.desired_body_rate.z;
    if (stats.jerk_body_rate_x >= -0.01 ||
        std::fabs(stats.yaw_rate_body_rate_z - in.reference_yaw_rate) > 1.0e-6)
    {
        fail(stats, "high_order_feedforward", "DFBC plus INDI must preserve high-order body-rate feedforward");
    }

    in.enable = false;
    const ControllerOutput disabled = mosim_px4ctrl::calculate_dfbc_smooth_robust_indi_core(params, state, in);
    if (disabled.status_code != 1 ||
        disabled.normalized_thrust != 0.0 ||
        quat_min_norm(disabled.desired_attitude, in.imu_attitude) > kTol)
    {
        fail(stats, "disabled_output", "disabled controller output is not neutral attitude plus zero thrust");
    }
}

} // namespace

int main()
{
    GateStats stats;

    run_hover_case(stats);
    run_indi_increment_case(stats);
    run_dob_nominal_case(stats);
    run_measurement_stamp_cases(stats);
    run_high_order_and_disabled_cases(stats);

    std::cout << std::setprecision(17);
    std::cout << "{\n";
    std::cout << "  \"schema\": \"mosim.g10c_dfbc_smooth_robust_indi_static_gate.v1\",\n";
    std::cout << "  \"status\": \"" << (stats.failures == 0 ? "passed" : "failed") << "\",\n";
    std::cout << "  \"claim_boundary\": \"Static DFBC smooth-robust DOB plus INDI core gate only. It proves the combined core keeps hover neutral, preserves G9.6 DOB as nominal low-frequency residual compensation, applies bounded INDI only to the remaining residual after a previous velocity sample exists, and preserves high-order feedforward fields. It does not prove ROS/Gazebo runtime, ablation improvement, MWORKS code generation, body-rate publishing, or PX4-native deployment.\",\n";
    std::cout << "  \"failure_count\": " << stats.failures << ",\n";
    std::cout << "  \"hover_thrust_error\": " << stats.hover_thrust_error << ",\n";
    std::cout << "  \"first_cycle_increment_norm\": " << stats.first_cycle_increment_norm << ",\n";
    std::cout << "  \"second_cycle_increment_x\": " << stats.second_cycle_increment_x << ",\n";
    std::cout << "  \"second_cycle_accel_x\": " << stats.second_cycle_accel_x << ",\n";
    std::cout << "  \"dob_nominal_disturbance_x\": " << stats.dob_nominal_disturbance_x << ",\n";
    std::cout << "  \"dob_nominal_increment_x\": " << stats.dob_nominal_increment_x << ",\n";
    std::cout << "  \"repeated_stamp_increment_x\": " << stats.repeated_stamp_increment_x << ",\n";
    std::cout << "  \"measured_stamp_dt_increment_x\": " << stats.measured_stamp_dt_increment_x << ",\n";
    std::cout << "  \"jerk_body_rate_x\": " << stats.jerk_body_rate_x << ",\n";
    std::cout << "  \"yaw_rate_body_rate_z\": " << stats.yaw_rate_body_rate_z << "\n";
    std::cout << "}\n";

    return stats.failures == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
