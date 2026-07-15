#include "px4ctrl_g9a_core_c.h"

#include <math.h>
#include <string.h>

static double c_clamp(double value, double lower, double upper)
{
    if (value < lower)
    {
        return lower;
    }
    if (value > upper)
    {
        return upper;
    }
    return value;
}

static MosimPx4ctrlG9ACVec3 c_vec3(double x, double y, double z)
{
    MosimPx4ctrlG9ACVec3 v;
    v.x = x;
    v.y = y;
    v.z = z;
    return v;
}

static MosimPx4ctrlG9ACVec3 c_clamp_vec3(
    MosimPx4ctrlG9ACVec3 value,
    double limit_x,
    double limit_y,
    double limit_z)
{
    return c_vec3(
        c_clamp(value.x, -limit_x, limit_x),
        c_clamp(value.y, -limit_y, limit_y),
        c_clamp(value.z, -limit_z, limit_z));
}

static MosimPx4ctrlG9ACQuat c_quat(double w, double x, double y, double z)
{
    MosimPx4ctrlG9ACQuat q;
    q.w = w;
    q.x = x;
    q.y = y;
    q.z = z;
    return q;
}

static MosimPx4ctrlG9ACQuat c_normalize(MosimPx4ctrlG9ACQuat q)
{
    const double n = sqrt(q.w * q.w + q.x * q.x + q.y * q.y + q.z * q.z);
    if (n <= 0.0)
    {
        return c_quat(1.0, 0.0, 0.0, 0.0);
    }
    return c_quat(q.w / n, q.x / n, q.y / n, q.z / n);
}

static MosimPx4ctrlG9ACQuat c_conjugate(MosimPx4ctrlG9ACQuat q)
{
    return c_quat(q.w, -q.x, -q.y, -q.z);
}

static MosimPx4ctrlG9ACQuat c_multiply(MosimPx4ctrlG9ACQuat a, MosimPx4ctrlG9ACQuat b)
{
    return c_normalize(c_quat(
        a.w * b.w - a.x * b.x - a.y * b.y - a.z * b.z,
        a.w * b.x + a.x * b.w + a.y * b.z - a.z * b.y,
        a.w * b.y - a.x * b.z + a.y * b.w + a.z * b.x,
        a.w * b.z + a.x * b.y - a.y * b.x + a.z * b.w));
}

static MosimPx4ctrlG9ACQuat c_inverse(MosimPx4ctrlG9ACQuat q)
{
    return c_conjugate(c_normalize(q));
}

static MosimPx4ctrlG9ACQuat c_angle_axis(double angle, MosimPx4ctrlG9ACVec3 axis)
{
    const double half = 0.5 * angle;
    const double s = sin(half);
    return c_normalize(c_quat(cos(half), axis.x * s, axis.y * s, axis.z * s));
}

static double c_yaw_from_quat(MosimPx4ctrlG9ACQuat q_raw)
{
    const MosimPx4ctrlG9ACQuat q = c_normalize(q_raw);
    return atan2(
        2.0 * (q.x * q.y + q.w * q.z),
        q.w * q.w + q.x * q.x - q.y * q.y - q.z * q.z);
}

void mosim_px4ctrl_g9a_c_reset(
    const MosimPx4ctrlG9ACParams *params,
    MosimPx4ctrlG9ACState *state)
{
    state->thr2acc = params->gravity / params->hover_percentage;
    state->covariance = 1.0e6;
    state->integral_position_error = c_vec3(0.0, 0.0, 0.0);
}

