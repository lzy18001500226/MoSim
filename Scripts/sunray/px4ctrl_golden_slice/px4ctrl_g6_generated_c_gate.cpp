#include "px4ctrl_core.h"
#include "px4ctrl_core_c.h"

extern "C" {
#include "PX4CTRL_Core_CFunction_Sysblock_private.h"
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
    double max_ref_cpp{0.0};
    double max_cpp_c{0.0};
    double max_cpp_generated{0.0};
    double max_quat_angle_generated_rad{0.0};
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

double output_max_abs_diff(const ControllerOutput &a, const ControllerOutput &b)
{
    double out = 0.0;
    out = std::max(out, quat_min_norm(a.desired_attitude, b.desired_attitude));
    out = std::max(out, std::fabs(a.normalized_thrust - b.normalized_thrust));
    out = std::max(out, std::fabs(a.collective_thrust_n - b.collective_thrust_n));
    out = std::max(out, absmax3(diff3(a.position_error, b.position_error)));
    out = std::max(out, absmax3(diff3(a.velocity_error, b.velocity_error)));
    out = std::max(out, absmax3(diff3(a.desired_acceleration, b.desired_acceleration)));
    out = std::max(out, absmax3(diff3(a.desired_force_n, b.desired_force_n)));
    out = std::max(out, std::fabs(static_cast<double>(a.status_code - b.status_code)));
    return out;
}

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
        input.reference_acceleration.z + params.kv[2] * out.velocity_error.z + params.kp[2] * out.position_error.z + params.gravity,
    };
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
        in.velocity = Vec3{0.8 * std::cos(theta - 0.05), 0.8 * std::cos(2.0 * theta - 0.1), 0.0};
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

MosimPx4ctrlCoreCParams to_c_params(const CoreParams &params)
{
    return MosimPx4ctrlCoreCParams{
        params.kp[0], params.kp[1], params.kp[2],
        params.kv[0], params.kv[1], params.kv[2],
        params.mass, params.gravity, params.hover_percentage};
}

MosimPx4ctrlCoreCInput to_c_input(const ControllerInput &input)
{
    MosimPx4ctrlCoreCInput out{};
    out.dt = input.dt;
    out.position = {input.position.x, input.position.y, input.position.z};
    out.velocity = {input.velocity.x, input.velocity.y, input.velocity.z};
    out.attitude = {input.attitude.w, input.attitude.x, input.attitude.y, input.attitude.z};
    out.angular_velocity = {input.angular_velocity.x, input.angular_velocity.y, input.angular_velocity.z};
    out.reference_position = {input.reference_position.x, input.reference_position.y, input.reference_position.z};
    out.reference_velocity = {input.reference_velocity.x, input.reference_velocity.y, input.reference_velocity.z};
    out.reference_acceleration = {input.reference_acceleration.x, input.reference_acceleration.y, input.reference_acceleration.z};
    out.reference_yaw = input.reference_yaw;
    out.reference_yaw_rate = input.reference_yaw_rate;
    out.imu_attitude = {input.imu_attitude.w, input.imu_attitude.x, input.imu_attitude.y, input.imu_attitude.z};
    out.imu_angular_velocity = {input.imu_angular_velocity.x, input.imu_angular_velocity.y, input.imu_angular_velocity.z};
    out.enable = input.enable ? 1 : 0;
    out.reset = input.reset ? 1 : 0;
    return out;
}

ControllerOutput from_c_output(const MosimPx4ctrlCoreCOutput &input)
{
    ControllerOutput out;
    out.desired_attitude = Quat{input.desired_attitude.w, input.desired_attitude.x, input.desired_attitude.y, input.desired_attitude.z};
    out.normalized_thrust = input.normalized_thrust;
    out.collective_thrust_n = input.collective_thrust_n;
    out.position_error = Vec3{input.position_error.x, input.position_error.y, input.position_error.z};
    out.velocity_error = Vec3{input.velocity_error.x, input.velocity_error.y, input.velocity_error.z};
    out.desired_acceleration = Vec3{input.desired_acceleration.x, input.desired_acceleration.y, input.desired_acceleration.z};
    out.desired_force_n = Vec3{input.desired_force_n.x, input.desired_force_n.y, input.desired_force_n.z};
    out.status_code = input.status_code;
    return out;
}

