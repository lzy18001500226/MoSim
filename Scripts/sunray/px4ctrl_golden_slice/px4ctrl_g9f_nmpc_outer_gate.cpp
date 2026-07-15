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
    double horizon_acc_x{0.0};
    double accel_limit_x{0.0};
    double increment_limited_x{0.0};
    double yaw_error_rad{0.0};
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

    const ControllerOutput out = mosim_px4ctrl::calculate_nmpc_outer_core(params, state, base_input());
    stats.hover_thrust_error = std::fabs(out.normalized_thrust - params.hover_percentage);
    stats.hover_quat_error = quat_min_norm(out.desired_attitude, Quat{});
    if (stats.hover_thrust_error > 1.0e-12 || stats.hover_quat_error > 1.0e-12)
    {
        fail(stats, "hover_identity", "NMPC outer hover must produce level attitude and hover normalized thrust");
    }
    if (out.status_text != "nmpc_outer_attitude_thrust")
    {
        fail(stats, "status_text", "NMPC outer status text did not identify the backend");
    }
}

void run_horizon_and_limit_cases(GateStats &stats)
{
    CoreParams params;
    params.hover_percentage = 0.294;
    params.nmpc_horizon_s = 0.5;
    params.nmpc_position_weight[0] = 1.0;
    params.nmpc_velocity_weight[0] = 0.0;
    params.nmpc_control_weight[0] = 0.0;
    params.nmpc_accel_limit[0] = 10.0;
    params.nmpc_increment_limit[0] = 10.0;
    CoreState state;
    mosim_px4ctrl::reset_thrust_mapping(params, state);

    auto in = base_input();
    in.reference_position = Vec3{1.0, 0.0, 1.0};
    const ControllerOutput horizon = mosim_px4ctrl::calculate_nmpc_outer_core(params, state, in);
    stats.horizon_acc_x = horizon.desired_acceleration.x;
    if (std::fabs(stats.horizon_acc_x - 8.0) > kTol)
    {
        fail(stats, "horizon_solution", "short-horizon quadratic solution did not match expected constant-acceleration result");
    }

    params.nmpc_accel_limit[0] = 0.5;
    mosim_px4ctrl::reset_thrust_mapping(params, state);
    const ControllerOutput limited = mosim_px4ctrl::calculate_nmpc_outer_core(params, state, in);
    stats.accel_limit_x = limited.desired_acceleration.x;
    if (!limited.saturated || std::fabs(stats.accel_limit_x - params.nmpc_accel_limit[0]) > kTol)
    {
        fail(stats, "accel_limit", "NMPC outer acceleration limit was not enforced");
    }

    params.nmpc_accel_limit[0] = 10.0;
    params.nmpc_increment_limit[0] = 0.25;
    mosim_px4ctrl::reset_thrust_mapping(params, state);
    const ControllerOutput increment_limited = mosim_px4ctrl::calculate_nmpc_outer_core(params, state, in);
    stats.increment_limited_x = increment_limited.desired_acceleration.x;
    if (!increment_limited.saturated || std::fabs(stats.increment_limited_x - params.nmpc_increment_limit[0]) > kTol)
    {
        fail(stats, "increment_limit", "NMPC outer command increment limit was not enforced");
    }
}

void run_yaw_and_disabled_cases(GateStats &stats)
{
    CoreParams params;
    params.hover_percentage = 0.294;
    CoreState state;
    mosim_px4ctrl::reset_thrust_mapping(params, state);

    auto in = base_input();
    in.reference_yaw = 0.6;
    const ControllerOutput yaw_out = mosim_px4ctrl::calculate_nmpc_outer_core(params, state, in);
    stats.yaw_error_rad = std::fabs(mosim_px4ctrl::yaw_from_quat(yaw_out.desired_attitude) - 0.6);
    if (stats.yaw_error_rad > 1.0e-9)
    {
        fail(stats, "yaw_preserved", "level NMPC outer attitude did not preserve reference yaw");
    }

    in.enable = false;
    const ControllerOutput disabled = mosim_px4ctrl::calculate_nmpc_outer_core(params, state, in);
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
    run_horizon_and_limit_cases(stats);
    run_yaw_and_disabled_cases(stats);

    std::cout << std::setprecision(17);
    std::cout << "{\n";
    std::cout << "  \"schema\": \"mosim.g9f_nmpc_outer_static_gate.v1\",\n";
    std::cout << "  \"status\": \"" << (stats.failures == 0 ? "passed" : "failed") << "\",\n";
    std::cout << "  \"claim_boundary\": \"Static short-horizon constrained outer-loop ATTITUDE_THRUST backend gate only. This is not a full nonlinear online solver, rotor-level NMPC, ROS, Gazebo, PX4, MAVROS, RViz, UE, or MWORKS runtime evidence.\",\n";
    std::cout << "  \"failure_count\": " << stats.failures << ",\n";
    std::cout << "  \"hover_thrust_error\": " << stats.hover_thrust_error << ",\n";
    std::cout << "  \"hover_quat_error\": " << stats.hover_quat_error << ",\n";
    std::cout << "  \"horizon_acc_x\": " << stats.horizon_acc_x << ",\n";
    std::cout << "  \"accel_limit_x\": " << stats.accel_limit_x << ",\n";
    std::cout << "  \"increment_limited_x\": " << stats.increment_limited_x << ",\n";
    std::cout << "  \"yaw_error_rad\": " << stats.yaw_error_rad << "\n";
    std::cout << "}\n";

    return stats.failures == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
