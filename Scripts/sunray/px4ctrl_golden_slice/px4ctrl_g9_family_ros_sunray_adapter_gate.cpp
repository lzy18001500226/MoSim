#include "px4ctrl_core.h"

extern "C" {
#ifndef GENERATED_MODEL_PRIVATE_HEADER
#define GENERATED_MODEL_PRIVATE_HEADER "G9_Family_CFunction_Sysblock_private.h"
#endif
#include GENERATED_MODEL_PRIVATE_HEADER
}

#ifndef GENERATED_MODEL_HAS_G10_BDE_INPUTS
#define GENERATED_MODEL_HAS_G10_BDE_INPUTS 0
#endif

#ifndef GENERATED_MODEL_INPUT_GLOBAL
#define GENERATED_MODEL_INPUT_GLOBAL GbIn
#endif

#ifndef GENERATED_MODEL_OUTPUT_GLOBAL
#define GENERATED_MODEL_OUTPUT_GLOBAL kGbOut
#endif

#include <algorithm>
#include <cmath>
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

constexpr int kOfficialPid = 1;
constexpr int kSe3Basic = 2;
constexpr int kDfbcBasic = 3;
constexpr int kSmcBoundaryLayer = 4;
constexpr int kPidIndi = 5;
constexpr int kNmpcOuter = 6;
constexpr int kL1Awff = 7;
constexpr int kSafetyFilter = 8;
constexpr int kFaultAllocation = 9;
constexpr int kIgnoreRollRate = 1;
constexpr int kIgnorePitchRate = 2;
constexpr int kIgnoreYawRate = 4;
constexpr int kExpectedAttitudeTypeMask = kIgnoreRollRate | kIgnorePitchRate | kIgnoreYawRate;
constexpr double kPi = 3.141592653589793238462643383279502884;
constexpr double kTol = 1.0e-12;

struct Case
{
    Case(const std::string &case_name, int selected_controller_id, const ControllerInput &case_input)
        : name(case_name), controller_id(selected_controller_id), input(case_input)
    {
    }

    std::string name;
    int controller_id{0};
    ControllerInput input;
};

struct AttitudeThrustCommand
{
    int type_mask{kExpectedAttitudeTypeMask};
    Quat orientation;
    Vec3 body_rate;
    double thrust{0.0};
    int status_code{0};
};

struct Stats
{
    int failures{0};
    int case_count{0};
    int nonfinite_command_count{0};
    int thrust_range_failure_count{0};
    double max_quat_min_norm{0.0};
    double max_quat_angle_rad{0.0};
    double max_orientation_norm_error{0.0};
    double max_thrust_abs_diff{0.0};
    double max_body_rate_abs{0.0};
    double max_status_code_abs_diff{0.0};
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

double quat_norm(const Quat &q)
{
    return std::sqrt(q.w * q.w + q.x * q.x + q.y * q.y + q.z * q.z);
}

bool finite_quat(const Quat &q)
{
    return std::isfinite(q.w) && std::isfinite(q.x) && std::isfinite(q.y) && std::isfinite(q.z);
}

bool finite_vec3(const Vec3 &v)
{
    return std::isfinite(v.x) && std::isfinite(v.y) && std::isfinite(v.z);
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
        kOfficialPid,
        kSe3Basic,
        kDfbcBasic,
        kSmcBoundaryLayer,
        kPidIndi,
        kNmpcOuter,
#if GENERATED_MODEL_HAS_G10_BDE_INPUTS
        kL1Awff,
        kSafetyFilter,
        kFaultAllocation,
#endif
    };
    const char *controller_names[] = {
        "official_pid",
        "se3_basic",
        "dfbc_basic",
        "smc_boundary_layer",
        "pid_indi",
        "nmpc_outer",
#if GENERATED_MODEL_HAS_G10_BDE_INPUTS
        "l1_awff",
        "safety_filter",
        "fault_allocation",
#endif
    };