void mosim_px4ctrl_g9a_c_step(
    const MosimPx4ctrlG9ACParams *params,
    MosimPx4ctrlG9ACState *state,
    const MosimPx4ctrlG9ACInput *input,
    MosimPx4ctrlG9ACOutput *output)
{
    memset(output, 0, sizeof(*output));
    output->desired_attitude = c_quat(1.0, 0.0, 0.0, 0.0);

    if (input->reset)
    {
        mosim_px4ctrl_g9a_c_reset(params, state);
    }

    if (!input->enable)
    {
        output->status_code = 1;
        output->desired_attitude = c_normalize(input->imu_attitude);
        output->normalized_thrust = 0.0;
        output->collective_thrust_n = 0.0;
        return;
    }

    output->position_error = c_vec3(
        input->reference_position.x - input->position.x,
        input->reference_position.y - input->position.y,
        input->reference_position.z - input->position.z);
    output->velocity_error = c_vec3(
        input->reference_velocity.x - input->velocity.x,
        input->reference_velocity.y - input->velocity.y,
        input->reference_velocity.z - input->velocity.z);

    {
        const double dt = input->dt > 0.0 ? input->dt : 0.01;
        state->integral_position_error = c_clamp_vec3(
            c_vec3(
                state->integral_position_error.x + output->position_error.x * dt,
                state->integral_position_error.y + output->position_error.y * dt,
                state->integral_position_error.z + output->position_error.z * dt),
            params->integral_limit_x,
            params->integral_limit_y,
            params->integral_limit_z);
    }

    output->desired_acceleration = c_vec3(
        input->reference_acceleration.x + params->kv_x * output->velocity_error.x + params->kp_x * output->position_error.x + params->ki_x * state->integral_position_error.x,
        input->reference_acceleration.y + params->kv_y * output->velocity_error.y + params->kp_y * output->position_error.y + params->ki_y * state->integral_position_error.y,
        input->reference_acceleration.z + params->kv_z * output->velocity_error.z + params->kp_z * output->position_error.z + params->ki_z * state->integral_position_error.z + params->gravity);

    {
        const double unclamped_normalized_thrust = output->desired_acceleration.z / state->thr2acc;
        output->normalized_thrust = c_clamp(
            unclamped_normalized_thrust,
            params->min_normalized_thrust,
            params->max_normalized_thrust);
        if (fabs(output->normalized_thrust - unclamped_normalized_thrust) > 1.0e-12)
        {
            output->saturated = 1.0;
        }
    }

    output->collective_thrust_n =
        output->normalized_thrust * (params->mass * params->gravity / params->hover_percentage);
    output->desired_force_n = c_vec3(
        params->mass * output->desired_acceleration.x,
        params->mass * output->desired_acceleration.y,
        params->mass * output->desired_acceleration.z);

    {
        const double yaw_odom = c_yaw_from_quat(input->attitude);
        const double sin_yaw = sin(yaw_odom);
        const double cos_yaw = cos(yaw_odom);
        double roll = (output->desired_acceleration.x * sin_yaw - output->desired_acceleration.y * cos_yaw) / params->gravity;
        double pitch = (output->desired_acceleration.x * cos_yaw + output->desired_acceleration.y * sin_yaw) / params->gravity;

        const double unclamped_roll = roll;
        const double unclamped_pitch = pitch;
        roll = c_clamp(roll, -params->tilt_limit_rad, params->tilt_limit_rad);
        pitch = c_clamp(pitch, -params->tilt_limit_rad, params->tilt_limit_rad);
        if (fabs(roll - unclamped_roll) > 1.0e-12 ||
            fabs(pitch - unclamped_pitch) > 1.0e-12)
        {
            output->saturated = 1.0;
        }

        {
            const MosimPx4ctrlG9ACQuat q_yaw = c_angle_axis(input->reference_yaw, c_vec3(0.0, 0.0, 1.0));
            const MosimPx4ctrlG9ACQuat q_pitch = c_angle_axis(pitch, c_vec3(0.0, 1.0, 0.0));
            const MosimPx4ctrlG9ACQuat q_roll = c_angle_axis(roll, c_vec3(1.0, 0.0, 0.0));
            const MosimPx4ctrlG9ACQuat q_des_world = c_multiply(c_multiply(q_yaw, q_pitch), q_roll);
            output->desired_attitude =
                c_multiply(c_multiply(input->imu_attitude, c_inverse(input->attitude)), q_des_world);
        }
    }
}

