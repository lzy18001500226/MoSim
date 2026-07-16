#include "pid_attitude_thrust_core.h"

#include <math.h>
#include <stddef.h>
#include <string.h>

static double clamp_value(double value, double lower, double upper)
{
    if (value < lower) return lower;
    if (value > upper) return upper;
    return value;
}

static MosimPidVec3 vec3(double x, double y, double z)
{
    MosimPidVec3 value = {x, y, z};
    return value;
}

static MosimPidVec3 cross(MosimPidVec3 a, MosimPidVec3 b)
{
    return vec3(a.y * b.z - a.z * b.y,
                a.z * b.x - a.x * b.z,
                a.x * b.y - a.y * b.x);
}

static double norm(MosimPidVec3 value)
{
    return sqrt(value.x * value.x + value.y * value.y + value.z * value.z);
}

static MosimPidVec3 normalize_vec3(MosimPidVec3 value, MosimPidVec3 fallback)
{
    const double magnitude = norm(value);
    if (!isfinite(magnitude) || magnitude <= 1.0e-12) return fallback;
    return vec3(value.x / magnitude, value.y / magnitude, value.z / magnitude);
}

static MosimPidQuat normalize_quat(MosimPidQuat value)
{
    const double magnitude = sqrt(value.w * value.w + value.x * value.x +
                                  value.y * value.y + value.z * value.z);
    MosimPidQuat identity = {1.0, 0.0, 0.0, 0.0};
    if (!isfinite(magnitude) || magnitude <= 1.0e-12) return identity;
    value.w /= magnitude;
    value.x /= magnitude;
    value.y /= magnitude;
    value.z /= magnitude;
    if (value.w < 0.0) {
        value.w = -value.w;
        value.x = -value.x;
        value.y = -value.y;
        value.z = -value.z;
    }
    return value;
}

static MosimPidQuat quat_from_columns(MosimPidVec3 b1, MosimPidVec3 b2,
                                      MosimPidVec3 b3)
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
    MosimPidQuat q;
    if (trace > 0.0) {
        const double s = 2.0 * sqrt(trace + 1.0);
        q.w = 0.25 * s;
        q.x = (m21 - m12) / s;
        q.y = (m02 - m20) / s;
        q.z = (m10 - m01) / s;
    } else if (m00 > m11 && m00 > m22) {
        const double s = 2.0 * sqrt(1.0 + m00 - m11 - m22);
        q.w = (m21 - m12) / s;
        q.x = 0.25 * s;
        q.y = (m01 + m10) / s;
        q.z = (m02 + m20) / s;
    } else if (m11 > m22) {
        const double s = 2.0 * sqrt(1.0 + m11 - m00 - m22);
        q.w = (m02 - m20) / s;
        q.x = (m01 + m10) / s;
        q.y = 0.25 * s;
        q.z = (m12 + m21) / s;
    } else {
        const double s = 2.0 * sqrt(1.0 + m22 - m00 - m11);
        q.w = (m10 - m01) / s;
        q.x = (m02 + m20) / s;
        q.y = (m12 + m21) / s;
        q.z = 0.25 * s;
    }
    return normalize_quat(q);
}

static int finite_vec3(MosimPidVec3 value)
{
    return isfinite(value.x) && isfinite(value.y) && isfinite(value.z);
}

static int finite_quat(MosimPidQuat value)
{
    return isfinite(value.w) && isfinite(value.x) &&
           isfinite(value.y) && isfinite(value.z);
}

static int valid_algorithm(int algorithm_id)
{
    return algorithm_id >= MOSIM_PID_CASCADE &&
           algorithm_id <= MOSIM_PID_FEEDFORWARD_PROFILE;
}

static void configure_axis(MosimPidConfig *position,
                           MosimPidConfig *velocity)
{
    mosim_pid_default_config(position);
    position->kp = 1.0;
    position->ki = 0.10;
    position->kd = 0.05;
    position->output_min = -2.0;
    position->output_max = 2.0;
    position->integral_min = -1.0;
    position->integral_max = 1.0;
    position->anti_windup_gain = 0.4;
    position->derivative_filter_tau = 0.05;

    mosim_pid_default_config(velocity);
    velocity->kp = 2.0;
    velocity->ki = 0.20;
    velocity->kd = 0.10;
    velocity->output_min = -5.0;
    velocity->output_max = 5.0;
    velocity->integral_min = -2.0;
    velocity->integral_max = 2.0;
    velocity->anti_windup_gain = 0.4;
    velocity->derivative_filter_tau = 0.03;
}