    const int controller_count = sizeof(controller_ids) / sizeof(controller_ids[0]);
    for (int c = 0; c < controller_count; ++c)
    {
        {
            auto in = base_input();
            in.reset = true;
            cases.push_back(Case(std::string(controller_names[c]) + "_reset_hover", controller_ids[c], in));
        }
        for (int i = 0; i < 72; ++i)
        {
            const double theta = i * 2.0 * kPi / 72.0;
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
            cases.push_back(Case(std::string(controller_names[c]) + "_figure8_" + std::to_string(i), controller_ids[c], in));
        }
        {
            auto in = base_input();
            in.position = Vec3{-3.0, 0.0, 0.0};
            in.reference_position = Vec3{0.0, 0.0, 2.2};
            cases.push_back(Case(std::string(controller_names[c]) + "_limit_sample", controller_ids[c], in));
        }
        {
            auto in = base_input();
            in.enable = false;
            cases.push_back(Case(std::string(controller_names[c]) + "_disabled", controller_ids[c], in));
        }
    }
#if GENERATED_MODEL_HAS_G10_BDE_INPUTS
    {
        auto in = base_input();
        in.reset = true;
        cases.push_back(Case("l1_awff_measurement_reset", kL1Awff, in));
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
            cases.push_back(Case("l1_awff_measurement_" + std::to_string(i), kL1Awff, seq));
        }
    }
    {
        auto in = base_input();
        in.position = Vec3{-4.0, 3.0, -1.5};
        in.reference_position = Vec3{0.4, -0.2, 2.0};
        cases.push_back(Case("safety_filter_explicit_clamp", kSafetyFilter, in));
    }
    {
        auto in = base_input();
        in.reference_position = Vec3{0.2, -0.1, 1.2};
        cases.push_back(Case("fault_allocation_degraded_hover", kFaultAllocation, in));
    }
#endif
    return cases;
}

CoreParams build_params()
{
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
    params.mass = 1.0;
    params.gravity = 9.80665;
    params.hover_percentage = 0.37;
    params.min_normalized_thrust = 0.0;
    params.max_normalized_thrust = 0.62;
    params.tilt_limit_rad = 0.35;
    return params;
}

ControllerOutput run_cpp_core(
    int controller_id,
    const CoreParams &params,
    CoreState &state,
    const ControllerInput &input)
{
    switch (controller_id)
    {
    case kOfficialPid:
        return mosim_px4ctrl::calculate_official_pid_core(params, state, input);
    case kSe3Basic:
        return mosim_px4ctrl::calculate_se3_basic_core(params, state, input);
    case kDfbcBasic:
        return mosim_px4ctrl::calculate_dfbc_basic_core(params, state, input);
    case kSmcBoundaryLayer:
        return mosim_px4ctrl::calculate_smc_boundary_layer_core(params, state, input);
    case kPidIndi:
        return mosim_px4ctrl::calculate_pid_indi_bounded_core(params, state, input);
    case kNmpcOuter:
        return mosim_px4ctrl::calculate_nmpc_outer_core(params, state, input);
    case kL1Awff:
        return mosim_px4ctrl::calculate_l1_awff_core(params, state, input);
    case kSafetyFilter:
        return mosim_px4ctrl::calculate_safety_filter_core(params, state, input);
    case kFaultAllocation:
        return mosim_px4ctrl::calculate_fault_allocation_core(params, state, input);
    default:
        return ControllerOutput{};
    }
}