void MosimPx4ctrlG9AOfficialPidCStepScalar(
    double dt,
    double position_x,
    double position_y,
    double position_z,
    double velocity_x,
    double velocity_y,
    double velocity_z,
    double attitude_w,
    double attitude_x,
    double attitude_y,
    double attitude_z,
    double angular_velocity_x,
    double angular_velocity_y,
    double angular_velocity_z,
    double reference_position_x,
    double reference_position_y,
    double reference_position_z,
    double reference_velocity_x,
    double reference_velocity_y,
    double reference_velocity_z,
    double reference_acceleration_x,
    double reference_acceleration_y,
    double reference_acceleration_z,
    double reference_yaw,
    double reference_yaw_rate,
    double imu_attitude_w,
    double imu_attitude_x,
    double imu_attitude_y,
    double imu_attitude_z,
    double imu_angular_velocity_x,
    double imu_angular_velocity_y,
    double imu_angular_velocity_z,
    double enable,
    double reset,
    double kp_x,
    double kp_y,
    double kp_z,
    double kv_x,
    double kv_y,
    double kv_z,
    double ki_x,
    double ki_y,
    double ki_z,
    double integral_limit_x,
    double integral_limit_y,
    double integral_limit_z,
    double mass,
    double gravity,
    double hover_percentage,
    double min_normalized_thrust,
    double max_normalized_thrust,
    double tilt_limit_rad,
    double *desired_attitude_w,
    double *desired_attitude_x,
    double *desired_attitude_y,
    double *desired_attitude_z,
    double *normalized_thrust,
    double *collective_thrust_N,
    double *position_error_x,
    double *position_error_y,
    double *position_error_z,
    double *velocity_error_x,
    double *velocity_error_y,
    double *velocity_error_z,
    double *desired_acceleration_x,
    double *desired_acceleration_y,
    double *desired_acceleration_z,
    double *desired_force_N_x,
    double *desired_force_N_y,
    double *desired_force_N_z,
    double *saturated,
    double *status_code)
{
    static MosimPx4ctrlG9ACState state = {0.0, 0.0, {0.0, 0.0, 0.0}};
    static int initialized = 0;

    MosimPx4ctrlG9ACParams params;
    MosimPx4ctrlG9ACInput input;
    MosimPx4ctrlG9ACOutput output;

    params.kp_x = kp_x;
    params.kp_y = kp_y;
    params.kp_z = kp_z;
    params.kv_x = kv_x;
    params.kv_y = kv_y;
    params.kv_z = kv_z;
    params.ki_x = ki_x;
    params.ki_y = ki_y;
    params.ki_z = ki_z;
    params.integral_limit_x = integral_limit_x;
    params.integral_limit_y = integral_limit_y;
    params.integral_limit_z = integral_limit_z;
    params.mass = mass;
    params.gravity = gravity;
    params.hover_percentage = hover_percentage;
    params.min_normalized_thrust = min_normalized_thrust;
    params.max_normalized_thrust = max_normalized_thrust;
    params.tilt_limit_rad = tilt_limit_rad;

    if (!initialized)
    {
        mosim_px4ctrl_g9a_c_reset(&params, &state);
        initialized = 1;
    }

    input.dt = dt;
    input.position = c_vec3(position_x, position_y, position_z);
    input.velocity = c_vec3(velocity_x, velocity_y, velocity_z);
    input.attitude = c_quat(attitude_w, attitude_x, attitude_y, attitude_z);
    input.angular_velocity = c_vec3(angular_velocity_x, angular_velocity_y, angular_velocity_z);
    input.reference_position = c_vec3(reference_position_x, reference_position_y, reference_position_z);
    input.reference_velocity = c_vec3(reference_velocity_x, reference_velocity_y, reference_velocity_z);
    input.reference_acceleration = c_vec3(reference_acceleration_x, reference_acceleration_y, reference_acceleration_z);
    input.reference_yaw = reference_yaw;
    input.reference_yaw_rate = reference_yaw_rate;
    input.imu_attitude = c_quat(imu_attitude_w, imu_attitude_x, imu_attitude_y, imu_attitude_z);
    input.imu_angular_velocity = c_vec3(imu_angular_velocity_x, imu_angular_velocity_y, imu_angular_velocity_z);
    input.enable = enable != 0.0;
    input.reset = reset != 0.0;

    mosim_px4ctrl_g9a_c_step(&params, &state, &input, &output);

    *desired_attitude_w = output.desired_attitude.w;
    *desired_attitude_x = output.desired_attitude.x;
    *desired_attitude_y = output.desired_attitude.y;
    *desired_attitude_z = output.desired_attitude.z;
    *normalized_thrust = output.normalized_thrust;
    *collective_thrust_N = output.collective_thrust_n;
    *position_error_x = output.position_error.x;
    *position_error_y = output.position_error.y;
    *position_error_z = output.position_error.z;
    *velocity_error_x = output.velocity_error.x;
    *velocity_error_y = output.velocity_error.y;
    *velocity_error_z = output.velocity_error.z;
    *desired_acceleration_x = output.desired_acceleration.x;
    *desired_acceleration_y = output.desired_acceleration.y;
    *desired_acceleration_z = output.desired_acceleration.z;
    *desired_force_N_x = output.desired_force_n.x;
    *desired_force_N_y = output.desired_force_n.y;
    *desired_force_N_z = output.desired_force_n.z;
    *saturated = output.saturated;
    *status_code = (double)output.status_code;
}
