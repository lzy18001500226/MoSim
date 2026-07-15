#include "px4ctrl_g9_family_core_c.h"

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

static double c_sat(double value)
{
    return c_clamp(value, -1.0, 1.0);
}

static double c_safe_positive(double value, double fallback)
{
    return value > 1.0e-9 ? value : fallback;
}

static double c_safe_nonnegative(double value)
{
    return value > 0.0 ? value : 0.0;
}

static int c_vec3_components_equal(
    MosimPx4ctrlG9FamilyCVec3 a,
    MosimPx4ctrlG9FamilyCVec3 b)
{
    return fabs(a.x - b.x) <= 1.0e-12 &&
        fabs(a.y - b.y) <= 1.0e-12 &&
        fabs(a.z - b.z) <= 1.0e-12;
}

static MosimPx4ctrlG9FamilyCVec3 c_vec3(double x, double y, double z)
{
    MosimPx4ctrlG9FamilyCVec3 v;
    v.x = x;
    v.y = y;
    v.z = z;
    return v;
}

static MosimPx4ctrlG9FamilyCQuat c_quat(double w, double x, double y, double z)
{
    MosimPx4ctrlG9FamilyCQuat q;
    q.w = w;
    q.x = x;
    q.y = y;
    q.z = z;
    return q;
}

static MosimPx4ctrlG9FamilyCVec3 c_add(
    MosimPx4ctrlG9FamilyCVec3 a,
    MosimPx4ctrlG9FamilyCVec3 b)
{
    return c_vec3(a.x + b.x, a.y + b.y, a.z + b.z);
}

static MosimPx4ctrlG9FamilyCVec3 c_subtract(
    MosimPx4ctrlG9FamilyCVec3 a,
    MosimPx4ctrlG9FamilyCVec3 b)
{
    return c_vec3(a.x - b.x, a.y - b.y, a.z - b.z);
}

static MosimPx4ctrlG9FamilyCVec3 c_scale(
    MosimPx4ctrlG9FamilyCVec3 v,
    double s)
{
    return c_vec3(v.x * s, v.y * s, v.z * s);
}