void set_generated_input(const CoreParams &params, const ControllerInput &input, int controller_id)
{
    GENERATED_MODEL_INPUT_GLOBAL.controller_id_in = static_cast<double>(controller_id);
    GENERATED_MODEL_INPUT_GLOBAL.dt_in = input.dt;
    GENERATED_MODEL_INPUT_GLOBAL.position_x_in = input.position.x;
    GENERATED_MODEL_INPUT_GLOBAL.position_y_in = input.position.y;
    GENERATED_MODEL_INPUT_GLOBAL.position_z_in = input.position.z;
    GENERATED_MODEL_INPUT_GLOBAL.velocity_x_in = input.velocity.x;
    GENERATED_MODEL_INPUT_GLOBAL.velocity_y_in = input.velocity.y;
    GENERATED_MODEL_INPUT_GLOBAL.velocity_z_in = input.velocity.z;
    GENERATED_MODEL_INPUT_GLOBAL.attitude_w_in = input.attitude.w;
    GENERATED_MODEL_INPUT_GLOBAL.attitude_x_in = input.attitude.x;
    GENERATED_MODEL_INPUT_GLOBAL.attitude_y_in = input.attitude.y;
    GENERATED_MODEL_INPUT_GLOBAL.attitude_z_in = input.attitude.z;
    GENERATED_MODEL_INPUT_GLOBAL.angular_velocity_x_in = input.angular_velocity.x;
    GENERATED_MODEL_INPUT_GLOBAL.angular_velocity_y_in = input.angular_velocity.y;
    GENERATED_MODEL_INPUT_GLOBAL.angular_velocity_z_in = input.angular_velocity.z;
    GENERATED_MODEL_INPUT_GLOBAL.reference_position_x_in = input.reference_position.x;
    GENERATED_MODEL_INPUT_GLOBAL.reference_position_y_in = input.reference_position.y;
    GENERATED_MODEL_INPUT_GLOBAL.reference_position_z_in = input.reference_position.z;
    GENERATED_MODEL_INPUT_GLOBAL.reference_velocity_x_in = input.reference_velocity.x;
    GENERATED_MODEL_INPUT_GLOBAL.reference_velocity_y_in = input.reference_velocity.y;
    GENERATED_MODEL_INPUT_GLOBAL.reference_velocity_z_in = input.reference_velocity.z;
    GENERATED_MODEL_INPUT_GLOBAL.reference_acceleration_x_in = input.reference_acceleration.x;
    GENERATED_MODEL_INPUT_GLOBAL.reference_acceleration_y_in = input.reference_acceleration.y;
    GENERATED_MODEL_INPUT_GLOBAL.reference_acceleration_z_in = input.reference_acceleration.z;
    GENERATED_MODEL_INPUT_GLOBAL.reference_jerk_x_in = input.reference_jerk.x;
    GENERATED_MODEL_INPUT_GLOBAL.reference_jerk_y_in = input.reference_jerk.y;
    GENERATED_MODEL_INPUT_GLOBAL.reference_jerk_z_in = input.reference_jerk.z;
    GENERATED_MODEL_INPUT_GLOBAL.reference_snap_x_in = input.reference_snap.x;
    GENERATED_MODEL_INPUT_GLOBAL.reference_snap_y_in = input.reference_snap.y;
    GENERATED_MODEL_INPUT_GLOBAL.reference_snap_z_in = input.reference_snap.z;
    GENERATED_MODEL_INPUT_GLOBAL.reference_yaw_in = input.reference_yaw;
    GENERATED_MODEL_INPUT_GLOBAL.reference_yaw_rate_in = input.reference_yaw_rate;
    GENERATED_MODEL_INPUT_GLOBAL.reference_yaw_acceleration_in = input.reference_yaw_acceleration;
    GENERATED_MODEL_INPUT_GLOBAL.measurement_stamp_s_in = input.measurement_stamp_s;
    GENERATED_MODEL_INPUT_GLOBAL.imu_attitude_w_in = input.imu_attitude.w;
    GENERATED_MODEL_INPUT_GLOBAL.imu_attitude_x_in = input.imu_attitude.x;
    GENERATED_MODEL_INPUT_GLOBAL.imu_attitude_y_in = input.imu_attitude.y;
    GENERATED_MODEL_INPUT_GLOBAL.imu_attitude_z_in = input.imu_attitude.z;
    GENERATED_MODEL_INPUT_GLOBAL.imu_angular_velocity_x_in = input.imu_angular_velocity.x;
    GENERATED_MODEL_INPUT_GLOBAL.imu_angular_velocity_y_in = input.imu_angular_velocity.y;
    GENERATED_MODEL_INPUT_GLOBAL.imu_angular_velocity_z_in = input.imu_angular_velocity.z;
    GENERATED_MODEL_INPUT_GLOBAL.enable_in = input.enable ? 1.0 : 0.0;
    GENERATED_MODEL_INPUT_GLOBAL.reset_in = input.reset ? 1.0 : 0.0;
    GENERATED_MODEL_INPUT_GLOBAL.measurement_stamp_valid_in = input.measurement_stamp_valid ? 1.0 : 0.0;
    GENERATED_MODEL_INPUT_GLOBAL.enable_disturbance_observer_in = input.enable_disturbance_observer ? 1.0 : 0.0;
    GENERATED_MODEL_INPUT_GLOBAL.kp_x_in = params.kp[0];
    GENERATED_MODEL_INPUT_GLOBAL.kp_y_in = params.kp[1];
    GENERATED_MODEL_INPUT_GLOBAL.kp_z_in = params.kp[2];
    GENERATED_MODEL_INPUT_GLOBAL.kv_x_in = params.kv[0];
    GENERATED_MODEL_INPUT_GLOBAL.kv_y_in = params.kv[1];
    GENERATED_MODEL_INPUT_GLOBAL.kv_z_in = params.kv[2];
    GENERATED_MODEL_INPUT_GLOBAL.ki_x_in = params.ki[0];
    GENERATED_MODEL_INPUT_GLOBAL.ki_y_in = params.ki[1];
    GENERATED_MODEL_INPUT_GLOBAL.ki_z_in = params.ki[2];
    GENERATED_MODEL_INPUT_GLOBAL.smc_lambda_x_in = params.smc_lambda[0];
    GENERATED_MODEL_INPUT_GLOBAL.smc_lambda_y_in = params.smc_lambda[1];
    GENERATED_MODEL_INPUT_GLOBAL.smc_lambda_z_in = params.smc_lambda[2];
    GENERATED_MODEL_INPUT_GLOBAL.smc_eta_x_in = params.smc_eta[0];
    GENERATED_MODEL_INPUT_GLOBAL.smc_eta_y_in = params.smc_eta[1];
    GENERATED_MODEL_INPUT_GLOBAL.smc_eta_z_in = params.smc_eta[2];
    GENERATED_MODEL_INPUT_GLOBAL.smc_phi_x_in = params.smc_phi[0];
    GENERATED_MODEL_INPUT_GLOBAL.smc_phi_y_in = params.smc_phi[1];
    GENERATED_MODEL_INPUT_GLOBAL.smc_phi_z_in = params.smc_phi[2];
    GENERATED_MODEL_INPUT_GLOBAL.smc_surface_limit_x_in = params.smc_surface_limit[0];
    GENERATED_MODEL_INPUT_GLOBAL.smc_surface_limit_y_in = params.smc_surface_limit[1];
    GENERATED_MODEL_INPUT_GLOBAL.smc_surface_limit_z_in = params.smc_surface_limit[2];
    GENERATED_MODEL_INPUT_GLOBAL.indi_gain_x_in = params.indi_gain[0];
    GENERATED_MODEL_INPUT_GLOBAL.indi_gain_y_in = params.indi_gain[1];
    GENERATED_MODEL_INPUT_GLOBAL.indi_gain_z_in = params.indi_gain[2];
    GENERATED_MODEL_INPUT_GLOBAL.indi_increment_limit_x_in = params.indi_increment_limit[0];
    GENERATED_MODEL_INPUT_GLOBAL.indi_increment_limit_y_in = params.indi_increment_limit[1];
    GENERATED_MODEL_INPUT_GLOBAL.indi_increment_limit_z_in = params.indi_increment_limit[2];
    GENERATED_MODEL_INPUT_GLOBAL.indi_measured_accel_limit_x_in = params.indi_measured_accel_limit[0];
    GENERATED_MODEL_INPUT_GLOBAL.indi_measured_accel_limit_y_in = params.indi_measured_accel_limit[1];
    GENERATED_MODEL_INPUT_GLOBAL.indi_measured_accel_limit_z_in = params.indi_measured_accel_limit[2];
    GENERATED_MODEL_INPUT_GLOBAL.indi_accel_lpf_alpha_in = params.indi_accel_lpf_alpha;
    GENERATED_MODEL_INPUT_GLOBAL.nmpc_horizon_s_in = params.nmpc_horizon_s;
    GENERATED_MODEL_INPUT_GLOBAL.nmpc_position_weight_x_in = params.nmpc_position_weight[0];
    GENERATED_MODEL_INPUT_GLOBAL.nmpc_position_weight_y_in = params.nmpc_position_weight[1];
    GENERATED_MODEL_INPUT_GLOBAL.nmpc_position_weight_z_in = params.nmpc_position_weight[2];
    GENERATED_MODEL_INPUT_GLOBAL.nmpc_velocity_weight_x_in = params.nmpc_velocity_weight[0];
    GENERATED_MODEL_INPUT_GLOBAL.nmpc_velocity_weight_y_in = params.nmpc_velocity_weight[1];
    GENERATED_MODEL_INPUT_GLOBAL.nmpc_velocity_weight_z_in = params.nmpc_velocity_weight[2];
    GENERATED_MODEL_INPUT_GLOBAL.nmpc_control_weight_x_in = params.nmpc_control_weight[0];
    GENERATED_MODEL_INPUT_GLOBAL.nmpc_control_weight_y_in = params.nmpc_control_weight[1];
    GENERATED_MODEL_INPUT_GLOBAL.nmpc_control_weight_z_in = params.nmpc_control_weight[2];
    GENERATED_MODEL_INPUT_GLOBAL.nmpc_accel_limit_x_in = params.nmpc_accel_limit[0];
    GENERATED_MODEL_INPUT_GLOBAL.nmpc_accel_limit_y_in = params.nmpc_accel_limit[1];
    GENERATED_MODEL_INPUT_GLOBAL.nmpc_accel_limit_z_in = params.nmpc_accel_limit[2];
    GENERATED_MODEL_INPUT_GLOBAL.nmpc_increment_limit_x_in = params.nmpc_increment_limit[0];
    GENERATED_MODEL_INPUT_GLOBAL.nmpc_increment_limit_y_in = params.nmpc_increment_limit[1];
    GENERATED_MODEL_INPUT_GLOBAL.nmpc_increment_limit_z_in = params.nmpc_increment_limit[2];
#if GENERATED_MODEL_HAS_G10_BDE_INPUTS
    GENERATED_MODEL_INPUT_GLOBAL.l1_model_decay_in = params.l1_model_decay;
    GENERATED_MODEL_INPUT_GLOBAL.l1_filter_T_in = params.l1_filter_T;
    GENERATED_MODEL_INPUT_GLOBAL.l1_gain_x_in = params.l1_gain[0];
    GENERATED_MODEL_INPUT_GLOBAL.l1_gain_y_in = params.l1_gain[1];
    GENERATED_MODEL_INPUT_GLOBAL.l1_gain_z_in = params.l1_gain[2];
    GENERATED_MODEL_INPUT_GLOBAL.l1_comp_limit_x_in = params.l1_comp_limit[0];
    GENERATED_MODEL_INPUT_GLOBAL.l1_comp_limit_y_in = params.l1_comp_limit[1];
    GENERATED_MODEL_INPUT_GLOBAL.l1_comp_limit_z_in = params.l1_comp_limit[2];
    GENERATED_MODEL_INPUT_GLOBAL.drag_feedforward_gain_x_in = params.drag_feedforward_gain[0];
    GENERATED_MODEL_INPUT_GLOBAL.drag_feedforward_gain_y_in = params.drag_feedforward_gain[1];
    GENERATED_MODEL_INPUT_GLOBAL.drag_feedforward_gain_z_in = params.drag_feedforward_gain[2];
    GENERATED_MODEL_INPUT_GLOBAL.safety_accel_limit_x_in = params.safety_accel_limit[0];
    GENERATED_MODEL_INPUT_GLOBAL.safety_accel_limit_y_in = params.safety_accel_limit[1];
    GENERATED_MODEL_INPUT_GLOBAL.safety_accel_limit_z_in = params.safety_accel_limit[2];
    GENERATED_MODEL_INPUT_GLOBAL.fault_rotor_efficiency_1_in = params.fault_rotor_efficiency[0];
    GENERATED_MODEL_INPUT_GLOBAL.fault_rotor_efficiency_2_in = params.fault_rotor_efficiency[1];
    GENERATED_MODEL_INPUT_GLOBAL.fault_rotor_efficiency_3_in = params.fault_rotor_efficiency[2];
    GENERATED_MODEL_INPUT_GLOBAL.fault_rotor_efficiency_4_in = params.fault_rotor_efficiency[3];
    GENERATED_MODEL_INPUT_GLOBAL.fault_allocation_blend_in = params.fault_allocation_blend;
    GENERATED_MODEL_INPUT_GLOBAL.fault_min_efficiency_in = params.fault_min_efficiency;
    GENERATED_MODEL_INPUT_GLOBAL.fault_thrust_comp_limit_in = params.fault_thrust_comp_limit;
#endif
    GENERATED_MODEL_INPUT_GLOBAL.integral_limit_x_in = params.integral_limit[0];
    GENERATED_MODEL_INPUT_GLOBAL.integral_limit_y_in = params.integral_limit[1];
    GENERATED_MODEL_INPUT_GLOBAL.integral_limit_z_in = params.integral_limit[2];
    GENERATED_MODEL_INPUT_GLOBAL.mass_in = params.mass;
    GENERATED_MODEL_INPUT_GLOBAL.gravity_in = params.gravity;
    GENERATED_MODEL_INPUT_GLOBAL.hover_percentage_in = params.hover_percentage;
    GENERATED_MODEL_INPUT_GLOBAL.min_normalized_thrust_in = params.min_normalized_thrust;
    GENERATED_MODEL_INPUT_GLOBAL.max_normalized_thrust_in = params.max_normalized_thrust;
    GENERATED_MODEL_INPUT_GLOBAL.tilt_limit_rad_in = params.tilt_limit_rad;
}

