#include "px4ctrl_core.h"

extern "C" {
#include "PX4CTRL_Core_CFunction_Sysblock_private.h"
void Init(void);
void Step(void);
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

constexpr int kIgnoreRollRate = 1;
constexpr int kIgnorePitchRate = 2;
constexpr int kIgnoreYawRate = 4;
constexpr int kExpectedAttitudeTypeMask = kIgnoreRollRate | kIgnorePitchRate | kIgnoreYawRate;
constexpr double kTol = 1.0e-12;
constexpr double kPi = 3.141592653589793238462643383279502884;

struct Case
{
    std::string name;
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
    int reset_input_count{0};
    int expected_reset_input_count{0};
    double max_quat_norm_diff{0.0};
    double max_quat_angle_rad{0.0};
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
        const double theta = i * 2.0 * kPi / 90.0;
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
        const double theta = i * 2.0 * kPi / 120.0;
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

class GeneratedCoreAttitudeAdapter
{
public:
    AttitudeThrustCommand step(const CoreParams &params, const ControllerInput &input)
    {
        const bool reset_this_cycle = reset_pending_ || input.reset;
        if (reset_this_cycle)
        {
            ++reset_input_count_;
        }
        reset_pending_ = false;

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
        lockGbIn.reset_in = reset_this_cycle ? 1.0 : 0.0;
        lockGbIn.kp_x_in = params.kp[0];
        lockGbIn.kp_y_in = params.kp[1];
        lockGbIn.kp_z_in = params.kp[2];
        lockGbIn.kv_x_in = params.kv[0];
        lockGbIn.kv_y_in = params.kv[1];
        lockGbIn.kv_z_in = params.kv[2];
        lockGbIn.mass_in = params.mass;
        lockGbIn.gravity_in = params.gravity;
        lockGbIn.hover_percentage_in = params.hover_percentage;

        Step();

        AttitudeThrustCommand command;
        command.type_mask = kExpectedAttitudeTypeMask;
        command.orientation = mosim_px4ctrl::normalize(Quat{
            blockGbOut.desired_attitude_w_out,
            blockGbOut.desired_attitude_x_out,
            blockGbOut.desired_attitude_y_out,
            blockGbOut.desired_attitude_z_out});
        command.body_rate = Vec3{0.0, 0.0, 0.0};
        command.thrust = blockGbOut.normalized_thrust_out;
        command.status_code = static_cast<int>(blockGbOut.status_code_out);
        return command;
    }

    int reset_input_count() const
    {
        return reset_input_count_;
    }

private:
    bool reset_pending_{true};
    int reset_input_count_{0};
};

int expected_reset_count_for_cases(const std::vector<Case> &cases)
{
    int count = 0;
    bool reset_pending = true;
    for (const auto &c : cases)
    {
        const bool reset_this_cycle = reset_pending || c.input.reset;
        if (reset_this_cycle)
        {
            ++count;
        }
        reset_pending = false;
    }
    return count;
}

} // namespace

int main()
{
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

    CoreState cpp_state;
    mosim_px4ctrl::reset_thrust_mapping(params, cpp_state);

    GeneratedCoreAttitudeAdapter adapter;
    Init();

    Stats stats;
    const auto cases = build_cases();
    stats.expected_reset_input_count = expected_reset_count_for_cases(cases);

    for (const auto &c : cases)
    {
        ControllerInput core_input = c.input;
        core_input.reset = (adapter.reset_input_count() == 0) || c.input.reset;
        const ControllerOutput expected = mosim_px4ctrl::calculate_px4ctrl_core(params, cpp_state, core_input);
        const AttitudeThrustCommand command = adapter.step(params, c.input);

        const double quat_norm_diff = quat_min_norm(expected.desired_attitude, command.orientation);
        const double quat_angle_rad = quat_angle_error_rad(expected.desired_attitude, command.orientation);
        const double thrust_abs_diff = std::fabs(expected.normalized_thrust - command.thrust);
        const double body_rate_abs = absmax3(command.body_rate);
        const double status_abs_diff = std::fabs(static_cast<double>(expected.status_code - command.status_code));

        stats.max_quat_norm_diff = std::max(stats.max_quat_norm_diff, quat_norm_diff);
        stats.max_quat_angle_rad = std::max(stats.max_quat_angle_rad, quat_angle_rad);
        stats.max_thrust_abs_diff = std::max(stats.max_thrust_abs_diff, thrust_abs_diff);
        stats.max_body_rate_abs = std::max(stats.max_body_rate_abs, body_rate_abs);
        stats.max_status_code_abs_diff = std::max(stats.max_status_code_abs_diff, status_abs_diff);

        const bool command_ok =
            command.type_mask == kExpectedAttitudeTypeMask &&
            quat_norm_diff <= kTol &&
            quat_angle_rad <= kTol &&
            thrust_abs_diff <= kTol &&
            body_rate_abs <= kTol &&
            status_abs_diff <= kTol;
        if (!command_ok)
        {
            ++stats.failures;
            std::cerr << "FAILED_CASE " << c.name
                      << " type_mask=" << command.type_mask
                      << " quat_norm_diff=" << quat_norm_diff
                      << " quat_angle_rad=" << quat_angle_rad
                      << " thrust_abs_diff=" << thrust_abs_diff
                      << " body_rate_abs=" << body_rate_abs
                      << " status_abs_diff=" << status_abs_diff << "\n";
        }
    }

    stats.reset_input_count = adapter.reset_input_count();
    if (stats.reset_input_count != stats.expected_reset_input_count)
    {
        ++stats.failures;
        std::cerr << "RESET_POLICY_FAILED actual=" << stats.reset_input_count
                  << " expected=" << stats.expected_reset_input_count << "\n";
    }
    if (stats.reset_input_count >= static_cast<int>(cases.size()))
    {
        ++stats.failures;
        std::cerr << "RESET_POLICY_FAILED reset asserted every cycle\n";
    }

    std::cout << std::setprecision(17);
    std::cout << "{\n";
    std::cout << "  \"schema\": \"mosim.px4ctrl_g7a_ros_sunray_adapter_gate.v1\",\n";
    std::cout << "  \"status\": \"" << (stats.failures == 0 ? "passed" : "failed") << "\",\n";
    std::cout << "  \"claim_boundary\": \"Static adapter gate only. It proves generated C can produce the attitude plus normalized-thrust command shape used by px4ctrl/Sunray; no ROS, Gazebo, PX4, MAVROS, or flight runtime is executed.\",\n";
    std::cout << "  \"case_count\": " << cases.size() << ",\n";
    std::cout << "  \"failure_count\": " << stats.failures << ",\n";
    std::cout << "  \"attitude_target_type_mask\": " << kExpectedAttitudeTypeMask << ",\n";
    std::cout << "  \"reset_input_count\": " << stats.reset_input_count << ",\n";
    std::cout << "  \"expected_reset_input_count\": " << stats.expected_reset_input_count << ",\n";
    std::cout << "  \"max_quat_norm_diff\": " << stats.max_quat_norm_diff << ",\n";
    std::cout << "  \"max_quat_angle_rad\": " << stats.max_quat_angle_rad << ",\n";
    std::cout << "  \"max_thrust_abs_diff\": " << stats.max_thrust_abs_diff << ",\n";
    std::cout << "  \"max_body_rate_abs\": " << stats.max_body_rate_abs << ",\n";
    std::cout << "  \"max_status_code_abs_diff\": " << stats.max_status_code_abs_diff << "\n";
    std::cout << "}\n";

    return stats.failures == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