void set_generated_input(const CoreParams &params, const ControllerInput &input)
{
    lockGbIn.dt_in = input.dt;
    lockGbIn.position_x_in = input.position.x;
    lockGbIn.position_y_in = input.position.y;
    lockGbIn.position_z_in = input.position.z;
    lockGbIn.velocity_x_in = input.velocity.x;
    lockGbIn.velocity_y_in = input.velocity.y;
    lockGbIn.velocity_z_in = input.velocity.z;
    lockGbIn.attitude_w_in = input.attitude.w;
    lockGbIn.attitude_x_in = input.attitude.x;
    lockGbIn.attitude_y_in = input.attitude.y;
    lockGbIn.attitude_z_in = input.attitude.z;
    lockGbIn.angular_velocity_x_in = input.angular_velocity.x;
    lockGbIn.angular_velocity_y_in = input.angular_velocity.y;
    lockGbIn.angular_velocity_z_in = input.angular_velocity.z;
    lockGbIn.reference_position_x_in = input.reference_position.x;
    lockGbIn.reference_position_y_in = input.reference_position.y;
    lockGbIn.reference_position_z_in = input.reference_position.z;
    lockGbIn.reference_velocity_x_in = input.reference_velocity.x;
    lockGbIn.reference_velocity_y_in = input.reference_velocity.y;
    lockGbIn.reference_velocity_z_in = input.reference_velocity.z;
    lockGbIn.reference_acceleration_x_in = input.reference_acceleration.x;
    lockGbIn.reference_acceleration_y_in = input.reference_acceleration.y;
    lockGbIn.reference_acceleration_z_in = input.reference_acceleration.z;
    lockGbIn.reference_yaw_in = input.reference_yaw;
    lockGbIn.reference_yaw_rate_in = input.reference_yaw_rate;
    lockGbIn.imu_attitude_w_in = input.imu_attitude.w;
    lockGbIn.imu_attitude_x_in = input.imu_attitude.x;
    lockGbIn.imu_attitude_y_in = input.imu_attitude.y;
    lockGbIn.imu_attitude_z_in = input.imu_attitude.z;
    lockGbIn.imu_angular_velocity_x_in = input.imu_angular_velocity.x;
    lockGbIn.imu_angular_velocity_y_in = input.imu_angular_velocity.y;
    lockGbIn.imu_angular_velocity_z_in = input.imu_angular_velocity.z;
    lockGbIn.enable_in = input.enable ? 1.0 : 0.0;
    lockGbIn.reset_in = input.reset ? 1.0 : 0.0;
    lockGbIn.kp_x_in = params.kp[0];
    lockGbIn.kp_y_in = params.kp[1];
    lockGbIn.kp_z_in = params.kp[2];
    lockGbIn.kv_x_in = params.kv[0];
    lockGbIn.kv_y_in = params.kv[1];
    lockGbIn.kv_z_in = params.kv[2];
    lockGbIn.mass_in = params.mass;
    lockGbIn.gravity_in = params.gravity;
    lockGbIn.hover_percentage_in = params.hover_percentage;
}

