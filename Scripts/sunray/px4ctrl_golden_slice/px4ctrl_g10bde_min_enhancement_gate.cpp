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
    double hover_max_thrust_error{0.0};
    double l1_compensation_x{0.0};
    double l1_clamped_accel_x{0.0};
    double awff_drag_accel_x{0.0};
    double safety_passthrough_max_error{0.0};
    double safety_clamped_accel_x{0.0};
    double safety_rejected_accel_x{0.0};
    double fault_hover_thrust{0.0};
    double fault_missing_authority{0.0};
    double fault_multiplier_delta{0.0};
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

CoreParams base_params()
{
    CoreParams params;
    params.hover_percentage = 0.294;
    params.max_normalized_thrust = 2.0;
    params.tilt_limit_rad = 1.2;
    return params;
}

void update_hover_error(GateStats &stats, const ControllerOutput &out, const CoreParams &params)
{
    stats.hover_max_thrust_error = std::max(
        stats.hover_max_thrust_error,
        std::fabs(out.normalized_thrust - params.hover_percentage));
}

void run_hover_identity_cases(GateStats &stats)
{
    CoreParams params = base_params();
    CoreState l1_state;
    CoreState safety_state;
    CoreState fault_state;
    mosim_px4ctrl::reset_thrust_mapping(params, l1_state);
    mosim_px4ctrl::reset_thrust_mapping(params, safety_state);
    mosim_px4ctrl::reset_thrust_mapping(params, fault_state);

    const ControllerInput in = base_input();
    const ControllerOutput l1 = mosim_px4ctrl::calculate_l1_awff_core(params, l1_state, in);
    const ControllerOutput safety = mosim_px4ctrl::calculate_safety_filter_core(params, safety_state, in);
    const ControllerOutput fault = mosim_px4ctrl::calculate_fault_allocation_core(params, fault_state, in);
    update_hover_error(stats, l1, params);
    update_hover_error(stats, safety, params);
    update_hover_error(stats, fault, params);
    if (stats.hover_max_thrust_error > 1.0e-12 ||
        quat_min_norm(l1.desired_attitude, Quat{}) > 1.0e-12 ||
        quat_min_norm(safety.desired_attitude, Quat{}) > 1.0e-12 ||
        quat_min_norm(fault.desired_attitude, Quat{}) > 1.0e-12 ||
        l1.saturated || safety.saturated || fault.saturated)
    {
        fail(stats, "hover_identity", "G10 B/D/E routes must be neutral and unsaturated at nominal hover");
    }
}

void run_l1_awff_cases(GateStats &stats)
{
    CoreParams params = base_params();
    params.kp[0] = 0.0;
    params.kv[0] = 0.0;
    params.l1_model_decay = 0.0;
    params.l1_filter_T = 0.0;
    params.l1_gain[0] = 1.0;
    params.l1_comp_limit[0] = 0.35;
    params.indi_measured_accel_limit[0] = 20.0;
    CoreState state;
    mosim_px4ctrl::reset_thrust_mapping(params, state);

    auto in = base_input();
    in.dt = 1.0;
    in.reference_acceleration = Vec3{1.0, 0.0, 0.0};
    (void)mosim_px4ctrl::calculate_l1_awff_core(params, state, in);
    const ControllerOutput l1 = mosim_px4ctrl::calculate_l1_awff_core(params, state, in);
    stats.l1_compensation_x = l1.disturbance_estimate.x;
    stats.l1_clamped_accel_x = l1.desired_acceleration.x;
    if (std::fabs(stats.l1_compensation_x - 0.35) > kTol ||
        std::fabs(stats.l1_clamped_accel_x - 1.35) > kTol)
    {
        fail(stats, "l1_bounded_compensation", "L1-inspired residual compensation must be low-pass/update bounded and clamp at the configured limit");
    }

    CoreParams awff_params = base_params();
    awff_params.kp[0] = 0.0;
    awff_params.kv[0] = 0.0;
    awff_params.drag_feedforward_gain[0] = 0.2;
    CoreState awff_state;
    mosim_px4ctrl::reset_thrust_mapping(awff_params, awff_state);

    auto awff_in = base_input();
    awff_in.reference_velocity = Vec3{2.0, 0.0, 0.0};
    const ControllerOutput awff = mosim_px4ctrl::calculate_l1_awff_core(awff_params, awff_state, awff_in);
    stats.awff_drag_accel_x = awff.desired_acceleration.x;
    if (std::fabs(stats.awff_drag_accel_x + 0.4) > kTol)
    {
        fail(stats, "awff_drag_feedforward", "AWFF drag feedforward must apply the configured bounded model term");
    }
}