void mosim_pid_attitude_thrust_default_params(
    int algorithm_id,
    MosimPidAttitudeThrustParams *params)
{
    size_t axis;
    if (params == NULL) return;
    memset(params, 0, sizeof(*params));
    params->algorithm_id = algorithm_id;
    for (axis = 0; axis < 3; ++axis) {
        configure_axis(&params->position[axis], &params->velocity[axis]);
    }
    if (algorithm_id == MOSIM_PID_GAIN_SCHEDULED) {
        for (axis = 0; axis < 3; ++axis) params->velocity[axis].schedule_gain = 0.4;
    } else if (algorithm_id == MOSIM_PID_FUZZY) {
        for (axis = 0; axis < 3; ++axis) params->velocity[axis].fuzzy_gain = 0.3;
    } else if (algorithm_id == MOSIM_PID_NEURAL) {
        for (axis = 0; axis < 3; ++axis) {
            params->velocity[axis].neural_gain = 0.2;
            params->velocity[axis].neural_residual_limit = 0.25;
        }
    } else if (algorithm_id == MOSIM_PID_ANTI_WINDUP) {
        for (axis = 0; axis < 3; ++axis) {
            params->position[axis].anti_windup_gain = 1.0;
            params->velocity[axis].anti_windup_gain = 1.0;
        }
    } else if (algorithm_id == MOSIM_PID_FEEDFORWARD_PROFILE) {
        for (axis = 0; axis < 3; ++axis) params->velocity[axis].feedforward_gain = 1.0;
    }
    params->mass_kg = 1.0;
    params->gravity_mps2 = 9.80665;
    params->max_tilt_rad = 0.52359877559829887308;
    params->min_collective_thrust_n = 0.0;
    params->max_collective_thrust_n = 19.6133;
}

void mosim_pid_attitude_thrust_reset(MosimPidAttitudeThrustState *state)
{
    if (state != NULL) memset(state, 0, sizeof(*state));
}

static double component(MosimPidVec3 value, size_t axis)
{
    if (axis == 0) return value.x;
    if (axis == 1) return value.y;
    return value.z;
}

static void set_component(MosimPidVec3 *value, size_t axis, double item)
{
    if (axis == 0) value->x = item;
    else if (axis == 1) value->y = item;
    else value->z = item;
}

static int valid_input(const MosimPidAttitudeThrustParams *params,
                       const MosimPidAttitudeThrustInput *input)
{
    return params != NULL && input != NULL && valid_algorithm(input->algorithm_id) &&
           params->algorithm_id == input->algorithm_id &&
           isfinite(input->dt) && input->dt > 0.0 &&
           isfinite(params->mass_kg) && params->mass_kg > 0.0 &&
           isfinite(params->gravity_mps2) && params->gravity_mps2 > 0.0 &&
           isfinite(params->max_tilt_rad) && params->max_tilt_rad >= 0.0 &&
           params->max_tilt_rad < 1.57079632679489661923 &&
           isfinite(params->min_collective_thrust_n) &&
           isfinite(params->max_collective_thrust_n) &&
           params->min_collective_thrust_n <= params->max_collective_thrust_n &&
           finite_vec3(input->position_enu_m) &&
           finite_vec3(input->velocity_enu_mps) &&
           finite_quat(input->attitude_enu_flu_wxyz) &&
           finite_vec3(input->angular_velocity_flu_radps) &&
           finite_vec3(input->reference_position_enu_m) &&
           finite_vec3(input->reference_velocity_enu_mps) &&
           finite_vec3(input->reference_acceleration_enu_mps2) &&
           isfinite(input->reference_yaw_enu_rad) &&
           finite_vec3(input->schedule) && finite_vec3(input->fuzzy_error) &&
           finite_vec3(input->neural_residual);
}