ControllerOutput get_generated_output()
{
    ControllerOutput out;
    out.desired_attitude = Quat{blockGbOut.desired_attitude_w_out, blockGbOut.desired_attitude_x_out, blockGbOut.desired_attitude_y_out, blockGbOut.desired_attitude_z_out};
    out.normalized_thrust = blockGbOut.normalized_thrust_out;
    out.collective_thrust_n = blockGbOut.collective_thrust_N_out;
    out.position_error = Vec3{blockGbOut.position_error_x_out, blockGbOut.position_error_y_out, blockGbOut.position_error_z_out};
    out.velocity_error = Vec3{blockGbOut.velocity_error_x_out, blockGbOut.velocity_error_y_out, blockGbOut.velocity_error_z_out};
    out.desired_acceleration = Vec3{blockGbOut.desired_acceleration_x_out, blockGbOut.desired_acceleration_y_out, blockGbOut.desired_acceleration_z_out};
    out.desired_force_n = Vec3{blockGbOut.desired_force_N_x_out, blockGbOut.desired_force_N_y_out, blockGbOut.desired_force_N_z_out};
    out.status_code = static_cast<int>(blockGbOut.status_code_out);
    return out;
}

} // namespace

int main()
{
    const double tol = 1.0e-12;
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
    CoreState cpp_state;
    mosim_px4ctrl::reset_thrust_mapping(params, ref_state);
    mosim_px4ctrl::reset_thrust_mapping(params, cpp_state);

    MosimPx4ctrlCoreCState c_state;
    const MosimPx4ctrlCoreCParams c_params = to_c_params(params);
    mosim_px4ctrl_core_c_reset(&c_params, &c_state);
    Init();

    DiffStats stats;
    const auto cases = build_cases();
    for (const auto &c : cases)
    {
        const auto ref = upstream_reference_calculate(params, ref_state, c.input);
        const auto cpp = mosim_px4ctrl::calculate_px4ctrl_core(params, cpp_state, c.input);
        const MosimPx4ctrlCoreCInput c_input = to_c_input(c.input);
        MosimPx4ctrlCoreCOutput c_output;
        mosim_px4ctrl_core_c_step(&c_params, &c_state, &c_input, &c_output);
        const auto c_core = from_c_output(c_output);

        set_generated_input(params, c.input);
        Step();
        const auto generated = get_generated_output();

        const double ref_cpp = output_max_abs_diff(ref, cpp);
        const double cpp_c = output_max_abs_diff(cpp, c_core);
        const double cpp_generated = output_max_abs_diff(cpp, generated);
        stats.max_ref_cpp = std::max(stats.max_ref_cpp, ref_cpp);
        stats.max_cpp_c = std::max(stats.max_cpp_c, cpp_c);
        stats.max_cpp_generated = std::max(stats.max_cpp_generated, cpp_generated);
        stats.max_quat_angle_generated_rad = std::max(stats.max_quat_angle_generated_rad, quat_angle_error_rad(cpp.desired_attitude, generated.desired_attitude));

        if (ref_cpp > tol || cpp_c > tol || cpp_generated > tol || quat_angle_error_rad(cpp.desired_attitude, generated.desired_attitude) > tol)
        {
            stats.failures += 1;
            std::cerr << "FAILED_CASE " << c.name
                      << " ref_cpp=" << ref_cpp
                      << " cpp_c=" << cpp_c
                      << " cpp_generated=" << cpp_generated
                      << "\n";
        }
    }

    std::cout << std::setprecision(17);
    std::cout << "{\n";
    std::cout << "  \"schema\": \"mosim.px4ctrl_g6_generated_c_gate.v1\",\n";
    std::cout << "  \"status\": \"" << (stats.failures == 0 ? "passed" : "failed") << "\",\n";
    std::cout << "  \"case_count\": " << cases.size() << ",\n";
    std::cout << "  \"failure_count\": " << stats.failures << ",\n";
    std::cout << "  \"max_ref_vs_cpp_abs_diff\": " << stats.max_ref_cpp << ",\n";
    std::cout << "  \"max_cpp_vs_c_abi_abs_diff\": " << stats.max_cpp_c << ",\n";
    std::cout << "  \"max_cpp_vs_mworks_generated_c_abs_diff\": " << stats.max_cpp_generated << ",\n";
    std::cout << "  \"max_cpp_vs_mworks_generated_c_quat_angle_rad\": " << stats.max_quat_angle_generated_rad << "\n";
    std::cout << "}\n";

    return stats.failures == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