void run_safety_filter_case(GateStats &stats)
{
    {
        CoreParams params = base_params();
        params.kp[0] = 2.0;
        params.kp[1] = 1.5;
        params.kp[2] = 3.0;
        params.kv[0] = 0.3;
        params.kv[1] = 0.2;
        params.kv[2] = 0.4;
        params.ki[0] = 0.1;
        params.ki[1] = 0.1;
        params.ki[2] = 0.1;
        params.safety_accel_limit[0] = 50.0;
        params.safety_accel_limit[1] = 50.0;
        params.safety_accel_limit[2] = 50.0;

        CoreState pid_state;
        CoreState safety_state;
        mosim_px4ctrl::reset_thrust_mapping(params, pid_state);
        mosim_px4ctrl::reset_thrust_mapping(params, safety_state);

        auto in = base_input();
        in.position = Vec3{0.1, -0.2, 0.9};
        in.velocity = Vec3{0.04, -0.03, 0.02};
        in.reference_position = Vec3{0.2, -0.1, 1.1};
        in.reference_velocity = Vec3{0.01, 0.02, -0.01};
        in.reference_acceleration = Vec3{0.3, -0.2, 0.1};
        in.reference_yaw = 0.15;

        const ControllerOutput pid = mosim_px4ctrl::calculate_official_pid_core(params, pid_state, in);
        const ControllerOutput safety = mosim_px4ctrl::calculate_safety_filter_core(params, safety_state, in);
        stats.safety_passthrough_max_error = std::max({
            std::fabs(pid.desired_acceleration.x - safety.desired_acceleration.x),
            std::fabs(pid.desired_acceleration.y - safety.desired_acceleration.y),
            std::fabs(pid.desired_acceleration.z - safety.desired_acceleration.z),
            std::fabs(pid.normalized_thrust - safety.normalized_thrust),
            quat_min_norm(pid.desired_attitude, safety.desired_attitude),
        });
        if (safety.saturated ||
            safety.status_code != 0 ||
            stats.safety_passthrough_max_error > 1.0e-12)
        {
            fail(stats, "safety_passthrough_equivalence", "Safety filter must exactly match official PID when the configured limits are inactive");
        }
    }

    CoreParams params = base_params();
    params.kp[0] = 10.0;
    params.kv[0] = 0.0;
    params.safety_accel_limit[0] = 2.0;
    CoreState state;
    mosim_px4ctrl::reset_thrust_mapping(params, state);

    auto in = base_input();
    in.reference_position = Vec3{1.0, 0.0, 1.0};
    const ControllerOutput out = mosim_px4ctrl::calculate_safety_filter_core(params, state, in);
    stats.safety_clamped_accel_x = out.desired_acceleration.x;
    stats.safety_rejected_accel_x = out.sliding_surface.x;
    if (!out.saturated ||
        out.status_code != 2 ||
        std::fabs(stats.safety_clamped_accel_x - 2.0) > kTol ||
        std::fabs(stats.safety_rejected_accel_x - 8.0) > kTol)
    {
        fail(stats, "safety_filter_clamp", "Safety filter must clamp candidate acceleration and expose the rejected command delta");
    }
}

void run_fault_allocation_case(GateStats &stats)
{
    CoreParams params = base_params();
    params.fault_rotor_efficiency[0] = 0.5;
    params.fault_rotor_efficiency[1] = 1.0;
    params.fault_rotor_efficiency[2] = 1.0;
    params.fault_rotor_efficiency[3] = 1.0;
    params.fault_allocation_blend = 0.52;
    params.fault_min_efficiency = 0.5;
    params.fault_thrust_comp_limit = 0.25;
    CoreState state;
    mosim_px4ctrl::reset_thrust_mapping(params, state);

    const ControllerOutput out = mosim_px4ctrl::calculate_fault_allocation_core(params, state, base_input());
    stats.fault_hover_thrust = out.normalized_thrust;
    stats.fault_missing_authority = out.disturbance_estimate.x;
    stats.fault_multiplier_delta = out.disturbance_estimate.z;
    const double expected_missing = 0.125;
    const double expected_delta = 0.065;
    const double expected_thrust = params.hover_percentage * (1.0 + expected_delta);
    if (!out.saturated ||
        out.status_code != 3 ||
        std::fabs(stats.fault_missing_authority - expected_missing) > kTol ||
        std::fabs(stats.fault_multiplier_delta - expected_delta) > kTol ||
        std::fabs(stats.fault_hover_thrust - expected_thrust) > kTol)
    {
        fail(stats, "fault_allocation_degraded_thrust", "Fault allocation profile must expose bounded ATTITUDE_THRUST degradation compensation without claiming motor-level allocation");
    }
}

} // namespace

int main()
{
    GateStats stats;

    run_hover_identity_cases(stats);
    run_l1_awff_cases(stats);
    run_safety_filter_case(stats);
    run_fault_allocation_case(stats);

    std::cout << std::setprecision(17);
    std::cout << "{\n";
    std::cout << "  \"schema\": \"mosim.g10bde_min_enhancement_static_gate.v1\",\n";
    std::cout << "  \"status\": \"" << (stats.failures == 0 ? "passed" : "failed") << "\",\n";
    std::cout << "  \"claim_boundary\": \"Static G10-B/D/E minimal enhancement gate only. It proves neutral hover behavior, bounded L1/AWFF compensation, acceleration safety filtering, and ATTITUDE_THRUST-level degraded thrust compensation. It does not prove Gazebo runtime improvement, MWORKS code generation, PX4-native deployment, motor-level control allocation, or autonomous fault recovery.\",\n";
    std::cout << "  \"failure_count\": " << stats.failures << ",\n";
    std::cout << "  \"hover_max_thrust_error\": " << stats.hover_max_thrust_error << ",\n";
    std::cout << "  \"l1_compensation_x\": " << stats.l1_compensation_x << ",\n";
    std::cout << "  \"l1_clamped_accel_x\": " << stats.l1_clamped_accel_x << ",\n";
    std::cout << "  \"awff_drag_accel_x\": " << stats.awff_drag_accel_x << ",\n";
    std::cout << "  \"safety_passthrough_max_error\": " << stats.safety_passthrough_max_error << ",\n";
    std::cout << "  \"safety_clamped_accel_x\": " << stats.safety_clamped_accel_x << ",\n";
    std::cout << "  \"safety_rejected_accel_x\": " << stats.safety_rejected_accel_x << ",\n";
    std::cout << "  \"fault_hover_thrust\": " << stats.fault_hover_thrust << ",\n";
    std::cout << "  \"fault_missing_authority\": " << stats.fault_missing_authority << ",\n";
    std::cout << "  \"fault_multiplier_delta\": " << stats.fault_multiplier_delta << "\n";
    std::cout << "}\n";

    return stats.failures == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