AttitudeThrustCommand run_generated_adapter(
    const CoreParams &params,
    const ControllerInput &input,
    int controller_id)
{
    set_generated_input(params, input, controller_id);
    Step();

    AttitudeThrustCommand command;
    command.type_mask = kExpectedAttitudeTypeMask;
    command.orientation = mosim_px4ctrl::normalize(Quat{
        GENERATED_MODEL_OUTPUT_GLOBAL.desired_attitude_w_out,
        GENERATED_MODEL_OUTPUT_GLOBAL.desired_attitude_x_out,
        GENERATED_MODEL_OUTPUT_GLOBAL.desired_attitude_y_out,
        GENERATED_MODEL_OUTPUT_GLOBAL.desired_attitude_z_out});
    command.body_rate = Vec3{0.0, 0.0, 0.0};
    command.thrust = GENERATED_MODEL_OUTPUT_GLOBAL.normalized_thrust_out;
    command.status_code = static_cast<int>(GENERATED_MODEL_OUTPUT_GLOBAL.status_code_out);
    return command;
}

bool command_is_finite(const AttitudeThrustCommand &command)
{
    return finite_quat(command.orientation) &&
        finite_vec3(command.body_rate) &&
        std::isfinite(command.thrust);
}

void update_stats(
    Stats &stats,
    const ControllerOutput &expected,
    const AttitudeThrustCommand &command)
{
    stats.max_quat_min_norm = std::max(stats.max_quat_min_norm, quat_min_norm(expected.desired_attitude, command.orientation));
    stats.max_quat_angle_rad = std::max(stats.max_quat_angle_rad, quat_angle_error_rad(expected.desired_attitude, command.orientation));
    stats.max_orientation_norm_error = std::max(stats.max_orientation_norm_error, std::fabs(quat_norm(command.orientation) - 1.0));
    stats.max_thrust_abs_diff = std::max(stats.max_thrust_abs_diff, std::fabs(expected.normalized_thrust - command.thrust));
    stats.max_body_rate_abs = std::max(stats.max_body_rate_abs, absmax3(command.body_rate));
    stats.max_status_code_abs_diff = std::max(stats.max_status_code_abs_diff, std::fabs(static_cast<double>(expected.status_code - command.status_code)));
}

