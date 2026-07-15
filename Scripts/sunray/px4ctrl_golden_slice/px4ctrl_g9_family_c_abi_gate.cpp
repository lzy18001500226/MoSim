#include "px4ctrl_core.h"

extern "C" {
#include "px4ctrl_g9_family_core_c.h"
}

#include <algorithm>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>

using mosim_px4ctrl::ControllerInput;
using mosim_px4ctrl::ControllerOutput;
using mosim_px4ctrl::CoreParams;
using mosim_px4ctrl::CoreState;
using mosim_px4ctrl::Quat;
using mosim_px4ctrl::Vec3;

namespace
{

struct Case
{
    std::string name;
    int controller_id;
    ControllerInput input;
};

struct DiffStats
{
    int failures{0};
    int case_count{0};
    double max_quat_min_norm{0.0};
    double max_quat_angle_rad{0.0};
    double max_normalized_thrust{0.0};
    double max_collective_thrust_n{0.0};
    double max_position_error{0.0};
    double max_velocity_error{0.0};
    double max_sliding_surface{0.0};
    double max_desired_acceleration{0.0};
    double max_desired_body_rate{0.0};
    double max_desired_body_acceleration{0.0};
    double max_disturbance_estimate{0.0};
    double max_desired_force_n{0.0};
    double max_saturated{0.0};
    double max_status_code{0.0};
};

Quat quat_from_rpy(double roll, double pitch, double yaw)
{
    return mosim_px4ctrl::multiply(
        mosim_px4ctrl::multiply(
            mosim_px4ctrl::angle_axis(yaw, Vec3{0.0, 0.0, 1.0}),
            mosim_px4ctrl::angle_axis(pitch, Vec3{0.0, 1.0, 0.0})),
        mosim_px4ctrl::angle_axis(roll, Vec3{1.0, 0.0, 0.0}));
}

double absmax3(const Vec3 &v)
{
    return std::max(std::max(std::fabs(v.x), std::fabs(v.y)), std::fabs(v.z));
}

Vec3 diff3(const Vec3 &a, const Vec3 &b)
{
    return Vec3{a.x - b.x, a.y - b.y, a.z - b.z};
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

double quat_angle_error_rad(const Quat &a_raw, const Quat &b_raw)
{
    const Quat a = mosim_px4ctrl::normalize(a_raw);
    const Quat b = mosim_px4ctrl::normalize(b_raw);
    double dot = std::fabs(a.w * b.w + a.x * b.x + a.y * b.y + a.z * b.z);
    dot = std::max(-1.0, std::min(1.0, dot));
    return 2.0 * std::acos(dot);
}

ControllerInput base_input()
{
    ControllerInput in;
    in.dt = 0.01;
    in.position = Vec3{0.0, 0.0, 1.0};
    in.velocity = Vec3{0.0, 0.0, 0.0};
    in.attitude = quat_from_rpy(0.0, 0.0, 0.0);
    in.imu_attitude = in.attitude;
    in.reference_position = Vec3{0.0, 0.0, 1.0};
    in.reference_velocity = Vec3{0.0, 0.0, 0.0};
    in.reference_acceleration = Vec3{0.0, 0.0, 0.0};
    in.reference_yaw = 0.0;
    in.enable = true;
    in.enable_disturbance_observer = true;
    return in;
}

std::vector<Case> build_cases()
{
    std::vector<Case> cases;
    const int controller_ids[] = {
        MOSIM_PX4CTRL_G9_OFFICIAL_PID,
        MOSIM_PX4CTRL_G9_SE3_BASIC,
        MOSIM_PX4CTRL_G9_DFBC_BASIC,
        MOSIM_PX4CTRL_G9_SMC_BOUNDARY_LAYER,
        MOSIM_PX4CTRL_G9_PID_INDI,
        MOSIM_PX4CTRL_G9_NMPC_OUTER,
        MOSIM_PX4CTRL_G10_L1_AWFF,
        MOSIM_PX4CTRL_G10_SAFETY_FILTER,
        MOSIM_PX4CTRL_G10_FAULT_ALLOCATION,
    };
    const char *controller_names[] = {
        "official_pid",
        "se3_basic",
        "dfbc_basic",
        "smc_boundary_layer",
        "pid_indi",
        "nmpc_outer",
        "l1_awff",
        "safety_filter",
        "fault_allocation",
    };

    for (int c = 0; c < 9; ++c)
    {
        {
            auto in = base_input();
            in.reset = true;
            cases.push_back({std::string(controller_names[c]) + "_reset_hover", controller_ids[c], in});
        }
        for (int i = 0; i < 72; ++i)
        {
            const double theta = i * 2.0 * M_PI / 72.0;
            auto in = base_input();
            in.position = Vec3{
                0.7 * std::sin(theta - 0.07),
                0.35 * std::sin(2.0 * (theta - 0.04)),
                1.0 + 0.04 * std::sin(theta)};
            in.velocity = Vec3{
                0.7 * std::cos(theta - 0.07),
                0.70 * std::cos(2.0 * (theta - 0.04)),
                0.04 * std::cos(theta)};
            in.reference_position = Vec3{
                0.7 * std::sin(theta),
                0.35 * std::sin(2.0 * theta),
                1.0 + 0.02 * std::sin(0.5 * theta)};
            in.reference_velocity = Vec3{
                0.7 * std::cos(theta),
                0.70 * std::cos(2.0 * theta),
                0.01 * std::cos(0.5 * theta)};
            in.reference_acceleration = Vec3{
                -0.7 * std::sin(theta),
                -1.4 * std::sin(2.0 * theta),
                -0.005 * std::sin(0.5 * theta)};
            in.reference_yaw = 0.25 * std::sin(0.5 * theta);
            in.reference_yaw_rate = 0.02 * std::cos(theta);
            in.reference_yaw_acceleration = -0.02 * std::sin(theta);
            in.reference_jerk = Vec3{
                -0.2 * std::cos(theta),
                -0.3 * std::cos(2.0 * theta),
                0.01 * std::sin(theta)};
            in.reference_snap = Vec3{
                0.2 * std::sin(theta),
                0.6 * std::sin(2.0 * theta),
                0.01 * std::cos(theta)};
            in.attitude = quat_from_rpy(
                0.03 * std::sin(2.0 * theta),
                -0.02 * std::cos(theta),
                0.18 * std::sin(0.5 * theta));
            in.imu_attitude = in.attitude;
            in.measurement_stamp_valid = true;
            in.measurement_stamp_s = i * 0.01;
            cases.push_back({std::string(controller_names[c]) + "_figure8_" + std::to_string(i), controller_ids[c], in});
        }
        {
            auto in = base_input();
            in.position = Vec3{-3.0, 0.0, 0.0};
            in.reference_position = Vec3{0.0, 0.0, 2.2};
            cases.push_back({std::string(controller_names[c]) + "_limit_sample", controller_ids[c], in});
        }
        {
            auto in = base_input();
            in.enable = false;
            cases.push_back({std::string(controller_names[c]) + "_disabled", controller_ids[c], in});
        }
    }
    {
        auto in = base_input();
        in.reset = true;
        cases.push_back({"l1_awff_measurement_reset", MOSIM_PX4CTRL_G10_L1_AWFF, in});
        for (int i = 1; i <= 24; ++i)
        {
            auto seq = base_input();
            const double t = 0.01 * i;
            seq.measurement_stamp_valid = true;
            seq.measurement_stamp_s = t;
            seq.position = Vec3{0.04 * std::sin(2.0 * t), -0.03 * std::cos(3.0 * t), 1.0 + 0.01 * std::sin(t)};
            seq.velocity = Vec3{0.35 + 0.02 * i, -0.15 + 0.01 * i, 0.04 * std::sin(0.5 * t)};
            seq.reference_velocity = Vec3{0.20, -0.10, 0.02};
            seq.reference_acceleration = Vec3{0.05, -0.02, 0.01};
            cases.push_back({"l1_awff_measurement_" + std::to_string(i), MOSIM_PX4CTRL_G10_L1_AWFF, seq});
        }
    }
    {
        auto in = base_input();
        in.position = Vec3{-4.0, 3.0, -1.5};
        in.reference_position = Vec3{0.4, -0.2, 2.0};
        cases.push_back({"safety_filter_explicit_clamp", MOSIM_PX4CTRL_G10_SAFETY_FILTER, in});
    }
    {
        auto in = base_input();
        in.reference_position = Vec3{0.2, -0.1, 1.2};
        cases.push_back({"fault_allocation_degraded_hover", MOSIM_PX4CTRL_G10_FAULT_ALLOCATION, in});
    }
    return cases;
}

MosimPx4ctrlG9FamilyCVec3 to_c_vec3(const Vec3 &v)
{
    return MosimPx4ctrlG9FamilyCVec3{v.x, v.y, v.z};
}

MosimPx4ctrlG9FamilyCQuat to_c_quat(const Quat &q)
{
    return MosimPx4ctrlG9FamilyCQuat{q.w, q.x, q.y, q.z};
}

MosimPx4ctrlG9FamilyCParams to_c_params(const CoreParams &params)
{
    MosimPx4ctrlG9FamilyCParams out{};
    for (int i = 0; i < 3; ++i)
    {
        out.kp[i] = params.kp[i];
        out.kv[i] = params.kv[i];
        out.ki[i] = params.ki[i];
        out.smc_lambda[i] = params.smc_lambda[i];
        out.smc_eta[i] = params.smc_eta[i];
        out.smc_phi[i] = params.smc_phi[i];
        out.smc_surface_limit[i] = params.smc_surface_limit[i];
        out.indi_gain[i] = params.indi_gain[i];
        out.indi_increment_limit[i] = params.indi_increment_limit[i];
        out.indi_measured_accel_limit[i] = params.indi_measured_accel_limit[i];
        out.nmpc_position_weight[i] = params.nmpc_position_weight[i];
        out.nmpc_velocity_weight[i] = params.nmpc_velocity_weight[i];
        out.nmpc_control_weight[i] = params.nmpc_control_weight[i];
        out.nmpc_accel_limit[i] = params.nmpc_accel_limit[i];
        out.nmpc_increment_limit[i] = params.nmpc_increment_limit[i];
        out.l1_gain[i] = params.l1_gain[i];
        out.l1_comp_limit[i] = params.l1_comp_limit[i];
        out.drag_feedforward_gain[i] = params.drag_feedforward_gain[i];
        out.safety_accel_limit[i] = params.safety_accel_limit[i];
        out.integral_limit[i] = params.integral_limit[i];
    }
    for (int i = 0; i < 4; ++i)
    {
        out.fault_rotor_efficiency[i] = params.fault_rotor_efficiency[i];
    }
    out.indi_accel_lpf_alpha = params.indi_accel_lpf_alpha;
    out.nmpc_horizon_s = params.nmpc_horizon_s;
    out.l1_model_decay = params.l1_model_decay;
    out.l1_filter_T = params.l1_filter_T;
    out.fault_allocation_blend = params.fault_allocation_blend;
    out.fault_min_efficiency = params.fault_min_efficiency;
    out.fault_thrust_comp_limit = params.fault_thrust_comp_limit;
    out.mass = params.mass;
    out.gravity = params.gravity;
    out.hover_percentage = params.hover_percentage;
    out.min_normalized_thrust = params.min_normalized_thrust;
    out.max_normalized_thrust = params.max_normalized_thrust;
    out.tilt_limit_rad = params.tilt_limit_rad;
    return out;
}

MosimPx4ctrlG9FamilyCInput to_c_input(const ControllerInput &input, int controller_id)
{
    MosimPx4ctrlG9FamilyCInput out{};
    out.controller_id = controller_id;
    out.dt = input.dt;
    out.position = to_c_vec3(input.position);
    out.velocity = to_c_vec3(input.velocity);
    out.attitude = to_c_quat(input.attitude);
    out.angular_velocity = to_c_vec3(input.angular_velocity);
    out.reference_position = to_c_vec3(input.reference_position);
    out.reference_velocity = to_c_vec3(input.reference_velocity);
    out.reference_acceleration = to_c_vec3(input.reference_acceleration);
    out.reference_jerk = to_c_vec3(input.reference_jerk);
    out.reference_snap = to_c_vec3(input.reference_snap);
    out.reference_yaw = input.reference_yaw;
    out.reference_yaw_rate = input.reference_yaw_rate;
    out.reference_yaw_acceleration = input.reference_yaw_acceleration;
    out.measurement_stamp_s = input.measurement_stamp_s;
    out.imu_attitude = to_c_quat(input.imu_attitude);
    out.imu_angular_velocity = to_c_vec3(input.imu_angular_velocity);
    out.enable = input.enable;
    out.reset = input.reset;
    out.measurement_stamp_valid = input.measurement_stamp_valid;
    out.enable_disturbance_observer = input.enable_disturbance_observer;
    return out;
}

ControllerOutput from_c_output(const MosimPx4ctrlG9FamilyCOutput &input)
{
    ControllerOutput out;
    out.desired_attitude = Quat{
        input.desired_attitude.w,
        input.desired_attitude.x,
        input.desired_attitude.y,
        input.desired_attitude.z};
    out.normalized_thrust = input.normalized_thrust;
    out.collective_thrust_n = input.collective_thrust_n;
    out.position_error = Vec3{input.position_error.x, input.position_error.y, input.position_error.z};
    out.velocity_error = Vec3{input.velocity_error.x, input.velocity_error.y, input.velocity_error.z};
    out.sliding_surface = Vec3{input.sliding_surface.x, input.sliding_surface.y, input.sliding_surface.z};
    out.desired_acceleration = Vec3{input.desired_acceleration.x, input.desired_acceleration.y, input.desired_acceleration.z};
    out.desired_body_rate = Vec3{input.desired_body_rate.x, input.desired_body_rate.y, input.desired_body_rate.z};
    out.desired_body_acceleration = Vec3{input.desired_body_acceleration.x, input.desired_body_acceleration.y, input.desired_body_acceleration.z};
    out.disturbance_estimate = Vec3{input.disturbance_estimate.x, input.disturbance_estimate.y, input.disturbance_estimate.z};
    out.desired_force_n = Vec3{input.desired_force_n.x, input.desired_force_n.y, input.desired_force_n.z};
    out.saturated = input.saturated != 0.0;
    out.status_code = input.status_code;
    return out;
}

ControllerOutput run_cpp_core(
    int controller_id,
    const CoreParams &params,
    CoreState &state,
    const ControllerInput &input)
{
    switch (controller_id)
    {
    case MOSIM_PX4CTRL_G9_OFFICIAL_PID:
        return mosim_px4ctrl::calculate_official_pid_core(params, state, input);
    case MOSIM_PX4CTRL_G9_SE3_BASIC:
        return mosim_px4ctrl::calculate_se3_basic_core(params, state, input);
    case MOSIM_PX4CTRL_G9_DFBC_BASIC:
        return mosim_px4ctrl::calculate_dfbc_basic_core(params, state, input);
    case MOSIM_PX4CTRL_G9_SMC_BOUNDARY_LAYER:
        return mosim_px4ctrl::calculate_smc_boundary_layer_core(params, state, input);
    case MOSIM_PX4CTRL_G9_PID_INDI:
        return mosim_px4ctrl::calculate_pid_indi_bounded_core(params, state, input);
    case MOSIM_PX4CTRL_G9_NMPC_OUTER:
        return mosim_px4ctrl::calculate_nmpc_outer_core(params, state, input);
    case MOSIM_PX4CTRL_G10_L1_AWFF:
        return mosim_px4ctrl::calculate_l1_awff_core(params, state, input);
    case MOSIM_PX4CTRL_G10_SAFETY_FILTER:
        return mosim_px4ctrl::calculate_safety_filter_core(params, state, input);
    case MOSIM_PX4CTRL_G10_FAULT_ALLOCATION:
        return mosim_px4ctrl::calculate_fault_allocation_core(params, state, input);
    default:
        return ControllerOutput{};
    }
}

void update_stats(DiffStats &stats, const ControllerOutput &ref, const ControllerOutput &core)
{
    stats.max_quat_min_norm = std::max(stats.max_quat_min_norm, quat_min_norm(ref.desired_attitude, core.desired_attitude));
    stats.max_quat_angle_rad = std::max(stats.max_quat_angle_rad, quat_angle_error_rad(ref.desired_attitude, core.desired_attitude));
    stats.max_normalized_thrust = std::max(stats.max_normalized_thrust, std::fabs(ref.normalized_thrust - core.normalized_thrust));
    stats.max_collective_thrust_n = std::max(stats.max_collective_thrust_n, std::fabs(ref.collective_thrust_n - core.collective_thrust_n));
    stats.max_position_error = std::max(stats.max_position_error, absmax3(diff3(ref.position_error, core.position_error)));
    stats.max_velocity_error = std::max(stats.max_velocity_error, absmax3(diff3(ref.velocity_error, core.velocity_error)));
    stats.max_sliding_surface = std::max(stats.max_sliding_surface, absmax3(diff3(ref.sliding_surface, core.sliding_surface)));
    stats.max_desired_acceleration = std::max(stats.max_desired_acceleration, absmax3(diff3(ref.desired_acceleration, core.desired_acceleration)));
    stats.max_desired_body_rate = std::max(stats.max_desired_body_rate, absmax3(diff3(ref.desired_body_rate, core.desired_body_rate)));
    stats.max_desired_body_acceleration = std::max(stats.max_desired_body_acceleration, absmax3(diff3(ref.desired_body_acceleration, core.desired_body_acceleration)));
    stats.max_disturbance_estimate = std::max(stats.max_disturbance_estimate, absmax3(diff3(ref.disturbance_estimate, core.disturbance_estimate)));
    stats.max_desired_force_n = std::max(stats.max_desired_force_n, absmax3(diff3(ref.desired_force_n, core.desired_force_n)));
    stats.max_saturated = std::max(stats.max_saturated, std::fabs(static_cast<double>(ref.saturated) - static_cast<double>(core.saturated)));
    stats.max_status_code = std::max(stats.max_status_code, std::fabs(static_cast<double>(ref.status_code - core.status_code)));
}

bool failed_case(const ControllerOutput &cpp, const ControllerOutput &c, double tol)
{
    return quat_min_norm(cpp.desired_attitude, c.desired_attitude) > tol ||
        quat_angle_error_rad(cpp.desired_attitude, c.desired_attitude) > tol ||
        std::fabs(cpp.normalized_thrust - c.normalized_thrust) > tol ||
        std::fabs(cpp.collective_thrust_n - c.collective_thrust_n) > tol ||
        absmax3(diff3(cpp.position_error, c.position_error)) > tol ||
        absmax3(diff3(cpp.velocity_error, c.velocity_error)) > tol ||
        absmax3(diff3(cpp.sliding_surface, c.sliding_surface)) > tol ||
        absmax3(diff3(cpp.desired_acceleration, c.desired_acceleration)) > tol ||
        absmax3(diff3(cpp.desired_body_rate, c.desired_body_rate)) > tol ||
        absmax3(diff3(cpp.desired_body_acceleration, c.desired_body_acceleration)) > tol ||
        absmax3(diff3(cpp.disturbance_estimate, c.disturbance_estimate)) > tol ||
        absmax3(diff3(cpp.desired_force_n, c.desired_force_n)) > tol ||
        cpp.saturated != c.saturated ||
        cpp.status_code != c.status_code;
}

} // namespace

int main()
{
    const double tol = 1.0e-12;
    CoreParams params;
    params.kp[0] = 1.2;
    params.kp[1] = 1.3;
    params.kp[2] = 1.4;
    params.kv[0] = 0.8;
    params.kv[1] = 0.9;
    params.kv[2] = 1.0;
    params.ki[0] = 0.05;
    params.ki[1] = 0.04;
    params.ki[2] = 0.12;
    params.smc_lambda[0] = 2.0;
    params.smc_lambda[1] = 2.1;
    params.smc_lambda[2] = 1.8;
    params.smc_eta[0] = 0.6;
    params.smc_eta[1] = 0.5;
    params.smc_eta[2] = 0.4;
    params.smc_phi[0] = 0.4;
    params.smc_phi[1] = 0.35;
    params.smc_phi[2] = 0.3;
    params.smc_surface_limit[0] = 3.0;
    params.smc_surface_limit[1] = 3.0;
    params.smc_surface_limit[2] = 2.5;
    params.indi_gain[0] = 0.12;
    params.indi_gain[1] = 0.11;
    params.indi_gain[2] = 0.08;
    params.indi_increment_limit[0] = 0.35;
    params.indi_increment_limit[1] = 0.34;
    params.indi_increment_limit[2] = 0.20;
    params.indi_measured_accel_limit[0] = 6.0;
    params.indi_measured_accel_limit[1] = 6.0;
    params.indi_measured_accel_limit[2] = 4.0;
    params.indi_accel_lpf_alpha = 0.35;
    params.nmpc_horizon_s = 0.35;
    params.nmpc_position_weight[0] = 1.0;
    params.nmpc_position_weight[1] = 1.1;
    params.nmpc_position_weight[2] = 1.2;
    params.nmpc_velocity_weight[0] = 0.05;
    params.nmpc_velocity_weight[1] = 0.06;
    params.nmpc_velocity_weight[2] = 0.07;
    params.nmpc_control_weight[0] = 0.001;
    params.nmpc_control_weight[1] = 0.0012;
    params.nmpc_control_weight[2] = 0.0015;
    params.nmpc_accel_limit[0] = 4.0;
    params.nmpc_accel_limit[1] = 4.0;
    params.nmpc_accel_limit[2] = 2.5;
    params.nmpc_increment_limit[0] = 4.0;
    params.nmpc_increment_limit[1] = 3.5;
    params.nmpc_increment_limit[2] = 2.5;
    params.l1_model_decay = 1.15;
    params.l1_filter_T = 0.18;
    params.l1_gain[0] = 0.31;
    params.l1_gain[1] = 0.33;
    params.l1_gain[2] = 0.36;
    params.l1_comp_limit[0] = 1.8;
    params.l1_comp_limit[1] = 1.9;
    params.l1_comp_limit[2] = 2.0;
    params.drag_feedforward_gain[0] = 0.08;
    params.drag_feedforward_gain[1] = 0.05;
    params.drag_feedforward_gain[2] = 0.02;
    params.safety_accel_limit[0] = 1.6;
    params.safety_accel_limit[1] = 1.5;
    params.safety_accel_limit[2] = 1.2;
    params.fault_rotor_efficiency[0] = 1.0;
    params.fault_rotor_efficiency[1] = 0.70;
    params.fault_rotor_efficiency[2] = 0.92;
    params.fault_rotor_efficiency[3] = 0.85;
    params.fault_allocation_blend = 0.52;
    params.fault_min_efficiency = 0.50;
    params.fault_thrust_comp_limit = 0.25;
    params.integral_limit[0] = 0.5;
    params.integral_limit[1] = 0.5;
    params.integral_limit[2] = 0.3;
    params.mass = 0.67;
    params.gravity = 9.8;
    params.hover_percentage = 0.294;
    params.min_normalized_thrust = 0.0;
    params.max_normalized_thrust = 0.62;
    params.tilt_limit_rad = 0.35;

    const MosimPx4ctrlG9FamilyCParams c_params = to_c_params(params);
    CoreState cpp_states[10];
    MosimPx4ctrlG9FamilyCState c_states[10]{};
    for (int i = 0; i < 10; ++i)
    {
        mosim_px4ctrl::reset_thrust_mapping(params, cpp_states[i]);
        mosim_px4ctrl_g9_family_c_reset(&c_params, &c_states[i]);
    }

    const auto cases = build_cases();
    DiffStats stats;

    for (const auto &c : cases)
    {
        MosimPx4ctrlG9FamilyCOutput c_output{};
        const ControllerOutput cpp = run_cpp_core(
            c.controller_id,
            params,
            cpp_states[c.controller_id],
            c.input);
        MosimPx4ctrlG9FamilyCInput c_input = to_c_input(c.input, c.controller_id);
        mosim_px4ctrl_g9_family_c_step(
            &c_params,
            &c_states[c.controller_id],
            &c_input,
            &c_output);
        const ControllerOutput c_as_cpp = from_c_output(c_output);

        ++stats.case_count;
        update_stats(stats, cpp, c_as_cpp);
        if (failed_case(cpp, c_as_cpp, tol))
        {
            ++stats.failures;
            std::cerr << "FAILED_CASE " << c.name
                      << " controller_id=" << c.controller_id
                      << " quat_norm=" << quat_min_norm(cpp.desired_attitude, c_as_cpp.desired_attitude)
                      << " quat_angle=" << quat_angle_error_rad(cpp.desired_attitude, c_as_cpp.desired_attitude)
                      << " thrust=" << std::fabs(cpp.normalized_thrust - c_as_cpp.normalized_thrust)
                      << " acc=" << absmax3(diff3(cpp.desired_acceleration, c_as_cpp.desired_acceleration))
                      << " force=" << absmax3(diff3(cpp.desired_force_n, c_as_cpp.desired_force_n))
                      << " status=" << std::fabs(static_cast<double>(cpp.status_code - c_as_cpp.status_code))
                      << "\n";
        }
    }

    std::cout << std::setprecision(17);
    std::cout << "{\n";
    std::cout << "  \"schema\": \"mosim.px4ctrl_g9_family_c_abi_gate.v1\",\n";
    std::cout << "  \"status\": \"" << (stats.failures == 0 ? "passed" : "failed") << "\",\n";
    std::cout << "  \"controller_ids\": [1, 2, 3, 4, 5, 6, 7, 8, 9],\n";
    std::cout << "  \"case_count\": " << stats.case_count << ",\n";
    std::cout << "  \"failure_count\": " << stats.failures << ",\n";
    std::cout << "  \"tolerance\": " << tol << ",\n";
    std::cout << "  \"max_quat_min_norm\": " << stats.max_quat_min_norm << ",\n";
    std::cout << "  \"max_quat_angle_rad\": " << stats.max_quat_angle_rad << ",\n";
    std::cout << "  \"max_normalized_thrust_abs_diff\": " << stats.max_normalized_thrust << ",\n";
    std::cout << "  \"max_collective_thrust_n_abs_diff\": " << stats.max_collective_thrust_n << ",\n";
    std::cout << "  \"max_position_error_abs_diff\": " << stats.max_position_error << ",\n";
    std::cout << "  \"max_velocity_error_abs_diff\": " << stats.max_velocity_error << ",\n";
    std::cout << "  \"max_sliding_surface_abs_diff\": " << stats.max_sliding_surface << ",\n";
    std::cout << "  \"max_desired_acc_abs_diff\": " << stats.max_desired_acceleration << ",\n";
    std::cout << "  \"max_desired_body_rate_abs_diff\": " << stats.max_desired_body_rate << ",\n";
    std::cout << "  \"max_desired_body_acceleration_abs_diff\": " << stats.max_desired_body_acceleration << ",\n";
    std::cout << "  \"max_disturbance_estimate_abs_diff\": " << stats.max_disturbance_estimate << ",\n";
    std::cout << "  \"max_desired_force_n_abs_diff\": " << stats.max_desired_force_n << ",\n";
    std::cout << "  \"max_saturated_abs_diff\": " << stats.max_saturated << ",\n";
    std::cout << "  \"max_status_code_abs_diff\": " << stats.max_status_code << "\n";
    std::cout << "}\n";

    return stats.failures == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
