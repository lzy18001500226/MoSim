#include "px4ctrl_core.h"

#include <algorithm>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <limits>
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
    ControllerInput input;
};

struct DiffStats
{
    double max_quat_norm{0.0};
    double max_quat_angle_rad{0.0};
    double max_norm_thrust{0.0};
    double max_collective_thrust_n{0.0};
    double max_acc{0.0};
    double max_force_n{0.0};
    int failures{0};
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

// Direct, ROS-free transcription of References/Lab/planning_local/Fast-Drone-250/
// src/realflight_modules/px4ctrl/src/controller.cpp::LinearControl::calculateControl.
ControllerOutput upstream_reference_calculate(
    const CoreParams &params,
    CoreState &state,
    const ControllerInput &input)
{
    if (input.reset)
    {
        mosim_px4ctrl::reset_thrust_mapping(params, state);
    }

    ControllerOutput out;

    if (!input.enable)
    {
        out.status_code = 1;
        out.status_text = "disabled";
        out.desired_attitude = mosim_px4ctrl::normalize(input.imu_attitude);
        return out;
    }

    out.position_error = Vec3{
        input.reference_position.x - input.position.x,
        input.reference_position.y - input.position.y,
        input.reference_position.z - input.position.z,
    };
    out.velocity_error = Vec3{
        input.reference_velocity.x - input.velocity.x,
        input.reference_velocity.y - input.velocity.y,
        input.reference_velocity.z - input.velocity.z,
    };

    out.desired_acceleration = Vec3{
        input.reference_acceleration.x + params.kv[0] * out.velocity_error.x + params.kp[0] * out.position_error.x,
        input.reference_acceleration.y + params.kv[1] * out.velocity_error.y + params.kp[1] * out.position_error.y,
        input.reference_acceleration.z + params.kv[2] * out.velocity_error.z + params.kp[2] * out.position_error.z,
    };
    out.desired_acceleration.z += params.gravity;

    out.normalized_thrust = out.desired_acceleration.z / state.thr2acc;
    out.collective_thrust_n = out.normalized_thrust * (params.mass * params.gravity / params.hover_percentage);
    out.desired_force_n = Vec3{
        params.mass * out.desired_acceleration.x,
        params.mass * out.desired_acceleration.y,
        params.mass * out.desired_acceleration.z,
    };

    const double yaw_odom = mosim_px4ctrl::yaw_from_quat(input.attitude);
    const double sin_yaw = std::sin(yaw_odom);
    const double cos_yaw = std::cos(yaw_odom);
    const double roll = (out.desired_acceleration.x * sin_yaw - out.desired_acceleration.y * cos_yaw) / params.gravity;
    const double pitch = (out.desired_acceleration.x * cos_yaw + out.desired_acceleration.y * sin_yaw) / params.gravity;

    const Quat q = mosim_px4ctrl::multiply(
        mosim_px4ctrl::multiply(
            mosim_px4ctrl::angle_axis(input.reference_yaw, Vec3{0.0, 0.0, 1.0}),
            mosim_px4ctrl::angle_axis(pitch, Vec3{0.0, 1.0, 0.0})),
        mosim_px4ctrl::angle_axis(roll, Vec3{1.0, 0.0, 0.0}));
    out.desired_attitude = mosim_px4ctrl::multiply(
        mosim_px4ctrl::multiply(input.imu_attitude, mosim_px4ctrl::inverse(input.attitude)),
        q);

    return out;
}

std::vector<Case> build_cases()
{
    std::vector<Case> cases;

    auto base = []() {
        ControllerInput in;
        in.dt = 0.01;
        in.attitude = quat_from_rpy(0.0, 0.0, 0.0);
        in.imu_attitude = in.attitude;
        in.reference_yaw = 0.0;
        return in;
    };

    {
        auto in = base();
        in.reference_position = in.position;
        cases.push_back({"static_zero_hover", in});
    }

    for (int i = 0; i < 80; ++i)
    {
        const double t = 0.01 * i;
        auto in = base();
        in.position = Vec3{0.02 * std::sin(t), -0.01 * std::cos(t), 1.0 + 0.01 * std::sin(0.5 * t)};
        in.velocity = Vec3{0.01 * std::cos(t), 0.005 * std::sin(t), 0.002};
        in.reference_position = Vec3{0.0, 0.0, 1.0};
        in.attitude = quat_from_rpy(0.01 * std::sin(t), -0.01 * std::cos(t), 0.02 * std::sin(t));
        in.imu_attitude = in.attitude;
        cases.push_back({"hover_replay_" + std::to_string(i), in});
    }

    for (int i = 0; i < 50; ++i)
    {
        auto in = base();
        in.position = Vec3{0.5 * (1.0 - std::exp(-0.04 * i)), 0.0, 1.0};
        in.velocity = Vec3{0.02 * std::exp(-0.04 * i), 0.0, 0.0};
        in.reference_position = Vec3{1.0, 0.0, 1.0};
        in.reference_velocity = Vec3{0.0, 0.0, 0.0};
        cases.push_back({"x_step_replay_" + std::to_string(i), in});
    }

    for (int i = 0; i < 90; ++i)
    {
        const double theta = i * 2.0 * M_PI / 90.0;
        auto in = base();
        in.position = Vec3{0.75 * std::cos(theta - 0.04), 0.75 * std::sin(theta - 0.04), 1.0};
        in.velocity = Vec3{-0.5 * std::sin(theta - 0.04), 0.5 * std::cos(theta - 0.04), 0.0};
        in.reference_position = Vec3{0.75 * std::cos(theta), 0.75 * std::sin(theta), 1.0};
        in.reference_velocity = Vec3{-0.5 * std::sin(theta), 0.5 * std::cos(theta), 0.0};
        in.reference_acceleration = Vec3{-0.35 * std::cos(theta), -0.35 * std::sin(theta), 0.0};
        in.reference_yaw = 0.2 * std::sin(theta);
        in.attitude = quat_from_rpy(0.02 * std::sin(theta), 0.03 * std::cos(theta), 0.2 * std::sin(theta - 0.03));
        in.imu_attitude = in.attitude;
        cases.push_back({"circle_replay_" + std::to_string(i), in});
    }

    for (int i = 0; i < 120; ++i)
    {
        const double theta = i * 2.0 * M_PI / 120.0;
        auto in = base();
        in.position = Vec3{0.8 * std::sin(theta - 0.05), 0.4 * std::sin(2.0 * (theta - 0.05)), 1.0};
        in.velocity = Vec3{0.8 * std::cos(theta - 0.05), 0.8 * std::cos(2.0 * (theta - 0.05)), 0.0};
        in.reference_position = Vec3{0.8 * std::sin(theta), 0.4 * std::sin(2.0 * theta), 1.0};
        in.reference_velocity = Vec3{0.8 * std::cos(theta), 0.8 * std::cos(2.0 * theta), 0.0};
        in.reference_acceleration = Vec3{-0.8 * std::sin(theta), -1.6 * std::sin(2.0 * theta), 0.0};
        in.reference_yaw = 0.1 * std::cos(theta);
        in.attitude = quat_from_rpy(0.02 * std::sin(2.0 * theta), -0.02 * std::cos(theta), 0.1 * std::cos(theta - 0.04));
        in.imu_attitude = in.attitude;
        cases.push_back({"figure8_replay_" + std::to_string(i), in});
    }

    {
        auto in = base();
        in.enable = false;
        cases.push_back({"disabled_sample", in});
    }

    {
        auto in = base();
        in.reset = true;
        in.position = Vec3{0.1, -0.2, 0.95};
        in.reference_position = Vec3{0.0, 0.0, 1.0};
        cases.push_back({"reset_reenable_sample", in});
    }

    return cases;
}

void update_stats(DiffStats &stats, const ControllerOutput &ref, const ControllerOutput &core)
{
    stats.max_quat_norm = std::max(stats.max_quat_norm, quat_min_norm(ref.desired_attitude, core.desired_attitude));
    stats.max_quat_angle_rad = std::max(stats.max_quat_angle_rad, quat_angle_error_rad(ref.desired_attitude, core.desired_attitude));
    stats.max_norm_thrust = std::max(stats.max_norm_thrust, std::fabs(ref.normalized_thrust - core.normalized_thrust));
    stats.max_collective_thrust_n = std::max(stats.max_collective_thrust_n, std::fabs(ref.collective_thrust_n - core.collective_thrust_n));
    stats.max_acc = std::max(stats.max_acc, absmax3(diff3(ref.desired_acceleration, core.desired_acceleration)));
    stats.max_force_n = std::max(stats.max_force_n, absmax3(diff3(ref.desired_force_n, core.desired_force_n)));
}

} // namespace

