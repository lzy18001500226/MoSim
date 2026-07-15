#include "px4ctrl_core.h"

extern "C" {
#include "G9A_OfficialPID_CFunction_Sysblock_private.h"
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
    ControllerInput input;
};

struct DiffStats
{
    double max_quat_norm{0.0};
    double max_quat_angle_rad{0.0};
    double max_norm_thrust{0.0};
    double max_collective_thrust_n{0.0};
    double max_position_error{0.0};
    double max_velocity_error{0.0};
    double max_acc{0.0};
    double max_force_n{0.0};
    double max_saturated{0.0};
    double max_status_code{0.0};
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

std::vector<Case> build_cases()
{
    std::vector<Case> cases;

    auto base = []() {
        ControllerInput in;
        in.dt = 0.01;
        in.position = Vec3{0.0, 0.0, 1.0};
        in.attitude = quat_from_rpy(0.0, 0.0, 0.0);
        in.imu_attitude = in.attitude;
        in.reference_position = Vec3{0.0, 0.0, 1.0};
        in.reference_yaw = 0.0;
        return in;
    };

    {
        auto in = base();
        cases.push_back({"static_hover", in});
    }

    for (int i = 0; i < 120; ++i)
    {
        const double theta = i * 2.0 * M_PI / 120.0;
        auto in = base();
        in.position = Vec3{
            0.8 * std::sin(theta - 0.05),
            0.4 * std::sin(2.0 * (theta - 0.05)),
            1.0 + 0.03 * std::sin(theta)};
        in.velocity = Vec3{
            0.8 * std::cos(theta - 0.05),
            0.8 * std::cos(2.0 * (theta - 0.05)),
            0.03 * std::cos(theta)};
        in.reference_position = Vec3{
            0.8 * std::sin(theta),
            0.4 * std::sin(2.0 * theta),
            1.0};
        in.reference_velocity = Vec3{
            0.8 * std::cos(theta),
            0.8 * std::cos(2.0 * theta),
            0.0};
        in.reference_acceleration = Vec3{
            -0.8 * std::sin(theta),
            -1.6 * std::sin(2.0 * theta),
            0.0};
        in.reference_yaw = 0.1 * std::cos(theta);
        in.attitude = quat_from_rpy(
            0.02 * std::sin(2.0 * theta),
            -0.02 * std::cos(theta),
            0.1 * std::cos(theta - 0.04));
        in.imu_attitude = in.attitude;
        cases.push_back({"figure8_" + std::to_string(i), in});
    }

    for (int i = 0; i < 90; ++i)
    {
        auto in = base();
        in.position = Vec3{0.2, -0.1, 0.82};
        in.reference_position = Vec3{0.0, 0.0, 1.0};
        in.reference_velocity = Vec3{0.0, 0.0, 0.0};
        in.reset = i == 0;
        cases.push_back({"persistent_z_integral_" + std::to_string(i), in});
    }

    {
        auto in = base();
        in.position = Vec3{-3.0, 0.0, 0.0};
        in.reference_position = Vec3{0.0, 0.0, 2.0};
        cases.push_back({"limit_sample", in});
    }

    {
        auto in = base();
        in.enable = false;
        cases.push_back({"disabled_sample", in});
    }

    {
        auto in = base();
        in.position = Vec3{0.2, -0.1, 0.9};
        in.reference_position = Vec3{0.0, 0.0, 1.0};
        in.reset = true;
        cases.push_back({"reset_sample", in});
    }

    return cases;
}

void set_generated_input(const CoreParams &params, const ControllerInput &input)
{
    ysblockGbIn.dt_in = input.dt;
    ysblockGbIn.position_x_in = input.position.x;
    ysblockGbIn.position_y_in = input.position.y;
    ysblockGbIn.position_z_in = input.position.z;
    ysblockGbIn.velocity_x_in = input.velocity.x;
    ysblockGbIn.velocity_y_in = input.velocity.y;
    ysblockGbIn.velocity_z_in = input.velocity.z;
    ysblockGbIn.attitude_w_in = input.attitude.w;
    ysblockGbIn.attitude_x_in = input.attitude.x;
    ysblockGbIn.attitude_y_in = input.attitude.y;
    ysblockGbIn.attitude_z_in = input.attitude.z;
    ysblockGbIn.angular_velocity_x_in = input.angular_velocity.x;
    ysblockGbIn.angular_velocity_y_in = input.angular_velocity.y;
    ysblockGbIn.angular_velocity_z_in = input.angular_velocity.z;
    ysblockGbIn.reference_position_x_in = input.reference_position.x;
    ysblockGbIn.reference_position_y_in = input.reference_position.y;
    ysblockGbIn.reference_position_z_in = input.reference_position.z;
    ysblockGbIn.reference_velocity_x_in = input.reference_velocity.x;
    ysblockGbIn.reference_velocity_y_in = input.reference_velocity.y;
    ysblockGbIn.reference_velocity_z_in = input.reference_velocity.z;
    ysblockGbIn.reference_acceleration_x_in = input.reference_acceleration.x;
    ysblockGbIn.reference_acceleration_y_in = input.reference_acceleration.y;
    ysblockGbIn.reference_acceleration_z_in = input.reference_acceleration.z;
    ysblockGbIn.reference_yaw_in = input.reference_yaw;
    ysblockGbIn.reference_yaw_rate_in = input.reference_yaw_rate;
    ysblockGbIn.imu_attitude_w_in = input.imu_attitude.w;
    ysblockGbIn.imu_attitude_x_in = input.imu_attitude.x;
    ysblockGbIn.imu_attitude_y_in = input.imu_attitude.y;
    ysblockGbIn.imu_attitude_z_in = input.imu_attitude.z;
    ysblockGbIn.imu_angular_velocity_x_in = input.imu_angular_velocity.x;
    ysblockGbIn.imu_angular_velocity_y_in = input.imu_angular_velocity.y;
    ysblockGbIn.imu_angular_velocity_z_in = input.imu_angular_velocity.z;
    ysblockGbIn.enable_in = input.enable ? 1.0 : 0.0;
    ysblockGbIn.reset_in = input.reset ? 1.0 : 0.0;
    ysblockGbIn.kp_x_in = params.kp[0];
    ysblockGbIn.kp_y_in = params.kp[1];
    ysblockGbIn.kp_z_in = params.kp[2];
    ysblockGbIn.kv_x_in = params.kv[0];
    ysblockGbIn.kv_y_in = params.kv[1];
    ysblockGbIn.kv_z_in = params.kv[2];
    ysblockGbIn.ki_x_in = params.ki[0];
    ysblockGbIn.ki_y_in = params.ki[1];
    ysblockGbIn.ki_z_in = params.ki[2];
    ysblockGbIn.integral_limit_x_in = params.integral_limit[0];
    ysblockGbIn.integral_limit_y_in = params.integral_limit[1];
    ysblockGbIn.integral_limit_z_in = params.integral_limit[2];
    ysblockGbIn.mass_in = params.mass;
    ysblockGbIn.gravity_in = params.gravity;
    ysblockGbIn.hover_percentage_in = params.hover_percentage;
    ysblockGbIn.min_normalized_thrust_in = params.min_normalized_thrust;
    ysblockGbIn.max_normalized_thrust_in = params.max_normalized_thrust;
    ysblockGbIn.tilt_limit_rad_in = params.tilt_limit_rad;
}

ControllerOutput get_generated_output()
{
    ControllerOutput out;
    out.desired_attitude = Quat{
        sysblockGbOut.desired_attitude_w_out,
        sysblockGbOut.desired_attitude_x_out,
        sysblockGbOut.desired_attitude_y_out,
        sysblockGbOut.desired_attitude_z_out};
    out.normalized_thrust = sysblockGbOut.normalized_thrust_out;
    out.collective_thrust_n = sysblockGbOut.collective_thrust_N_out;
    out.position_error = Vec3{
        sysblockGbOut.position_error_x_out,
        sysblockGbOut.position_error_y_out,
        sysblockGbOut.position_error_z_out};
    out.velocity_error = Vec3{
        sysblockGbOut.velocity_error_x_out,
        sysblockGbOut.velocity_error_y_out,
        sysblockGbOut.velocity_error_z_out};
    out.desired_acceleration = Vec3{
        sysblockGbOut.desired_acceleration_x_out,
        sysblockGbOut.desired_acceleration_y_out,
        sysblockGbOut.desired_acceleration_z_out};
    out.desired_force_n = Vec3{
        sysblockGbOut.desired_force_N_x_out,
        sysblockGbOut.desired_force_N_y_out,
        sysblockGbOut.desired_force_N_z_out};
    out.saturated = sysblockGbOut.saturated_out != 0.0;
    out.status_code = static_cast<int>(sysblockGbOut.status_code_out);
    return out;
}

void update_stats(DiffStats &stats, const ControllerOutput &ref, const ControllerOutput &core)
{
    stats.max_quat_norm = std::max(stats.max_quat_norm, quat_min_norm(ref.desired_attitude, core.desired_attitude));
    stats.max_quat_angle_rad = std::max(stats.max_quat_angle_rad, quat_angle_error_rad(ref.desired_attitude, core.desired_attitude));
    stats.max_norm_thrust = std::max(stats.max_norm_thrust, std::fabs(ref.normalized_thrust - core.normalized_thrust));
    stats.max_collective_thrust_n = std::max(stats.max_collective_thrust_n, std::fabs(ref.collective_thrust_n - core.collective_thrust_n));
    stats.max_position_error = std::max(stats.max_position_error, absmax3(diff3(ref.position_error, core.position_error)));
    stats.max_velocity_error = std::max(stats.max_velocity_error, absmax3(diff3(ref.velocity_error, core.velocity_error)));
    stats.max_acc = std::max(stats.max_acc, absmax3(diff3(ref.desired_acceleration, core.desired_acceleration)));
    stats.max_force_n = std::max(stats.max_force_n, absmax3(diff3(ref.desired_force_n, core.desired_force_n)));
    stats.max_saturated = std::max(stats.max_saturated, std::fabs(static_cast<double>(ref.saturated) - static_cast<double>(core.saturated)));
    stats.max_status_code = std::max(stats.max_status_code, std::fabs(static_cast<double>(ref.status_code - core.status_code)));
}

bool failed_case(const ControllerOutput &cpp, const ControllerOutput &generated, double tol)
{
    return quat_min_norm(cpp.desired_attitude, generated.desired_attitude) > tol ||
        quat_angle_error_rad(cpp.desired_attitude, generated.desired_attitude) > tol ||
        std::fabs(cpp.normalized_thrust - generated.normalized_thrust) > tol ||
        std::fabs(cpp.collective_thrust_n - generated.collective_thrust_n) > tol ||
        absmax3(diff3(cpp.position_error, generated.position_error)) > tol ||
        absmax3(diff3(cpp.velocity_error, generated.velocity_error)) > tol ||
        absmax3(diff3(cpp.desired_acceleration, generated.desired_acceleration)) > tol ||
        absmax3(diff3(cpp.desired_force_n, generated.desired_force_n)) > tol ||
        cpp.saturated != generated.saturated ||
        cpp.status_code != generated.status_code;
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
    params.integral_limit[0] = 0.5;
    params.integral_limit[1] = 0.5;
    params.integral_limit[2] = 0.3;
    params.mass = 0.67;
    params.gravity = 9.8;
    params.hover_percentage = 0.294;
    params.min_normalized_thrust = 0.0;
    params.max_normalized_thrust = 0.62;
    params.tilt_limit_rad = 0.35;

    CoreState cpp_state;
    mosim_px4ctrl::reset_thrust_mapping(params, cpp_state);
    Init();

    const auto cases = build_cases();
    DiffStats stats;

    for (const auto &c : cases)
    {
        const ControllerOutput cpp = mosim_px4ctrl::calculate_official_pid_core(params, cpp_state, c.input);

        set_generated_input(params, c.input);
        Step();
        const ControllerOutput generated = get_generated_output();
        update_stats(stats, cpp, generated);

        if (failed_case(cpp, generated, tol))
        {
            stats.failures += 1;
            std::cerr << "FAILED_CASE " << c.name
                      << " quat_norm=" << quat_min_norm(cpp.desired_attitude, generated.desired_attitude)
                      << " quat_angle=" << quat_angle_error_rad(cpp.desired_attitude, generated.desired_attitude)
                      << " thrust=" << std::fabs(cpp.normalized_thrust - generated.normalized_thrust)
                      << " status=" << std::fabs(static_cast<double>(cpp.status_code - generated.status_code))
                      << "\n";
        }
    }

    std::cout << std::setprecision(17);
    std::cout << "{\n";
    std::cout << "  \"schema\": \"mosim.px4ctrl_g9a_generated_c_gate.v1\",\n";
    std::cout << "  \"status\": \"" << (stats.failures == 0 ? "passed" : "failed") << "\",\n";
    std::cout << "  \"case_count\": " << cases.size() << ",\n";
    std::cout << "  \"failure_count\": " << stats.failures << ",\n";
    std::cout << "  \"tolerance\": " << tol << ",\n";
    std::cout << "  \"max_quat_min_norm\": " << stats.max_quat_norm << ",\n";
    std::cout << "  \"max_quat_angle_rad\": " << stats.max_quat_angle_rad << ",\n";
    std::cout << "  \"max_normalized_thrust_abs_diff\": " << stats.max_norm_thrust << ",\n";
    std::cout << "  \"max_collective_thrust_n_abs_diff\": " << stats.max_collective_thrust_n << ",\n";
    std::cout << "  \"max_position_error_abs_diff\": " << stats.max_position_error << ",\n";
    std::cout << "  \"max_velocity_error_abs_diff\": " << stats.max_velocity_error << ",\n";
    std::cout << "  \"max_desired_acc_abs_diff\": " << stats.max_acc << ",\n";
    std::cout << "  \"max_desired_force_n_abs_diff\": " << stats.max_force_n << ",\n";
    std::cout << "  \"max_saturated_abs_diff\": " << stats.max_saturated << ",\n";
    std::cout << "  \"max_status_code_abs_diff\": " << stats.max_status_code << "\n";
    std::cout << "}\n";

    return stats.failures == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
