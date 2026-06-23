#include "px4ctrl_core.h"

namespace mosim_px4ctrl
{

ControllerOutput calculate_px4ctrl_core(
    const CoreParams &params,
    CoreState &state,
    const ControllerInput &input)
{
    if (input.reset)
    {
        reset_thrust_mapping(params, state);
    }

    ControllerOutput out;

    if (!input.enable)
    {
        out.status_code = 1;
        out.status_text = "disabled";
        out.desired_attitude = normalize(input.imu_attitude);
        out.normalized_thrust = 0.0;
        out.collective_thrust_n = 0.0;
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
    const double full_thrust_n = params.mass * params.gravity / params.hover_percentage;
    out.collective_thrust_n = out.normalized_thrust * full_thrust_n;

    out.desired_force_n = Vec3{
        params.mass * out.desired_acceleration.x,
        params.mass * out.desired_acceleration.y,
        params.mass * out.desired_acceleration.z,
    };

    const double yaw_odom = yaw_from_quat(input.attitude);
    const double sin_yaw = std::sin(yaw_odom);
    const double cos_yaw = std::cos(yaw_odom);

    const double roll = (out.desired_acceleration.x * sin_yaw - out.desired_acceleration.y * cos_yaw) / params.gravity;
    const double pitch = (out.desired_acceleration.x * cos_yaw + out.desired_acceleration.y * sin_yaw) / params.gravity;

    const Quat q_yaw = angle_axis(input.reference_yaw, Vec3{0.0, 0.0, 1.0});
    const Quat q_pitch = angle_axis(pitch, Vec3{0.0, 1.0, 0.0});
    const Quat q_roll = angle_axis(roll, Vec3{1.0, 0.0, 0.0});
    const Quat q_des_world = multiply(multiply(q_yaw, q_pitch), q_roll);

    out.desired_attitude = multiply(multiply(input.imu_attitude, inverse(input.attitude)), q_des_world);
    return out;
}

} // namespace mosim_px4ctrl