bool command_failed(
    const CoreParams &params,
    const ControllerOutput &expected,
    const AttitudeThrustCommand &command)
{
    return command.type_mask != kExpectedAttitudeTypeMask ||
        !command_is_finite(command) ||
        command.thrust < params.min_normalized_thrust - kTol ||
        command.thrust > params.max_normalized_thrust + kTol ||
        quat_min_norm(expected.desired_attitude, command.orientation) > kTol ||
        quat_angle_error_rad(expected.desired_attitude, command.orientation) > kTol ||
        std::fabs(quat_norm(command.orientation) - 1.0) > kTol ||
        std::fabs(expected.normalized_thrust - command.thrust) > kTol ||
        absmax3(command.body_rate) > kTol ||
        expected.status_code != command.status_code;
}

} // namespace

int main()
{
    const CoreParams params = build_params();
    CoreState cpp_states[10];
    for (int i = 0; i < 10; ++i)
    {
        mosim_px4ctrl::reset_thrust_mapping(params, cpp_states[i]);
    }
    Init();

    const auto cases = build_cases();
    Stats stats;
    for (const auto &c : cases)
    {
        const ControllerOutput expected = run_cpp_core(
            c.controller_id,
            params,
            cpp_states[c.controller_id],
            c.input);
        const AttitudeThrustCommand command = run_generated_adapter(params, c.input, c.controller_id);

        ++stats.case_count;
        update_stats(stats, expected, command);
        if (!command_is_finite(command))
        {
            ++stats.nonfinite_command_count;
        }
        if (command.thrust < params.min_normalized_thrust - kTol ||
            command.thrust > params.max_normalized_thrust + kTol)
        {
            ++stats.thrust_range_failure_count;
        }
        if (command_failed(params, expected, command))
        {
            ++stats.failures;
            std::cerr << "FAILED_CASE " << c.name
                      << " controller_id=" << c.controller_id
                      << " type_mask=" << command.type_mask
                      << " quat_norm=" << quat_min_norm(expected.desired_attitude, command.orientation)
                      << " quat_angle=" << quat_angle_error_rad(expected.desired_attitude, command.orientation)
                      << " orientation_norm_error=" << std::fabs(quat_norm(command.orientation) - 1.0)
                      << " thrust=" << std::fabs(expected.normalized_thrust - command.thrust)
                      << " body_rate=" << absmax3(command.body_rate)
                      << " status=" << std::fabs(static_cast<double>(expected.status_code - command.status_code))
                      << "\n";
        }
    }

    std::cout << std::setprecision(17);
    std::cout << "{\n";
    std::cout << "  \"schema\": \"mosim.px4ctrl_g9_family_ros_sunray_adapter_gate.v1\",\n";
    std::cout << "  \"status\": \"" << (stats.failures == 0 ? "passed" : "failed") << "\",\n";
#if GENERATED_MODEL_HAS_G10_BDE_INPUTS
    std::cout << "  \"claim_boundary\": \"Static ROS/Sunray adapter gate only. It proves the G9 family plus accepted G10-B/D/E generated C output can be normalized to the px4ctrl/MAVROS attitude plus normalized-thrust command shape; no ROS, Gazebo, PX4, MAVROS, RViz, or flight runtime is executed.\",\n";
    std::cout << "  \"controller_ids\": [1, 2, 3, 4, 5, 6, 7, 8, 9],\n";
#else
    std::cout << "  \"claim_boundary\": \"Static ROS/Sunray adapter gate only. It proves the G9 generated C output can be normalized to the px4ctrl/MAVROS attitude plus normalized-thrust command shape; no ROS, Gazebo, PX4, MAVROS, RViz, or flight runtime is executed.\",\n";
    std::cout << "  \"controller_ids\": [1, 2, 3, 4, 5, 6],\n";
#endif
    std::cout << "  \"case_count\": " << stats.case_count << ",\n";
    std::cout << "  \"failure_count\": " << stats.failures << ",\n";
    std::cout << "  \"nonfinite_command_count\": " << stats.nonfinite_command_count << ",\n";
    std::cout << "  \"thrust_range_failure_count\": " << stats.thrust_range_failure_count << ",\n";
    std::cout << "  \"attitude_target_type_mask\": " << kExpectedAttitudeTypeMask << ",\n";
    std::cout << "  \"max_quat_min_norm\": " << stats.max_quat_min_norm << ",\n";
    std::cout << "  \"max_quat_angle_rad\": " << stats.max_quat_angle_rad << ",\n";
    std::cout << "  \"max_orientation_norm_error\": " << stats.max_orientation_norm_error << ",\n";
    std::cout << "  \"max_thrust_abs_diff\": " << stats.max_thrust_abs_diff << ",\n";
    std::cout << "  \"max_body_rate_abs\": " << stats.max_body_rate_abs << ",\n";
    std::cout << "  \"max_status_code_abs_diff\": " << stats.max_status_code_abs_diff << "\n";
    std::cout << "}\n";

    return stats.failures == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
