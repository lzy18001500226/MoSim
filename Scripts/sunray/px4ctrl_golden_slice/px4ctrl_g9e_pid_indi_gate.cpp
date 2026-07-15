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
    double hover_quat_error{0.0};
    double residual_x{0.0};
    double bounded_increment_x{0.0};
    double saturated_thrust{0.0};
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

bool finite_quat(const Quat &q)
{
    return std::isfinite(q.w) && std::isfinite(q.x) && std::isfinite(q.y) && std::isfinite(q.z);
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
    in.reference_yaw = 0.0;
    return in;
}

void run_hover_case(GateStats &stats)
{
    CoreParams params;
    params.hover_percentage = 0.294;
    params.min_normalized_thrust = 0.0;
    params.max_normalized_thrust = 1.0;
    params.tilt_limit_rad = 0.8;
    CoreState state;
    mosim_px4ctrl::reset_thrust_mapping(params, state);

    const ControllerOutput out = mosim_px4ctrl::calculate_pid_indi_bounded_core(params, state, base_input());
    stats.hover_thrust_error = std::fabs(out.normalized_thrust - params.hover_percentage);
    stats.hover_quat_error = quat_min_norm(out.desired_attitude, Quat{});
    if (stats.hover_thrust_error > 1.0e-12 || stats.hover_quat_error > 1.0e-12)
    {
        fail(stats, "hover_identity", "PID-INDI hover must produce level attitude and hover normalized thrust");
    }
    if (out.status_text != "pid_indi_bounded_attitude_thrust")
    {
        fail(stats, "status_text", "PID-INDI status text did not identify the backend");
    }
}

void run_increment_case(GateStats &stats)
{
    CoreParams params;
    params.kp[0] = 0.0;
    params.kp[1] = 0.0;
    params.kp[2] = 0.0;
    params.kv[0] = 0.0;
    params.kv[1] = 0.0;
    params.kv[2] = 0.0;
    params.hover_percentage = 0.294;
    params.indi_gain[0] = 1.0;
    params.indi_increment_limit[0] = 0.2;
    params.indi_measured_accel_limit[0] = 10.0;
    params.indi_accel_lpf_alpha = 1.0;
    CoreState state;
    mosim_px4ctrl::reset_thrust_mapping(params, state);

    auto in = base_input();
    in.reference_acceleration = Vec3{1.0, 0.0, 0.0};
    const ControllerOutput first = mosim_px4ctrl::calculate_pid_indi_bounded_core(params, state, in);
    if (std::fabs(first.desired_acceleration.x - 1.0) > kTol)
    {
        fail(stats, "first_sample_no_increment", "first sample must not inject INDI correction before velocity derivative exists");
    }

    in.velocity = Vec3{0.0, 0.0, 0.0};
    const ControllerOutput second = mosim_px4ctrl::calculate_pid_indi_bounded_core(params, state, in);
    stats.residual_x = second.sliding_surface.x;
    stats.bounded_increment_x = second.desired_acceleration.x - 1.0;
    if (std::fabs(stats.residual_x - 1.0) > kTol ||
        std::fabs(stats.bounded_increment_x - params.indi_increment_limit[0]) > kTol)
    {
        fail(stats, "bounded_increment", "INDI residual correction must be bounded by increment_limit");
    }
}

void run_limit_and_disabled_cases(GateStats &stats)
{
    CoreParams params;
    params.hover_percentage = 0.294;
    params.min_normalized_thrust = 0.0;
    params.max_normalized_thrust = 0.40;
    params.kp[2] = 20.0;
    CoreState state;
    mosim_px4ctrl::reset_thrust_mapping(params, state);

    auto in = base_input();
    in.position = Vec3{0.0, 0.0, -2.0};
    const ControllerOutput limited = mosim_px4ctrl::calculate_pid_indi_bounded_core(params, state, in);
    stats.saturated_thrust = limited.normalized_thrust;
    if (!limited.saturated || stats.saturated_thrust > params.max_normalized_thrust + kTol)
    {
        fail(stats, "thrust_limit", "PID-INDI thrust limit was not enforced");
    }

    in.enable = false;
    const ControllerOutput disabled = mosim_px4ctrl::calculate_pid_indi_bounded_core(params, state, in);
    if (disabled.status_code != 1 ||
        disabled.normalized_thrust != 0.0 ||
        quat_min_norm(disabled.desired_attitude, in.imu_attitude) > kTol ||
        !finite_quat(disabled.desired_attitude))
    {
        fail(stats, "disabled_output", "disabled controller output is not neutral attitude plus zero thrust");
    }
}

} // namespace

int main()
{
    GateStats stats;

    run_hover_case(stats);
    run_increment_case(stats);
    run_limit_and_disabled_cases(stats);

    std::cout << std::setprecision(17);
    std::cout << "{\n";
    std::cout << "  \"schema\": \"mosim.g9e_pid_indi_static_gate.v1\",\n";
    std::cout << "  \"status\": \"" << (stats.failures == 0 ? "passed" : "failed") << "\",\n";
    std::cout << "  \"claim_boundary\": \"Static PID plus bounded INDI acceleration-increment ATTITUDE_THRUST backend gate only. No rotor-level, body-rate-level, actuator-effectiveness INDI, ROS, Gazebo, PX4, MAVROS, RViz, UE, or MWORKS runtime is executed.\",\n";
    std::cout << "  \"failure_count\": " << stats.failures << ",\n";
    std::cout << "  \"hover_thrust_error\": " << stats.hover_thrust_error << ",\n";
    std::cout << "  \"hover_quat_error\": " << stats.hover_quat_error << ",\n";
    std::cout << "  \"residual_x\": " << stats.residual_x << ",\n";
    std::cout << "  \"bounded_increment_x\": " << stats.bounded_increment_x << ",\n";
    std::cout << "  \"saturated_thrust\": " << stats.saturated_thrust << "\n";
    std::cout << "}\n";

    return stats.failures == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