static double c_dot(
    MosimPx4ctrlG9FamilyCVec3 a,
    MosimPx4ctrlG9FamilyCVec3 b)
{
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

static MosimPx4ctrlG9FamilyCVec3 c_cross(
    MosimPx4ctrlG9FamilyCVec3 a,
    MosimPx4ctrlG9FamilyCVec3 b)
{
    return c_vec3(
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x);
}

static double c_norm(MosimPx4ctrlG9FamilyCVec3 v)
{
    return sqrt(c_dot(v, v));
}

static MosimPx4ctrlG9FamilyCVec3 c_clamp_vec3(
    MosimPx4ctrlG9FamilyCVec3 value,
    const double limit[3])
{
    return c_vec3(
        c_clamp(value.x, -limit[0], limit[0]),
        c_clamp(value.y, -limit[1], limit[1]),
        c_clamp(value.z, -limit[2], limit[2]));
}

static MosimPx4ctrlG9FamilyCVec3 c_clamp_delta_vec3(
    MosimPx4ctrlG9FamilyCVec3 value,
    MosimPx4ctrlG9FamilyCVec3 previous,
    const double limit[3])
{
    const MosimPx4ctrlG9FamilyCVec3 delta =
        c_clamp_vec3(c_subtract(value, previous), limit);
    return c_add(previous, delta);
}

static MosimPx4ctrlG9FamilyCVec3 c_normalize_vec3(
    MosimPx4ctrlG9FamilyCVec3 v,
    MosimPx4ctrlG9FamilyCVec3 fallback)
{
    const double n = c_norm(v);
    if (n <= 1.0e-12)
    {
        return fallback;
    }
    return c_scale(v, 1.0 / n);
}

static MosimPx4ctrlG9FamilyCQuat c_normalize_quat(MosimPx4ctrlG9FamilyCQuat q)
{
    const double n = sqrt(q.w * q.w + q.x * q.x + q.y * q.y + q.z * q.z);
    if (n <= 0.0)
    {
        return c_quat(1.0, 0.0, 0.0, 0.0);
    }
    return c_quat(q.w / n, q.x / n, q.y / n, q.z / n);
}

static MosimPx4ctrlG9FamilyCQuat c_conjugate(MosimPx4ctrlG9FamilyCQuat q)
{
    return c_quat(q.w, -q.x, -q.y, -q.z);
}

static MosimPx4ctrlG9FamilyCQuat c_multiply(
    MosimPx4ctrlG9FamilyCQuat a,
    MosimPx4ctrlG9FamilyCQuat b)
{
    return c_normalize_quat(c_quat(
        a.w * b.w - a.x * b.x - a.y * b.y - a.z * b.z,
        a.w * b.x + a.x * b.w + a.y * b.z - a.z * b.y,
        a.w * b.y - a.x * b.z + a.y * b.w + a.z * b.x,
        a.w * b.z + a.x * b.y - a.y * b.x + a.z * b.w));
}

static MosimPx4ctrlG9FamilyCQuat c_inverse(MosimPx4ctrlG9FamilyCQuat q)
{
    return c_conjugate(c_normalize_quat(q));
}

static MosimPx4ctrlG9FamilyCQuat c_angle_axis(
    double angle,
    MosimPx4ctrlG9FamilyCVec3 axis)
{
    const double half = 0.5 * angle;
    const double s = sin(half);
    return c_normalize_quat(c_quat(cos(half), axis.x * s, axis.y * s, axis.z * s));
}

static double c_yaw_from_quat(MosimPx4ctrlG9FamilyCQuat q_raw)
{
    const MosimPx4ctrlG9FamilyCQuat q = c_normalize_quat(q_raw);
    return atan2(
        2.0 * (q.x * q.y + q.w * q.z),
        q.w * q.w + q.x * q.x - q.y * q.y - q.z * q.z);
}

static MosimPx4ctrlG9FamilyCQuat c_quat_from_rotation_matrix_columns(
    MosimPx4ctrlG9FamilyCVec3 b1,
    MosimPx4ctrlG9FamilyCVec3 b2,
    MosimPx4ctrlG9FamilyCVec3 b3)
{
    const double m00 = b1.x;
    const double m01 = b2.x;
    const double m02 = b3.x;
    const double m10 = b1.y;
    const double m11 = b2.y;
    const double m12 = b3.y;
    const double m20 = b1.z;
    const double m21 = b2.z;
    const double m22 = b3.z;
    const double trace = m00 + m11 + m22;

    if (trace > 0.0)
    {
        const double s = sqrt(trace + 1.0) * 2.0;
        return c_normalize_quat(c_quat(
            0.25 * s,
            (m21 - m12) / s,
            (m02 - m20) / s,
            (m10 - m01) / s));
    }
    if (m00 > m11 && m00 > m22)
    {
        const double s = sqrt(1.0 + m00 - m11 - m22) * 2.0;
        return c_normalize_quat(c_quat(
            (m21 - m12) / s,
            0.25 * s,
            (m01 + m10) / s,
            (m02 + m20) / s));
    }
    if (m11 > m22)
    {
        const double s = sqrt(1.0 + m11 - m00 - m22) * 2.0;
        return c_normalize_quat(c_quat(
            (m02 - m20) / s,
            (m01 + m10) / s,
            0.25 * s,
            (m12 + m21) / s));
    }
    {
        const double s = sqrt(1.0 + m22 - m00 - m11) * 2.0;
        return c_normalize_quat(c_quat(
            (m10 - m01) / s,
            (m02 + m20) / s,
            (m12 + m21) / s,
            0.25 * s));
    }
}

void mosim_px4ctrl_g9_family_c_reset(
    const MosimPx4ctrlG9FamilyCParams *params,
    MosimPx4ctrlG9FamilyCState *state)
{
    state->thr2acc = params->gravity / params->hover_percentage;
    state->covariance = 1.0e6;
    state->integral_position_error = c_vec3(0.0, 0.0, 0.0);
    state->previous_velocity = c_vec3(0.0, 0.0, 0.0);
    state->measured_acceleration_lpf = c_vec3(0.0, 0.0, 0.0);
    state->previous_command_acceleration = c_vec3(0.0, 0.0, 0.0);
    state->disturbance_estimate = c_vec3(0.0, 0.0, 0.0);
    state->previous_measurement_stamp_s = 0.0;
    state->has_previous_velocity = 0;
    state->has_previous_measurement_stamp = 0;
}

static MosimPx4ctrlG9FamilyCOutput c_disabled_output(
    const MosimPx4ctrlG9FamilyCInput *input)
{
    MosimPx4ctrlG9FamilyCOutput out;
    memset(&out, 0, sizeof(out));
    out.status_code = 1;
    out.desired_attitude = c_normalize_quat(input->imu_attitude);
    return out;
}

static MosimPx4ctrlG9FamilyCVec3 c_pid_acceleration_no_gravity(
    const MosimPx4ctrlG9FamilyCParams *params,
    MosimPx4ctrlG9FamilyCState *state,
    const MosimPx4ctrlG9FamilyCInput *input,
    MosimPx4ctrlG9FamilyCOutput *out)
{
    const double dt = input->dt > 0.0 ? input->dt : 0.01;
    out->position_error = c_subtract(input->reference_position, input->position);
    out->velocity_error = c_subtract(input->reference_velocity, input->velocity);
    state->integral_position_error = c_clamp_vec3(
        c_vec3(
            state->integral_position_error.x + out->position_error.x * dt,
            state->integral_position_error.y + out->position_error.y * dt,
            state->integral_position_error.z + out->position_error.z * dt),
        params->integral_limit);
    return c_vec3(
        input->reference_acceleration.x + params->kv[0] * out->velocity_error.x + params->kp[0] * out->position_error.x + params->ki[0] * state->integral_position_error.x,
        input->reference_acceleration.y + params->kv[1] * out->velocity_error.y + params->kp[1] * out->position_error.y + params->ki[1] * state->integral_position_error.y,
        input->reference_acceleration.z + params->kv[2] * out->velocity_error.z + params->kp[2] * out->position_error.z + params->ki[2] * state->integral_position_error.z);
}

static int c_consume_new_measurement_sample(
    MosimPx4ctrlG9FamilyCState *state,
    const MosimPx4ctrlG9FamilyCInput *input,
    double *dt)
{
    *dt = c_safe_positive(input->dt, 0.01);
    if (!input->measurement_stamp_valid)
    {
        return 1;
    }
    if (!state->has_previous_measurement_stamp)
    {
        state->previous_measurement_stamp_s = input->measurement_stamp_s;
        state->has_previous_measurement_stamp = 1;
        return 1;
    }
    {
        const double measurement_dt =
            input->measurement_stamp_s - state->previous_measurement_stamp_s;
        if (measurement_dt <= 1.0e-6)
        {
            return 0;
        }
        state->previous_measurement_stamp_s = input->measurement_stamp_s;
        *dt = measurement_dt;
    }
    return 1;
}

static MosimPx4ctrlG9FamilyCVec3 c_measured_acceleration_from_velocity(
    const MosimPx4ctrlG9FamilyCParams *params,
    MosimPx4ctrlG9FamilyCState *state,
    const MosimPx4ctrlG9FamilyCInput *input,
    double dt)
{
    MosimPx4ctrlG9FamilyCVec3 measured_acceleration;
    const double alpha = c_clamp(params->indi_accel_lpf_alpha, 0.0, 1.0);
    dt = c_safe_positive(dt, 0.01);
    if (state->has_previous_velocity)
    {
        measured_acceleration =
            c_scale(c_subtract(input->velocity, state->previous_velocity), 1.0 / dt);
    }
    else
    {
        measured_acceleration = state->previous_command_acceleration;
    }
    measured_acceleration =
        c_clamp_vec3(measured_acceleration, params->indi_measured_accel_limit);
    if (state->has_previous_velocity)
    {
        state->measured_acceleration_lpf = c_add(
            c_scale(measured_acceleration, alpha),
            c_scale(state->measured_acceleration_lpf, 1.0 - alpha));
    }
    else
    {
        state->measured_acceleration_lpf = measured_acceleration;
    }
    state->previous_velocity = input->velocity;
    state->has_previous_velocity = 1;
    return state->measured_acceleration_lpf;
}

static void c_fill_attitude_thrust_output(
    const MosimPx4ctrlG9FamilyCParams *params,
    const MosimPx4ctrlG9FamilyCState *state,
    const MosimPx4ctrlG9FamilyCInput *input,
    MosimPx4ctrlG9FamilyCOutput *out,
    int enforce_limits)
{
    double roll;
    double pitch;
    out->normalized_thrust = out->desired_acceleration.z / state->thr2acc;
    if (enforce_limits)
    {
        const double unclamped = out->normalized_thrust;
        out->normalized_thrust = c_clamp(
            out->normalized_thrust,
            params->min_normalized_thrust,
            params->max_normalized_thrust);
        if (fabs(out->normalized_thrust - unclamped) > 1.0e-12)
        {
            out->saturated = 1.0;
        }
    }
    out->collective_thrust_n =
        out->normalized_thrust * (params->mass * params->gravity / params->hover_percentage);
    out->desired_force_n = c_vec3(
        params->mass * out->desired_acceleration.x,
        params->mass * out->desired_acceleration.y,
        params->mass * out->desired_acceleration.z);
    {
        const double yaw_odom = c_yaw_from_quat(input->attitude);
        const double sin_yaw = sin(yaw_odom);
        const double cos_yaw = cos(yaw_odom);
        roll = (out->desired_acceleration.x * sin_yaw - out->desired_acceleration.y * cos_yaw) / params->gravity;
        pitch = (out->desired_acceleration.x * cos_yaw + out->desired_acceleration.y * sin_yaw) / params->gravity;
    }
    if (enforce_limits)
    {
        const double unclamped_roll = roll;
        const double unclamped_pitch = pitch;
        roll = c_clamp(roll, -params->tilt_limit_rad, params->tilt_limit_rad);
        pitch = c_clamp(pitch, -params->tilt_limit_rad, params->tilt_limit_rad);
        if (fabs(roll - unclamped_roll) > 1.0e-12 ||
            fabs(pitch - unclamped_pitch) > 1.0e-12)
        {
            out->saturated = 1.0;
        }
    }
    {
        const MosimPx4ctrlG9FamilyCQuat q_yaw =
            c_angle_axis(input->reference_yaw, c_vec3(0.0, 0.0, 1.0));
        const MosimPx4ctrlG9FamilyCQuat q_pitch =
            c_angle_axis(pitch, c_vec3(0.0, 1.0, 0.0));
        const MosimPx4ctrlG9FamilyCQuat q_roll =
            c_angle_axis(roll, c_vec3(1.0, 0.0, 0.0));
        const MosimPx4ctrlG9FamilyCQuat q_des_world =
            c_multiply(c_multiply(q_yaw, q_pitch), q_roll);
        out->desired_attitude =
            c_multiply(c_multiply(input->imu_attitude, c_inverse(input->attitude)), q_des_world);
    }
}

static void c_fill_flatness_attitude_output(
    const MosimPx4ctrlG9FamilyCParams *params,
    const MosimPx4ctrlG9FamilyCState *state,
    const MosimPx4ctrlG9FamilyCInput *input,
    MosimPx4ctrlG9FamilyCOutput *out,
    MosimPx4ctrlG9FamilyCVec3 force,
    int enforce_limits)
{
    MosimPx4ctrlG9FamilyCVec3 limited_force = force;
    const double force_norm = c_norm(limited_force);
    MosimPx4ctrlG9FamilyCVec3 b3c =
        c_normalize_vec3(limited_force, c_vec3(0.0, 0.0, 1.0));
    const double k_half_pi = 1.57079632679489661923;
    if (enforce_limits && params->tilt_limit_rad > 0.0 && params->tilt_limit_rad < k_half_pi)
    {
        const double min_b3_z = cos(params->tilt_limit_rad);
        if (b3c.z < min_b3_z)
        {
            const double xy_norm = sqrt(b3c.x * b3c.x + b3c.y * b3c.y);
            const double xy_limited = sin(params->tilt_limit_rad);
            if (xy_norm > 1.0e-12)
            {
                b3c.x = b3c.x / xy_norm * xy_limited;
                b3c.y = b3c.y / xy_norm * xy_limited;
            }
            else
            {
                b3c.x = 0.0;
                b3c.y = 0.0;
            }
            b3c.z = min_b3_z;
            b3c = c_normalize_vec3(b3c, c_vec3(0.0, 0.0, 1.0));
            limited_force = c_scale(b3c, force_norm);
            out->saturated = 1.0;
        }
    }
    {
        const MosimPx4ctrlG9FamilyCVec3 b1d =
            c_vec3(cos(input->reference_yaw), sin(input->reference_yaw), 0.0);
        MosimPx4ctrlG9FamilyCVec3 b2c = c_cross(b3c, b1d);
        MosimPx4ctrlG9FamilyCVec3 b1c;
        if (c_norm(b2c) <= 1.0e-9)
        {
            b2c = c_cross(b3c, c_vec3(0.0, 1.0, 0.0));
        }
        b2c = c_normalize_vec3(b2c, c_vec3(0.0, 1.0, 0.0));
        b1c = c_normalize_vec3(c_cross(b2c, b3c), b1d);
        out->desired_attitude = c_multiply(
            c_multiply(input->imu_attitude, c_inverse(input->attitude)),
            c_quat_from_rotation_matrix_columns(b1c, b2c, b3c));
    }
    out->desired_force_n = limited_force;
    out->desired_acceleration = c_vec3(
        limited_force.x / params->mass,
        limited_force.y / params->mass,
        limited_force.z / params->mass);
    out->normalized_thrust =
        c_dot(limited_force, b3c) / (params->mass * state->thr2acc);
    if (enforce_limits)
    {
        const double unclamped = out->normalized_thrust;
        out->normalized_thrust = c_clamp(
            out->normalized_thrust,
            params->min_normalized_thrust,
            params->max_normalized_thrust);
        if (fabs(out->normalized_thrust - unclamped) > 1.0e-12)
        {
            out->saturated = 1.0;
        }
    }
    out->collective_thrust_n =
        out->normalized_thrust * (params->mass * params->gravity / params->hover_percentage);
}

static void c_se3_or_dfbc_basic_step(
    const MosimPx4ctrlG9FamilyCParams *params,
    const MosimPx4ctrlG9FamilyCState *state,
    const MosimPx4ctrlG9FamilyCInput *input,
    MosimPx4ctrlG9FamilyCOutput *out)
{
    MosimPx4ctrlG9FamilyCVec3 force;
    out->position_error = c_subtract(input->reference_position, input->position);
    out->velocity_error = c_subtract(input->reference_velocity, input->velocity);
    force = c_vec3(
        params->mass * (input->reference_acceleration.x + params->kp[0] * out->position_error.x + params->kv[0] * out->velocity_error.x),
        params->mass * (input->reference_acceleration.y + params->kp[1] * out->position_error.y + params->kv[1] * out->velocity_error.y),
        params->mass * (input->reference_acceleration.z + params->kp[2] * out->position_error.z + params->kv[2] * out->velocity_error.z + params->gravity));
    c_fill_flatness_attitude_output(params, state, input, out, force, 1);
}

static void c_smc_boundary_layer_step(
    const MosimPx4ctrlG9FamilyCParams *params,
    const MosimPx4ctrlG9FamilyCState *state,
    const MosimPx4ctrlG9FamilyCInput *input,
    MosimPx4ctrlG9FamilyCOutput *out)
{
    MosimPx4ctrlG9FamilyCVec3 switching_acceleration;
    MosimPx4ctrlG9FamilyCVec3 force;
    out->position_error = c_subtract(input->reference_position, input->position);
    out->velocity_error = c_subtract(input->reference_velocity, input->velocity);
    out->sliding_surface = c_clamp_vec3(
        c_vec3(
            out->velocity_error.x + params->smc_lambda[0] * out->position_error.x,
            out->velocity_error.y + params->smc_lambda[1] * out->position_error.y,
            out->velocity_error.z + params->smc_lambda[2] * out->position_error.z),
        params->smc_surface_limit);
    switching_acceleration = c_vec3(
        params->smc_eta[0] * c_sat(out->sliding_surface.x / c_safe_positive(fabs(params->smc_phi[0]), 1.0e-9)),
        params->smc_eta[1] * c_sat(out->sliding_surface.y / c_safe_positive(fabs(params->smc_phi[1]), 1.0e-9)),
        params->smc_eta[2] * c_sat(out->sliding_surface.z / c_safe_positive(fabs(params->smc_phi[2]), 1.0e-9)));
    force = c_vec3(
        params->mass * (input->reference_acceleration.x + params->kp[0] * out->position_error.x + params->kv[0] * out->velocity_error.x + switching_acceleration.x),
        params->mass * (input->reference_acceleration.y + params->kp[1] * out->position_error.y + params->kv[1] * out->velocity_error.y + switching_acceleration.y),
        params->mass * (input->reference_acceleration.z + params->kp[2] * out->position_error.z + params->kv[2] * out->velocity_error.z + switching_acceleration.z + params->gravity));
    c_fill_flatness_attitude_output(params, state, input, out, force, 1);
}

static void c_pid_indi_step(
    const MosimPx4ctrlG9FamilyCParams *params,
    MosimPx4ctrlG9FamilyCState *state,
    const MosimPx4ctrlG9FamilyCInput *input,
    MosimPx4ctrlG9FamilyCOutput *out)
{
    const MosimPx4ctrlG9FamilyCVec3 base_acceleration_no_gravity =
        c_pid_acceleration_no_gravity(params, state, input, out);
    double measurement_dt = input->dt;
    const int update_measurement =
        c_consume_new_measurement_sample(state, input, &measurement_dt);
    const int had_previous_velocity = state->has_previous_velocity;
    MosimPx4ctrlG9FamilyCVec3 indi_increment = c_vec3(0.0, 0.0, 0.0);
    if (update_measurement)
    {
        (void)c_measured_acceleration_from_velocity(params, state, input, measurement_dt);
    }
    if (update_measurement && had_previous_velocity)
    {
        const MosimPx4ctrlG9FamilyCVec3 acceleration_residual =
            c_subtract(state->previous_command_acceleration, state->measured_acceleration_lpf);
        indi_increment = c_clamp_vec3(
            c_vec3(
                params->indi_gain[0] * acceleration_residual.x,
                params->indi_gain[1] * acceleration_residual.y,
                params->indi_gain[2] * acceleration_residual.z),
            params->indi_increment_limit);
        out->sliding_surface = acceleration_residual;
    }
    out->desired_acceleration = c_vec3(
        base_acceleration_no_gravity.x + indi_increment.x,
        base_acceleration_no_gravity.y + indi_increment.y,
        base_acceleration_no_gravity.z + indi_increment.z + params->gravity);
    state->previous_command_acceleration = c_vec3(
        out->desired_acceleration.x,
        out->desired_acceleration.y,
        out->desired_acceleration.z - params->gravity);
    c_fill_attitude_thrust_output(params, state, input, out, 1);
}

static void c_nmpc_outer_step(
    const MosimPx4ctrlG9FamilyCParams *params,
    MosimPx4ctrlG9FamilyCState *state,
    const MosimPx4ctrlG9FamilyCInput *input,
    MosimPx4ctrlG9FamilyCOutput *out)
{
    const double horizon = c_clamp(params->nmpc_horizon_s, 0.05, 2.0);
    const double half_horizon_sq = 0.5 * horizon * horizon;
    const double horizon_sq = horizon * horizon;
    const double horizon_fourth = horizon_sq * horizon_sq;
    double unconstrained[3];
    MosimPx4ctrlG9FamilyCVec3 constrained_acceleration;

    out->position_error = c_subtract(input->reference_position, input->position);
    out->velocity_error = c_subtract(input->reference_velocity, input->velocity);
    {
        const MosimPx4ctrlG9FamilyCVec3 reference_position_horizon = c_vec3(
            input->reference_position.x + input->reference_velocity.x * horizon + half_horizon_sq * input->reference_acceleration.x,
            input->reference_position.y + input->reference_velocity.y * horizon + half_horizon_sq * input->reference_acceleration.y,
            input->reference_position.z + input->reference_velocity.z * horizon + half_horizon_sq * input->reference_acceleration.z);
        const MosimPx4ctrlG9FamilyCVec3 reference_velocity_horizon = c_vec3(
            input->reference_velocity.x + input->reference_acceleration.x * horizon,
            input->reference_velocity.y + input->reference_acceleration.y * horizon,
            input->reference_velocity.z + input->reference_acceleration.z * horizon);
        const MosimPx4ctrlG9FamilyCVec3 predicted_position_open_loop = c_vec3(
            input->position.x + input->velocity.x * horizon,
            input->position.y + input->velocity.y * horizon,
            input->position.z + input->velocity.z * horizon);
        const MosimPx4ctrlG9FamilyCVec3 horizon_position_error =
            c_subtract(reference_position_horizon, predicted_position_open_loop);
        const MosimPx4ctrlG9FamilyCVec3 horizon_velocity_error =
            c_subtract(reference_velocity_horizon, input->velocity);
        int i;
        const double hp[3] = {
            horizon_position_error.x,
            horizon_position_error.y,
            horizon_position_error.z};
        const double hv[3] = {
            horizon_velocity_error.x,
            horizon_velocity_error.y,
            horizon_velocity_error.z};
        const double previous[3] = {
            state->previous_command_acceleration.x,
            state->previous_command_acceleration.y,
            state->previous_command_acceleration.z};
        for (i = 0; i < 3; ++i)
        {
            const double wp = c_safe_nonnegative(params->nmpc_position_weight[i]);
            const double wv = c_safe_nonnegative(params->nmpc_velocity_weight[i]);
            const double wu = c_safe_nonnegative(params->nmpc_control_weight[i]);
            const double numerator =
                wp * horizon_sq * hp[i] +
                2.0 * wv * horizon * hv[i] +
                2.0 * wu * previous[i];
            const double denominator =
                0.5 * wp * horizon_fourth + 2.0 * wv * horizon_sq + 2.0 * wu;
            unconstrained[i] = numerator / c_safe_positive(denominator, 1.0e-6);
        }
    }
    constrained_acceleration =
        c_clamp_vec3(c_vec3(unconstrained[0], unconstrained[1], unconstrained[2]), params->nmpc_accel_limit);
    constrained_acceleration =
        c_clamp_delta_vec3(constrained_acceleration, state->previous_command_acceleration, params->nmpc_increment_limit);
    state->previous_command_acceleration = constrained_acceleration;
    out->desired_acceleration = c_vec3(
        constrained_acceleration.x,
        constrained_acceleration.y,
        constrained_acceleration.z + params->gravity);
    out->sliding_surface =
        c_subtract(c_vec3(unconstrained[0], unconstrained[1], unconstrained[2]), constrained_acceleration);
    out->saturated = c_norm(out->sliding_surface) > 1.0e-12 ? 1.0 : 0.0;
    c_fill_attitude_thrust_output(params, state, input, out, 1);
}

static void c_l1_awff_step(
    const MosimPx4ctrlG9FamilyCParams *params,
    MosimPx4ctrlG9FamilyCState *state,
    const MosimPx4ctrlG9FamilyCInput *input,
    MosimPx4ctrlG9FamilyCOutput *out)
{
    const MosimPx4ctrlG9FamilyCVec3 nominal_acceleration_no_gravity =
        c_pid_acceleration_no_gravity(params, state, input, out);
    double measurement_dt = input->dt;
    const int update_measurement =
        c_consume_new_measurement_sample(state, input, &measurement_dt);
    const int had_previous_velocity = state->has_previous_velocity;
    MosimPx4ctrlG9FamilyCVec3 measured_acceleration = state->measured_acceleration_lpf;
    MosimPx4ctrlG9FamilyCVec3 residual = c_vec3(0.0, 0.0, 0.0);

    if (update_measurement)
    {
        measured_acceleration =
            c_measured_acceleration_from_velocity(params, state, input, measurement_dt);
    }
    if (update_measurement && had_previous_velocity)
    {
        MosimPx4ctrlG9FamilyCVec3 adaptive_update;
        const double filter_T = fabs(params->l1_filter_T);
        const double alpha = filter_T > 1.0e-9
            ? c_clamp(measurement_dt / (filter_T + measurement_dt), 0.0, 1.0)
            : 1.0;
        const double model_decay = c_safe_nonnegative(params->l1_model_decay);

        residual = c_subtract(measured_acceleration, state->previous_command_acceleration);
        adaptive_update = c_vec3(
            -params->l1_gain[0] * residual.x - model_decay * state->disturbance_estimate.x,
            -params->l1_gain[1] * residual.y - model_decay * state->disturbance_estimate.y,
            -params->l1_gain[2] * residual.z - model_decay * state->disturbance_estimate.z);
        state->disturbance_estimate = c_clamp_vec3(
            c_add(
                c_scale(state->disturbance_estimate, 1.0 - alpha),
                c_scale(
                    c_add(state->disturbance_estimate, c_scale(adaptive_update, measurement_dt)),
                    alpha)),
            params->l1_comp_limit);
    }

    {
        const MosimPx4ctrlG9FamilyCVec3 drag_feedforward = c_vec3(
            -params->drag_feedforward_gain[0] * input->reference_velocity.x,
            -params->drag_feedforward_gain[1] * input->reference_velocity.y,
            -params->drag_feedforward_gain[2] * input->reference_velocity.z);
        const MosimPx4ctrlG9FamilyCVec3 compensated_acceleration_no_gravity =
            c_add(c_add(nominal_acceleration_no_gravity, state->disturbance_estimate), drag_feedforward);
        state->previous_command_acceleration = compensated_acceleration_no_gravity;
        out->desired_acceleration = c_vec3(
            compensated_acceleration_no_gravity.x,
            compensated_acceleration_no_gravity.y,
            compensated_acceleration_no_gravity.z + params->gravity);
    }

    c_fill_attitude_thrust_output(params, state, input, out, 1);
    out->sliding_surface = residual;
    out->disturbance_estimate = state->disturbance_estimate;
}

static void c_safety_filter_step(
    const MosimPx4ctrlG9FamilyCParams *params,
    MosimPx4ctrlG9FamilyCState *state,
    const MosimPx4ctrlG9FamilyCInput *input,
    MosimPx4ctrlG9FamilyCOutput *out)
{
    const MosimPx4ctrlG9FamilyCVec3 nominal_acceleration_no_gravity =
        c_pid_acceleration_no_gravity(params, state, input, out);
    const MosimPx4ctrlG9FamilyCVec3 limited_acceleration_no_gravity =
        c_clamp_vec3(nominal_acceleration_no_gravity, params->safety_accel_limit);
    const double saturated_before_attitude =
        c_vec3_components_equal(nominal_acceleration_no_gravity, limited_acceleration_no_gravity) ? 0.0 : 1.0;

    out->saturated = saturated_before_attitude;
    out->sliding_surface = c_subtract(nominal_acceleration_no_gravity, limited_acceleration_no_gravity);
    state->previous_command_acceleration = limited_acceleration_no_gravity;
    out->desired_acceleration = c_vec3(
        limited_acceleration_no_gravity.x,
        limited_acceleration_no_gravity.y,
        limited_acceleration_no_gravity.z + params->gravity);
    c_fill_attitude_thrust_output(params, state, input, out, 1);
    out->saturated = out->saturated || saturated_before_attitude;
    out->status_code = out->saturated ? 2 : 0;
}

static void c_fault_allocation_step(
    const MosimPx4ctrlG9FamilyCParams *params,
    MosimPx4ctrlG9FamilyCState *state,
    const MosimPx4ctrlG9FamilyCInput *input,
    MosimPx4ctrlG9FamilyCOutput *out)
{
    int i;
    double min_efficiency = 1.0;
    double mean_efficiency = 0.0;
    double missing_authority;
    double requested_multiplier;
    double bounded_multiplier;
    double uncompensated_thrust;
    double full_thrust_n;
    const MosimPx4ctrlG9FamilyCVec3 nominal_acceleration_no_gravity =
        c_pid_acceleration_no_gravity(params, state, input, out);

    state->previous_command_acceleration = nominal_acceleration_no_gravity;
    out->desired_acceleration = c_vec3(
        nominal_acceleration_no_gravity.x,
        nominal_acceleration_no_gravity.y,
        nominal_acceleration_no_gravity.z + params->gravity);
    c_fill_attitude_thrust_output(params, state, input, out, 1);

    for (i = 0; i < 4; ++i)
    {
        const double eta = c_clamp(
            params->fault_rotor_efficiency[i],
            c_safe_positive(params->fault_min_efficiency, 0.01),
            1.0);
        if (eta < min_efficiency)
        {
            min_efficiency = eta;
        }
        mean_efficiency += eta;
    }
    mean_efficiency *= 0.25;

    missing_authority = c_clamp(1.0 - mean_efficiency, 0.0, 1.0);
    requested_multiplier = 1.0 + c_clamp(params->fault_allocation_blend, 0.0, 1.0) * missing_authority;
    bounded_multiplier = c_clamp(
        requested_multiplier,
        1.0,
        1.0 + c_safe_nonnegative(params->fault_thrust_comp_limit));
    uncompensated_thrust = out->normalized_thrust;
    out->normalized_thrust = c_clamp(
        uncompensated_thrust * bounded_multiplier,
        params->min_normalized_thrust,
        params->max_normalized_thrust);
    full_thrust_n = params->mass * params->gravity / params->hover_percentage;
    out->collective_thrust_n = out->normalized_thrust * full_thrust_n;
    out->desired_force_n = c_vec3(
        out->desired_force_n.x,
        out->desired_force_n.y,
        out->desired_force_n.z * bounded_multiplier);
    out->saturated = out->saturated ||
        missing_authority > 1.0e-12 ||
        fabs(out->normalized_thrust - uncompensated_thrust * bounded_multiplier) > 1.0e-12;
    out->disturbance_estimate = c_vec3(
        missing_authority,
        min_efficiency,
        bounded_multiplier - 1.0);
    out->sliding_surface = c_vec3(
        params->fault_rotor_efficiency[0],
        params->fault_rotor_efficiency[1],
        params->fault_rotor_efficiency[2]);
    out->status_code = missing_authority > 1.0e-12 ? 3 : 0;
}

void mosim_px4ctrl_g9_family_c_step(
    const MosimPx4ctrlG9FamilyCParams *params,
    MosimPx4ctrlG9FamilyCState *state,
    const MosimPx4ctrlG9FamilyCInput *input,
    MosimPx4ctrlG9FamilyCOutput *output)
{
    memset(output, 0, sizeof(*output));
    output->desired_attitude = c_quat(1.0, 0.0, 0.0, 0.0);
    if (input->reset)
    {
        mosim_px4ctrl_g9_family_c_reset(params, state);
    }
    if (!input->enable)
    {
        *output = c_disabled_output(input);
        return;
    }
    if (input->controller_id == MOSIM_PX4CTRL_G9_OFFICIAL_PID)
    {
        const MosimPx4ctrlG9FamilyCVec3 acc =
            c_pid_acceleration_no_gravity(params, state, input, output);
        output->desired_acceleration = c_vec3(acc.x, acc.y, acc.z + params->gravity);
        c_fill_attitude_thrust_output(params, state, input, output, 1);
        return;
    }
    if (input->controller_id == MOSIM_PX4CTRL_G9_SE3_BASIC ||
        input->controller_id == MOSIM_PX4CTRL_G9_DFBC_BASIC)
    {
        c_se3_or_dfbc_basic_step(params, state, input, output);
        return;
    }
    if (input->controller_id == MOSIM_PX4CTRL_G9_SMC_BOUNDARY_LAYER)
    {
        c_smc_boundary_layer_step(params, state, input, output);
        return;
    }
    if (input->controller_id == MOSIM_PX4CTRL_G9_PID_INDI)
    {
        c_pid_indi_step(params, state, input, output);
        return;
    }
    if (input->controller_id == MOSIM_PX4CTRL_G9_NMPC_OUTER)
    {
        c_nmpc_outer_step(params, state, input, output);
        return;
    }
    if (input->controller_id == MOSIM_PX4CTRL_G10_L1_AWFF)
    {
        c_l1_awff_step(params, state, input, output);
        return;
    }
    if (input->controller_id == MOSIM_PX4CTRL_G10_SAFETY_FILTER)
    {
        c_safety_filter_step(params, state, input, output);
        return;
    }
    if (input->controller_id == MOSIM_PX4CTRL_G10_FAULT_ALLOCATION)
    {
        c_fault_allocation_step(params, state, input, output);
        return;
    }
    *output = c_disabled_output(input);
    output->status_code = 2;
}

void MosimPx4ctrlG9FamilyCStepScalar(
    double controller_id,
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
    double reference_jerk_x,
    double reference_jerk_y,
    double reference_jerk_z,
    double reference_snap_x,
    double reference_snap_y,
    double reference_snap_z,
    double reference_yaw,
    double reference_yaw_rate,
    double reference_yaw_acceleration,
    double measurement_stamp_s,
    double imu_attitude_w,
    double imu_attitude_x,
    double imu_attitude_y,
    double imu_attitude_z,
    double imu_angular_velocity_x,
    double imu_angular_velocity_y,
    double imu_angular_velocity_z,
    double enable,
    double reset,
    double measurement_stamp_valid,
    double enable_disturbance_observer,
    double kp_x,
    double kp_y,
    double kp_z,
    double kv_x,
    double kv_y,
    double kv_z,
    double ki_x,
    double ki_y,
    double ki_z,
    double smc_lambda_x,
    double smc_lambda_y,
    double smc_lambda_z,
    double smc_eta_x,
    double smc_eta_y,
    double smc_eta_z,
    double smc_phi_x,
    double smc_phi_y,
    double smc_phi_z,
    double smc_surface_limit_x,
    double smc_surface_limit_y,
    double smc_surface_limit_z,
    double indi_gain_x,
    double indi_gain_y,
    double indi_gain_z,
    double indi_increment_limit_x,
    double indi_increment_limit_y,
    double indi_increment_limit_z,
    double indi_measured_accel_limit_x,
    double indi_measured_accel_limit_y,
    double indi_measured_accel_limit_z,
    double indi_accel_lpf_alpha,
    double nmpc_horizon_s,
    double nmpc_position_weight_x,
    double nmpc_position_weight_y,
    double nmpc_position_weight_z,
    double nmpc_velocity_weight_x,
    double nmpc_velocity_weight_y,
    double nmpc_velocity_weight_z,
    double nmpc_control_weight_x,
    double nmpc_control_weight_y,
    double nmpc_control_weight_z,
    double nmpc_accel_limit_x,
    double nmpc_accel_limit_y,
    double nmpc_accel_limit_z,
    double nmpc_increment_limit_x,
    double nmpc_increment_limit_y,
    double nmpc_increment_limit_z,
    double l1_model_decay,
    double l1_filter_T,
    double l1_gain_x,
    double l1_gain_y,
    double l1_gain_z,
    double l1_comp_limit_x,
    double l1_comp_limit_y,
    double l1_comp_limit_z,
    double drag_feedforward_gain_x,
    double drag_feedforward_gain_y,
    double drag_feedforward_gain_z,
    double safety_accel_limit_x,
    double safety_accel_limit_y,
    double safety_accel_limit_z,
    double fault_rotor_efficiency_1,
    double fault_rotor_efficiency_2,
    double fault_rotor_efficiency_3,
    double fault_rotor_efficiency_4,
    double fault_allocation_blend,
    double fault_min_efficiency,
    double fault_thrust_comp_limit,
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
    double *sliding_surface_x,
    double *sliding_surface_y,
    double *sliding_surface_z,
    double *desired_acceleration_x,
    double *desired_acceleration_y,
    double *desired_acceleration_z,
    double *desired_body_rate_x,
    double *desired_body_rate_y,
    double *desired_body_rate_z,
    double *desired_body_acceleration_x,
    double *desired_body_acceleration_y,
    double *desired_body_acceleration_z,
    double *disturbance_estimate_x,
    double *disturbance_estimate_y,
    double *disturbance_estimate_z,
    double *desired_force_N_x,
    double *desired_force_N_y,
    double *desired_force_N_z,
    double *saturated,
    double *status_code)
{
    static MosimPx4ctrlG9FamilyCState states[10];
    static int initialized[10] = {0};
    MosimPx4ctrlG9FamilyCParams params;
    MosimPx4ctrlG9FamilyCInput input;
    MosimPx4ctrlG9FamilyCOutput output;

    params.kp[0] = kp_x;
    params.kp[1] = kp_y;
    params.kp[2] = kp_z;
    params.kv[0] = kv_x;
    params.kv[1] = kv_y;
    params.kv[2] = kv_z;
    params.ki[0] = ki_x;
    params.ki[1] = ki_y;
    params.ki[2] = ki_z;
    params.smc_lambda[0] = smc_lambda_x;
    params.smc_lambda[1] = smc_lambda_y;
    params.smc_lambda[2] = smc_lambda_z;
    params.smc_eta[0] = smc_eta_x;
    params.smc_eta[1] = smc_eta_y;
    params.smc_eta[2] = smc_eta_z;
    params.smc_phi[0] = smc_phi_x;
    params.smc_phi[1] = smc_phi_y;
    params.smc_phi[2] = smc_phi_z;
    params.smc_surface_limit[0] = smc_surface_limit_x;
    params.smc_surface_limit[1] = smc_surface_limit_y;
    params.smc_surface_limit[2] = smc_surface_limit_z;
    params.indi_gain[0] = indi_gain_x;
    params.indi_gain[1] = indi_gain_y;
    params.indi_gain[2] = indi_gain_z;
    params.indi_increment_limit[0] = indi_increment_limit_x;
    params.indi_increment_limit[1] = indi_increment_limit_y;
    params.indi_increment_limit[2] = indi_increment_limit_z;
    params.indi_measured_accel_limit[0] = indi_measured_accel_limit_x;
    params.indi_measured_accel_limit[1] = indi_measured_accel_limit_y;
    params.indi_measured_accel_limit[2] = indi_measured_accel_limit_z;
    params.indi_accel_lpf_alpha = indi_accel_lpf_alpha;
    params.nmpc_horizon_s = nmpc_horizon_s;
    params.nmpc_position_weight[0] = nmpc_position_weight_x;
    params.nmpc_position_weight[1] = nmpc_position_weight_y;
    params.nmpc_position_weight[2] = nmpc_position_weight_z;
    params.nmpc_velocity_weight[0] = nmpc_velocity_weight_x;
    params.nmpc_velocity_weight[1] = nmpc_velocity_weight_y;
    params.nmpc_velocity_weight[2] = nmpc_velocity_weight_z;
    params.nmpc_control_weight[0] = nmpc_control_weight_x;
    params.nmpc_control_weight[1] = nmpc_control_weight_y;
    params.nmpc_control_weight[2] = nmpc_control_weight_z;
    params.nmpc_accel_limit[0] = nmpc_accel_limit_x;
    params.nmpc_accel_limit[1] = nmpc_accel_limit_y;
    params.nmpc_accel_limit[2] = nmpc_accel_limit_z;
    params.nmpc_increment_limit[0] = nmpc_increment_limit_x;
    params.nmpc_increment_limit[1] = nmpc_increment_limit_y;
    params.nmpc_increment_limit[2] = nmpc_increment_limit_z;
    params.l1_model_decay = l1_model_decay;
    params.l1_filter_T = l1_filter_T;
    params.l1_gain[0] = l1_gain_x;
    params.l1_gain[1] = l1_gain_y;
    params.l1_gain[2] = l1_gain_z;
    params.l1_comp_limit[0] = l1_comp_limit_x;
    params.l1_comp_limit[1] = l1_comp_limit_y;
    params.l1_comp_limit[2] = l1_comp_limit_z;
    params.drag_feedforward_gain[0] = drag_feedforward_gain_x;
    params.drag_feedforward_gain[1] = drag_feedforward_gain_y;
    params.drag_feedforward_gain[2] = drag_feedforward_gain_z;
    params.safety_accel_limit[0] = safety_accel_limit_x;
    params.safety_accel_limit[1] = safety_accel_limit_y;
    params.safety_accel_limit[2] = safety_accel_limit_z;
    params.fault_rotor_efficiency[0] = fault_rotor_efficiency_1;
    params.fault_rotor_efficiency[1] = fault_rotor_efficiency_2;
    params.fault_rotor_efficiency[2] = fault_rotor_efficiency_3;
    params.fault_rotor_efficiency[3] = fault_rotor_efficiency_4;
    params.fault_allocation_blend = fault_allocation_blend;
    params.fault_min_efficiency = fault_min_efficiency;
    params.fault_thrust_comp_limit = fault_thrust_comp_limit;
    params.integral_limit[0] = integral_limit_x;
    params.integral_limit[1] = integral_limit_y;
    params.integral_limit[2] = integral_limit_z;
    params.mass = mass;
    params.gravity = gravity;
    params.hover_percentage = hover_percentage;
    params.min_normalized_thrust = min_normalized_thrust;
    params.max_normalized_thrust = max_normalized_thrust;
    params.tilt_limit_rad = tilt_limit_rad;

    input.controller_id = (int)controller_id;
    input.dt = dt;
    input.position = c_vec3(position_x, position_y, position_z);
    input.velocity = c_vec3(velocity_x, velocity_y, velocity_z);
    input.attitude = c_quat(attitude_w, attitude_x, attitude_y, attitude_z);
    input.angular_velocity = c_vec3(angular_velocity_x, angular_velocity_y, angular_velocity_z);
    input.reference_position = c_vec3(reference_position_x, reference_position_y, reference_position_z);
    input.reference_velocity = c_vec3(reference_velocity_x, reference_velocity_y, reference_velocity_z);
    input.reference_acceleration = c_vec3(reference_acceleration_x, reference_acceleration_y, reference_acceleration_z);
    input.reference_jerk = c_vec3(reference_jerk_x, reference_jerk_y, reference_jerk_z);
    input.reference_snap = c_vec3(reference_snap_x, reference_snap_y, reference_snap_z);
    input.reference_yaw = reference_yaw;
    input.reference_yaw_rate = reference_yaw_rate;
    input.reference_yaw_acceleration = reference_yaw_acceleration;
    input.measurement_stamp_s = measurement_stamp_s;
    input.imu_attitude = c_quat(imu_attitude_w, imu_attitude_x, imu_attitude_y, imu_attitude_z);
    input.imu_angular_velocity = c_vec3(imu_angular_velocity_x, imu_angular_velocity_y, imu_angular_velocity_z);
    input.enable = enable != 0.0;
    input.reset = reset != 0.0;
    input.measurement_stamp_valid = measurement_stamp_valid != 0.0;
    input.enable_disturbance_observer = enable_disturbance_observer != 0.0;

    {
        int state_index = input.controller_id;
        if (state_index < 0 || state_index > 9)
        {
            state_index = 0;
        }
        if (!initialized[state_index])
        {
            mosim_px4ctrl_g9_family_c_reset(&params, &states[state_index]);
            initialized[state_index] = 1;
        }
        mosim_px4ctrl_g9_family_c_step(&params, &states[state_index], &input, &output);
    }

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
    *sliding_surface_x = output.sliding_surface.x;
    *sliding_surface_y = output.sliding_surface.y;
    *sliding_surface_z = output.sliding_surface.z;
    *desired_acceleration_x = output.desired_acceleration.x;
    *desired_acceleration_y = output.desired_acceleration.y;
    *desired_acceleration_z = output.desired_acceleration.z;
    *desired_body_rate_x = output.desired_body_rate.x;
    *desired_body_rate_y = output.desired_body_rate.y;
    *desired_body_rate_z = output.desired_body_rate.z;
    *desired_body_acceleration_x = output.desired_body_acceleration.x;
    *desired_body_acceleration_y = output.desired_body_acceleration.y;
    *desired_body_acceleration_z = output.desired_body_acceleration.z;
    *disturbance_estimate_x = output.disturbance_estimate.x;
    *disturbance_estimate_y = output.disturbance_estimate.y;
    *disturbance_estimate_z = output.disturbance_estimate.z;
    *desired_force_N_x = output.desired_force_n.x;
    *desired_force_N_y = output.desired_force_n.y;
    *desired_force_N_z = output.desired_force_n.z;
    *saturated = output.saturated;
    *status_code = (double)output.status_code;
}