int mosim_pid_attitude_thrust_step(
    const MosimPidAttitudeThrustParams *params,
    MosimPidAttitudeThrustState *state,
    const MosimPidAttitudeThrustInput *input,
    MosimPidAttitudeThrustOutput *output)
{
    MosimPidAttitudeThrustState working_state;
    MosimPidVec3 acceleration = {0.0, 0.0, 0.0};
    MosimPidVec3 b1d;
    MosimPidVec3 b2;
    MosimPidVec3 b1;
    MosimPidVec3 b3;
    double horizontal;
    double horizontal_limit;
    double thrust;
    size_t axis;
    if (output == NULL || state == NULL) return -1;
    memset(output, 0, sizeof(*output));
    output->desired_attitude_enu_flu_wxyz.w = 1.0;
    output->status_code = -1;
    if (!valid_input(params, input)) return -1;
    output->algorithm_id = input->algorithm_id;
    if (!input->enable) {
        if (input->reset) mosim_pid_attitude_thrust_reset(state);
        output->desired_attitude_enu_flu_wxyz =
            normalize_quat(input->attitude_enu_flu_wxyz);
        output->status_code = 1;
        return 0;
    }
    working_state = *state;
    if (input->reset) mosim_pid_attitude_thrust_reset(&working_state);

    for (axis = 0; axis < 3; ++axis) {
        MosimPidInput position_input;
        MosimPidInput velocity_input;
        MosimPidOutput position_output;
        MosimPidOutput velocity_output;
        const double reference_position = component(input->reference_position_enu_m, axis);
        const double position = component(input->position_enu_m, axis);
        const double reference_velocity = component(input->reference_velocity_enu_mps, axis);
        const double velocity = component(input->velocity_enu_mps, axis);
        memset(&position_input, 0, sizeof(position_input));
        position_input.setpoint = reference_position;
        position_input.measurement = position;
        position_input.schedule = component(input->schedule, axis);
        position_input.fuzzy_error = component(input->fuzzy_error, axis);
        position_input.neural_residual = component(input->neural_residual, axis);
        position_input.dt = input->dt;
        position_input.enable = 1;
        if (mosim_pid_step(&params->position[axis], &working_state.position[axis],
                           &position_input, &position_output) != 0) return -1;

        memset(&velocity_input, 0, sizeof(velocity_input));
        velocity_input.setpoint = reference_velocity + position_output.command;
        velocity_input.measurement = velocity;
        velocity_input.feedforward = component(input->reference_acceleration_enu_mps2, axis);
        velocity_input.schedule = component(input->schedule, axis);
        velocity_input.fuzzy_error = component(input->fuzzy_error, axis);
        velocity_input.neural_residual = component(input->neural_residual, axis);
        velocity_input.dt = input->dt;
        velocity_input.enable = 1;
        if (mosim_pid_step(&params->velocity[axis], &working_state.velocity[axis],
                           &velocity_input, &velocity_output) != 0) return -1;
        set_component(&acceleration, axis, velocity_output.command);
        set_component(&output->position_error_enu_m, axis, reference_position - position);
        set_component(&output->velocity_error_enu_mps, axis,
                      velocity_input.setpoint - velocity);
        set_component(&output->scheduled_gain, axis, velocity_output.scheduled_gain);
        output->saturated = output->saturated || position_output.saturated ||
                            velocity_output.saturated;
    }

    acceleration.z += params->gravity_mps2;
    horizontal = hypot(acceleration.x, acceleration.y);
    horizontal_limit = fmax(acceleration.z, 0.0) * tan(params->max_tilt_rad);
    if (horizontal > horizontal_limit && horizontal > 1.0e-12) {
        const double scale = horizontal_limit / horizontal;
        acceleration.x *= scale;
        acceleration.y *= scale;
        output->saturated = 1;
    }
    b3 = normalize_vec3(acceleration, vec3(0.0, 0.0, 1.0));
    b1d = vec3(cos(input->reference_yaw_enu_rad),
               sin(input->reference_yaw_enu_rad), 0.0);
    b2 = cross(b3, b1d);
    if (norm(b2) <= 1.0e-9) b2 = cross(b3, vec3(0.0, 1.0, 0.0));
    b2 = normalize_vec3(b2, vec3(0.0, 1.0, 0.0));
    b1 = normalize_vec3(cross(b2, b3), b1d);
    output->desired_attitude_enu_flu_wxyz = quat_from_columns(b1, b2, b3);
    thrust = params->mass_kg * norm(acceleration);
    output->desired_collective_thrust_n = clamp_value(
        thrust, params->min_collective_thrust_n,
        params->max_collective_thrust_n);
    if (fabs(output->desired_collective_thrust_n - thrust) > 1.0e-12)
        output->saturated = 1;
    output->desired_acceleration_enu_mps2 = acceleration;
    output->status_code = 0;
    *state = working_state;
    return 0;
}