int main()
{
    const double quat_tol = 1.0e-12;
    const double angle_tol = 1.0e-12;
    const double thrust_tol = 1.0e-12;
    const double force_tol = 1.0e-12;

    CoreParams params;
    params.kp[0] = 1.5;
    params.kp[1] = 1.5;
    params.kp[2] = 1.5;
    params.kv[0] = 1.5;
    params.kv[1] = 1.5;
    params.kv[2] = 1.5;
    params.mass = 0.67;
    params.gravity = 9.8;
    params.hover_percentage = 0.37;

    CoreState ref_state;
    CoreState core_state;
    mosim_px4ctrl::reset_thrust_mapping(params, ref_state);
    mosim_px4ctrl::reset_thrust_mapping(params, core_state);

    const auto cases = build_cases();
    DiffStats stats;

    for (const auto &c : cases)
    {
        auto ref = upstream_reference_calculate(params, ref_state, c.input);
        auto core = mosim_px4ctrl::calculate_px4ctrl_core(params, core_state, c.input);
        update_stats(stats, ref, core);

        const bool failed =
            quat_min_norm(ref.desired_attitude, core.desired_attitude) > quat_tol ||
            quat_angle_error_rad(ref.desired_attitude, core.desired_attitude) > angle_tol ||
            std::fabs(ref.normalized_thrust - core.normalized_thrust) > thrust_tol ||
            std::fabs(ref.collective_thrust_n - core.collective_thrust_n) > thrust_tol ||
            absmax3(diff3(ref.desired_acceleration, core.desired_acceleration)) > thrust_tol ||
            absmax3(diff3(ref.desired_force_n, core.desired_force_n)) > force_tol ||
            ref.status_code != core.status_code;
        if (failed)
        {
            stats.failures += 1;
            std::cerr << "FAILED_CASE " << c.name << "\n";
        }
    }

    std::cout << std::setprecision(17);
    std::cout << "{\n";
    std::cout << "  \"schema\": \"mosim.px4ctrl_g5_offline_gate.v1\",\n";
    std::cout << "  \"status\": \"" << (stats.failures == 0 ? "passed" : "failed") << "\",\n";
    std::cout << "  \"case_count\": " << cases.size() << ",\n";
    std::cout << "  \"failure_count\": " << stats.failures << ",\n";
    std::cout << "  \"max_quat_min_norm\": " << stats.max_quat_norm << ",\n";
    std::cout << "  \"max_quat_angle_rad\": " << stats.max_quat_angle_rad << ",\n";
    std::cout << "  \"max_normalized_thrust_abs_diff\": " << stats.max_norm_thrust << ",\n";
    std::cout << "  \"max_collective_thrust_n_abs_diff\": " << stats.max_collective_thrust_n << ",\n";
    std::cout << "  \"max_desired_acc_abs_diff\": " << stats.max_acc << ",\n";
    std::cout << "  \"max_desired_force_n_abs_diff\": " << stats.max_force_n << "\n";
    std::cout << "}\n";

    return stats.failures == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
