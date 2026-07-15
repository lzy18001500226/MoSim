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

constexpr double kTol = 1.0e-10;

struct GateStats
{
    int failures{0};
    double max_px4ctrl_compat_diff{0.0};
    double integral_thrust_delta{0.0};
    double reset_thrust_delta{0.0};
};

Quat quat_from_rpy(double roll, double pitch, double yaw)
{
    return mosim_px4ctrl::multiply(
        mosim_px4ctrl::multiply(
            mosim_px4ctrl::angle_axis(yaw, Vec3{0.0, 0.0, 1.0}),
            mosim_px4ctrl::angle_axis(pitch, Vec3{0.0, 1.0, 0.0})),
        mosim_px4ctrl::angle_axis(roll, Vec3{1.0, 0.0, 0.0}));
}

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

ControllerInput base_input()
{
    ControllerInput in;
    in.dt = 0.01;
    in.position = Vec3{0.0, 0.0, 1.0};
    in.velocity = Vec3{0.0, 0.0, 0.0};
    in.attitude = quat_from_rpy(0.01, -0.02, 0.1);
    in.imu_attitude = in.attitude;
    in.reference_position = Vec3{0.0, 0.0, 1.0};
    in.reference_velocity = Vec3{0.0, 0.0, 0.0};
    in.reference_acceleration = Vec3{0.0, 0.0, 0.0};
    in.reference_yaw = 0.1;
    return in;
}

void fail(GateStats &stats, const std::string &name, const std::string &message)
{
    ++stats.failures;
    std::cerr << "FAILED_CASE " << name << " " << message << "\n";
}

void run_compatibility_case(GateStats &stats)
{
    CoreParams params;
    params.kp[0] = 1.2;
    params.kp[1] = 1.3;
    params.kp[2] = 1.4;
    params.kv[0] = 0.8;
    params.kv[1] = 0.9;
    params.kv[2] = 1.0;
    params.ki[0] = 0.0;
    params.ki[1] = 0.0;
    params.ki[2] = 0.0;
    params.mass = 0.67;
    params.gravity = 9.8;
    params.hover_percentage = 0.294;
    params.max_normalized_thrust = 2.0;
    params.tilt_limit_rad = 1.2;

    CoreState px4_state;
    CoreState pid_state;
    mosim_px4ctrl::reset_thrust_mapping(params, px4_state);
    mosim_px4ctrl::reset_thrust_mapping(params, pid_state);

    auto in = base_input();
    in.position = Vec3{0.08, -0.06, 0.93};
    in.velocity = Vec3{-0.03, 0.02, 0.01};
    in.reference_position = Vec3{0.0, 0.0, 1.0};
    in.reference_velocity = Vec3{0.0, 0.0, 0.0};
    in.reference_acceleration = Vec3{0.1, -0.05, 0.0};

    const ControllerOutput px4 = mosim_px4ctrl::calculate_px4ctrl_core(params, px4_state, in);
    const ControllerOutput pid = mosim_px4ctrl::calculate_official_pid_core(params, pid_state, in);
    stats.max_px4ctrl_compat_diff = std::max(
        std::fabs(px4.normalized_thrust - pid.normalized_thrust),
        quat_min_norm(px4.desired_attitude, pid.desired_attitude));
    if (stats.max_px4ctrl_compat_diff > kTol)
    {
        fail(stats, "ki_zero_compatibility", "official_pid must match px4ctrl core when Ki=0 and limits are inactive");
    }
}

void run_integral_case(GateStats &stats)
{
    CoreParams params;
    params.kp[2] = 0.6;
    params.kv[2] = 0.1;
    params.ki[2] = 1.0;
    params.integral_limit[2] = 0.5;
    params.hover_percentage = 0.294;
    params.max_normalized_thrust = 2.0;
    params.tilt_limit_rad = 1.2;

    CoreState state;
    mosim_px4ctrl::reset_thrust_mapping(params, state);

    auto in = base_input();
    in.position = Vec3{0.0, 0.0, 0.8};
    in.reference_position = Vec3{0.0, 0.0, 1.0};

    const ControllerOutput first = mosim_px4ctrl::calculate_official_pid_core(params, state, in);
    ControllerOutput last = first;
    for (int i = 0; i < 80; ++i)
    {
        last = mosim_px4ctrl::calculate_official_pid_core(params, state, in);
    }
    stats.integral_thrust_delta = last.normalized_thrust - first.normalized_thrust;
    if (stats.integral_thrust_delta <= 0.001)
    {
        fail(stats, "integral_accumulates", "normalized thrust did not increase under persistent positive Z error");
    }

    in.reset = true;
    const ControllerOutput after_reset = mosim_px4ctrl::calculate_official_pid_core(params, state, in);
    stats.reset_thrust_delta = std::fabs(after_reset.normalized_thrust - first.normalized_thrust);
    if (stats.reset_thrust_delta > 1.0e-6)
    {
        fail(stats, "reset_clears_integral", "reset did not clear accumulated PID integral state");
    }
}

void run_limit_and_disabled_cases(GateStats &stats)
{
    CoreParams params;
    params.kp[0] = 15.0;
    params.kp[2] = 20.0;
    params.hover_percentage = 0.294;
    params.max_normalized_thrust = 0.42;
    params.tilt_limit_rad = 0.05;

    CoreState state;
    mosim_px4ctrl::reset_thrust_mapping(params, state);

    auto in = base_input();
    in.position = Vec3{-3.0, 0.0, 0.0};
    in.reference_position = Vec3{0.0, 0.0, 2.0};
    const ControllerOutput limited = mosim_px4ctrl::calculate_official_pid_core(params, state, in);
    if (!limited.saturated ||
        limited.normalized_thrust > params.max_normalized_thrust + kTol ||
        !finite_quat(limited.desired_attitude))
    {
        fail(stats, "limit_enforced", "official_pid did not report/enforce thrust or tilt saturation cleanly");
    }

    in.enable = false;
    const ControllerOutput disabled = mosim_px4ctrl::calculate_official_pid_core(params, state, in);
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

    run_compatibility_case(stats);
    run_integral_case(stats);
    run_limit_and_disabled_cases(stats);

    std::cout << std::setprecision(17);
    std::cout << "{\n";
    std::cout << "  \"schema\": \"mosim.g9a_official_pid_static_gate.v1\",\n";
    std::cout << "  \"status\": \"" << (stats.failures == 0 ? "passed" : "failed") << "\",\n";
    std::cout << "  \"claim_boundary\": \"Static official_pid ATTITUDE_THRUST backend gate only. No ROS, Gazebo, PX4, MAVROS, RViz, UE, or MWORKS runtime is executed.\",\n";
    std::cout << "  \"failure_count\": " << stats.failures << ",\n";
    std::cout << "  \"max_px4ctrl_compat_diff_when_ki_zero\": " << stats.max_px4ctrl_compat_diff << ",\n";
    std::cout << "  \"integral_thrust_delta\": " << stats.integral_thrust_delta << ",\n";
    std::cout << "  \"reset_thrust_delta\": " << stats.reset_thrust_delta << "\n";
    std::cout << "}\n";

    return stats.failures == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
