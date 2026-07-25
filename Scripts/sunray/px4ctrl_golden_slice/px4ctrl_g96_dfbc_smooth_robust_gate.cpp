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
    double smooth_feedback_accel_x{0.0};
    double disturbance_estimate_x{0.0};
    double compensated_accel_x{0.0};
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

    const ControllerOutput out = mosim_px4ctrl::calculate_dfbc_smooth_robust_core(params, state, base_input());
    stats.hover_thrust_error = std::fabs(out.normalized_thrust - params.hover_percentage);
    if (stats.hover_thrust_error > 1.0e-12 ||
        quat_min_norm(out.desired_attitude, Quat{}) > 1.0e-12 ||
        mosim_px4ctrl::norm(out.disturbance_estimate) > 1.0e-12)
    {
        fail(stats, "hover_identity", "smooth robust DFBC hover must keep level attitude, hover thrust, and zero disturbance estimate");
    }
}

void run_smooth_feedback_case(GateStats &stats)
{
    CoreParams params;
    params.hover_percentage = 0.37;
    params.tilt_limit_rad = 1.2;
    params.smooth_feedback_gain[0] = 5.0;
    params.smooth_feedback_bound[0] = 0.8;
    params.kv[0] = 0.0;
    params.disturbance_observer_gain[0] = 0.0;
    CoreState state;
    mosim_px4ctrl::reset_thrust_mapping(params, state);

    auto in = base_input();
    in.reference_position = Vec3{10.0, 0.0, 1.0};
    const ControllerOutput out = mosim_px4ctrl::calculate_dfbc_smooth_robust_core(params, state, in);
    stats.smooth_feedback_accel_x = out.desired_acceleration.x;
    if (stats.smooth_feedback_accel_x < 0.79 || stats.smooth_feedback_accel_x > 0.81)
    {
        fail(stats, "smooth_feedback_bound", "large position error must saturate smoothly near configured bounded feedback acceleration");
    }
}

void run_disturbance_observer_case(GateStats &stats)
{
    CoreParams params;
    params.hover_percentage = 0.37;
    params.tilt_limit_rad = 1.2;
    params.indi_accel_lpf_alpha = 1.0;
    params.indi_measured_accel_limit[0] = 6.0;
    params.disturbance_observer_gain[0] = 1.0;
    params.disturbance_compensation_limit[0] = 0.5;
    CoreState state;
    mosim_px4ctrl::reset_thrust_mapping(params, state);

    auto in = base_input();
    (void)mosim_px4ctrl::calculate_dfbc_smooth_robust_core(params, state, in);

    in.velocity = Vec3{0.2, 0.0, 0.0};
    const ControllerOutput out = mosim_px4ctrl::calculate_dfbc_smooth_robust_core(params, state, in);
    stats.disturbance_estimate_x = out.disturbance_estimate.x;
    stats.compensated_accel_x = out.desired_acceleration.x;
    if (std::fabs(stats.disturbance_estimate_x - params.disturbance_compensation_limit[0]) > kTol ||
        stats.compensated_accel_x > -0.49)
    {
        fail(stats, "disturbance_observer_clamp", "acceleration residual must update and clamp disturbance estimate before compensation");
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
    const ControllerOutput out = mosim_px4ctrl::calculate_dfbc_smooth_robust_core(params, state, in);
    stats.jerk_body_rate_x = out.desired_body_rate.x;
    stats.yaw_rate_body_rate_z = out.desired_body_rate.z;
    if (stats.jerk_body_rate_x >= -0.01 ||
        std::fabs(stats.yaw_rate_body_rate_z - in.reference_yaw_rate) > 1.0e-6)
    {
        fail(stats, "high_order_feedforward", "smooth robust DFBC must preserve high-order body-rate feedforward");
    }

    in.enable = false;
    const ControllerOutput disabled = mosim_px4ctrl::calculate_dfbc_smooth_robust_core(params, state, in);
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
    run_smooth_feedback_case(stats);
    run_disturbance_observer_case(stats);
    run_high_order_and_disabled_cases(stats);

    std::cout << std::setprecision(17);
    std::cout << "{\n";
    std::cout << "  \"schema\": \"mosim.g96_dfbc_smooth_robust_static_gate.v1\",\n";
    std::cout << "  \"status\": \"" << (stats.failures == 0 ? "passed" : "failed") << "\",\n";
    std::cout << "  \"claim_boundary\": \"Static smooth robust DFBC core gate only. It proves bounded feedback, acceleration-residual DOB clamp, and high-order feedforward fields inside the controller core. It does not prove wind-tunnel performance, ROS/Gazebo runtime, MWORKS code generation, body-rate publishing, or PX4-native deployment.\",\n";
    std::cout << "  \"failure_count\": " << stats.failures << ",\n";
    std::cout << "  \"hover_thrust_error\": " << stats.hover_thrust_error << ",\n";
    std::cout << "  \"smooth_feedback_accel_x\": " << stats.smooth_feedback_accel_x << ",\n";
    std::cout << "  \"disturbance_estimate_x\": " << stats.disturbance_estimate_x << ",\n";
    std::cout << "  \"compensated_accel_x\": " << stats.compensated_accel_x << ",\n";
    std::cout << "  \"jerk_body_rate_x\": " << stats.jerk_body_rate_x << ",\n";
    std::cout << "  \"yaw_rate_body_rate_z\": " << stats.yaw_rate_body_rate_z << "\n";
    std::cout << "}\n";

    return stats.failures == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
