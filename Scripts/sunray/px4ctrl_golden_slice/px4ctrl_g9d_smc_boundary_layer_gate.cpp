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
    double surface_x{0.0};
    double boundary_layer_acc_delta_x{0.0};
    double eta_saturated_acc_delta_x{0.0};
    double tilt_limited_b3_z{1.0};
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

Vec3 b3_from_quat(const Quat &q_raw)
{
    const Quat q = mosim_px4ctrl::normalize(q_raw);
    return Vec3{
        2.0 * (q.x * q.z + q.w * q.y),
        2.0 * (q.y * q.z - q.w * q.x),
        q.w * q.w - q.x * q.x - q.y * q.y + q.z * q.z,
    };
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

    const ControllerOutput out = mosim_px4ctrl::calculate_smc_boundary_layer_core(params, state, base_input());
    stats.hover_thrust_error = std::fabs(out.normalized_thrust - params.hover_percentage);
    stats.hover_quat_error = quat_min_norm(out.desired_attitude, Quat{});
    if (stats.hover_thrust_error > 1.0e-12 || stats.hover_quat_error > 1.0e-12)
    {
        fail(stats, "hover_identity", "SMC boundary-layer hover must produce level attitude and hover normalized thrust");
    }
    if (out.status_text != "smc_boundary_layer_attitude_thrust")
    {
        fail(stats, "status_text", "SMC boundary-layer status text did not identify the backend");
    }
}

void run_boundary_layer_case(GateStats &stats)
{
    CoreParams params;
    params.kp[0] = 0.0;
    params.kp[1] = 0.0;
    params.kp[2] = 0.0;
    params.kv[0] = 0.0;
    params.kv[1] = 0.0;
    params.kv[2] = 0.0;
    params.smc_lambda[0] = 2.0;
    params.smc_eta[0] = 0.6;
    params.smc_phi[0] = 0.4;
    params.hover_percentage = 0.294;
    params.tilt_limit_rad = 1.2;
    CoreState state;
    mosim_px4ctrl::reset_thrust_mapping(params, state);

    auto in = base_input();
    in.position = Vec3{-0.05, 0.0, 1.0};
    const ControllerOutput small = mosim_px4ctrl::calculate_smc_boundary_layer_core(params, state, in);
    stats.surface_x = small.sliding_surface.x;
    stats.boundary_layer_acc_delta_x = small.desired_acceleration.x;
    if (std::fabs(stats.surface_x - 0.1) > 1.0e-12 ||
        std::fabs(stats.boundary_layer_acc_delta_x - 0.15) > 1.0e-12)
    {
        fail(stats, "linear_boundary_layer", "inside boundary layer, switching acceleration must scale with s / phi");
    }

    in.position = Vec3{-1.0, 0.0, 1.0};
    const ControllerOutput large = mosim_px4ctrl::calculate_smc_boundary_layer_core(params, state, in);
    stats.eta_saturated_acc_delta_x = large.desired_acceleration.x;
    if (std::fabs(stats.eta_saturated_acc_delta_x - params.smc_eta[0]) > 1.0e-12)
    {
        fail(stats, "saturated_boundary_layer", "outside boundary layer, switching acceleration must saturate at eta");
    }
}

void run_yaw_limit_and_disabled_cases(GateStats &stats)
{
    CoreParams params;
    params.hover_percentage = 0.294;
    params.min_normalized_thrust = 0.0;
    params.max_normalized_thrust = 0.45;
    params.tilt_limit_rad = 0.20;
    params.kp[0] = 20.0;
    params.smc_eta[0] = 1.0;
    CoreState state;
    mosim_px4ctrl::reset_thrust_mapping(params, state);

    auto in = base_input();
    in.reference_yaw = 0.8;
    const ControllerOutput yaw_out = mosim_px4ctrl::calculate_smc_boundary_layer_core(params, state, in);
    stats.yaw_error_rad = std::fabs(mosim_px4ctrl::yaw_from_quat(yaw_out.desired_attitude) - 0.8);
    if (stats.yaw_error_rad > 1.0e-9)
    {
        fail(stats, "yaw_preserved", "level SMC boundary-layer attitude did not preserve reference yaw");
    }

    in = base_input();
    in.position = Vec3{-5.0, 0.0, 1.0};
    const ControllerOutput limited = mosim_px4ctrl::calculate_smc_boundary_layer_core(params, state, in);
    const Vec3 b3 = b3_from_quat(limited.desired_attitude);
    stats.tilt_limited_b3_z = b3.z;
    if (!limited.saturated ||
        limited.normalized_thrust > params.max_normalized_thrust + kTol ||
        stats.tilt_limited_b3_z < std::cos(params.tilt_limit_rad) - 1.0e-6)
    {
        fail(stats, "limits_enforced", "SMC boundary-layer thrust or tilt limits were not enforced cleanly");
    }

    in.enable = false;
    const ControllerOutput disabled = mosim_px4ctrl::calculate_smc_boundary_layer_core(params, state, in);
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
    run_boundary_layer_case(stats);
    run_yaw_limit_and_disabled_cases(stats);

    std::cout << std::setprecision(17);
    std::cout << "{\n";
    std::cout << "  \"schema\": \"mosim.g9d_smc_boundary_layer_static_gate.v1\",\n";
    std::cout << "  \"status\": \"" << (stats.failures == 0 ? "passed" : "failed") << "\",\n";
    std::cout << "  \"claim_boundary\": \"Static smc_boundary_layer ATTITUDE_THRUST backend gate only. No terminal, super-twisting, attitude-loop, torque-level, ROS, Gazebo, PX4, MAVROS, RViz, UE, or MWORKS runtime is executed.\",\n";
    std::cout << "  \"failure_count\": " << stats.failures << ",\n";
    std::cout << "  \"hover_thrust_error\": " << stats.hover_thrust_error << ",\n";
    std::cout << "  \"hover_quat_error\": " << stats.hover_quat_error << ",\n";
    std::cout << "  \"surface_x\": " << stats.surface_x << ",\n";
    std::cout << "  \"boundary_layer_acc_delta_x\": " << stats.boundary_layer_acc_delta_x << ",\n";
    std::cout << "  \"eta_saturated_acc_delta_x\": " << stats.eta_saturated_acc_delta_x << ",\n";
    std::cout << "  \"yaw_error_rad\": " << stats.yaw_error_rad << ",\n";
    std::cout << "  \"tilt_limited_b3_z\": " << stats.tilt_limited_b3_z << "\n";
    std::cout << "}\n";

    return stats.failures == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
