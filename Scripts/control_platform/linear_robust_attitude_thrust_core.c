#include "linear_robust_attitude_thrust_core.h"

#include <math.h>
#include <stddef.h>
#include <string.h>

static double clamp_value(double value, double lower, double upper)
{
    if (value < lower) return lower;
    if (value > upper) return upper;
    return value;
}

static int finite3(const double value[3])
{
    return isfinite(value[0]) && isfinite(value[1]) && isfinite(value[2]);
}

static int params_valid(const MosimLinearRobustParams *params)
{
    int axis;
    if (!isfinite(params->mass_kg) || params->mass_kg <= 0.0 ||
        !isfinite(params->gravity_mps2) || params->gravity_mps2 <= 0.0 ||
        !isfinite(params->hover_percentage) || params->hover_percentage <= 0.0 ||
        params->hover_percentage > 1.0 ||
        !isfinite(params->max_tilt_rad) || params->max_tilt_rad <= 0.0 ||
        params->max_tilt_rad >= 1.5707963267948966 ||
        !isfinite(params->min_collective_thrust_n) ||
        !isfinite(params->max_collective_thrust_n) ||
        params->min_collective_thrust_n < 0.0 ||
        params->max_collective_thrust_n <= params->min_collective_thrust_n) return 0;
    for (axis = 0; axis < 3; ++axis) {
        if (!isfinite(params->position_gain[axis]) || params->position_gain[axis] < 0.0 ||
            !isfinite(params->velocity_gain[axis]) || params->velocity_gain[axis] < 0.0 ||
            !isfinite(params->observer_position_gain[axis]) ||
            params->observer_position_gain[axis] < 0.0 || params->observer_position_gain[axis] > 1.0 ||
            !isfinite(params->observer_velocity_gain[axis]) ||
            params->observer_velocity_gain[axis] < 0.0 || params->observer_velocity_gain[axis] > 1.0 ||
            !isfinite(params->backstepping_k1[axis]) || params->backstepping_k1[axis] < 0.0 ||
            !isfinite(params->backstepping_k2[axis]) || params->backstepping_k2[axis] < 0.0 ||
            !isfinite(params->adaptive_gain[axis]) || params->adaptive_gain[axis] < 0.0 ||
            !isfinite(params->adaptive_limit[axis]) || params->adaptive_limit[axis] < 0.0) return 0;
    }
    return 1;
}

static double norm3(const double value[3])
{
    return sqrt(value[0] * value[0] + value[1] * value[1] + value[2] * value[2]);
}

static void cross3(const double a[3], const double b[3], double out[3])
{
    out[0] = a[1] * b[2] - a[2] * b[1];
    out[1] = a[2] * b[0] - a[0] * b[2];
    out[2] = a[0] * b[1] - a[1] * b[0];
}

static int normalize3(double value[3])
{
    const double length = norm3(value);
    int axis;
    if (length <= 1.0e-12) return -1;
    for (axis = 0; axis < 3; ++axis) value[axis] /= length;
    return 0;
}

static void quaternion_from_rotation(const double rotation[3][3], double q[4])
{
    const double trace = rotation[0][0] + rotation[1][1] + rotation[2][2];
    if (trace > 0.0) {
        const double scale = 2.0 * sqrt(trace + 1.0);
        q[0] = 0.25 * scale;
        q[1] = (rotation[2][1] - rotation[1][2]) / scale;
        q[2] = (rotation[0][2] - rotation[2][0]) / scale;
        q[3] = (rotation[1][0] - rotation[0][1]) / scale;
    } else if (rotation[0][0] > rotation[1][1] && rotation[0][0] > rotation[2][2]) {
        const double scale = 2.0 * sqrt(1.0 + rotation[0][0] - rotation[1][1] - rotation[2][2]);
        q[0] = (rotation[2][1] - rotation[1][2]) / scale;
        q[1] = 0.25 * scale;
        q[2] = (rotation[0][1] + rotation[1][0]) / scale;
        q[3] = (rotation[0][2] + rotation[2][0]) / scale;
    } else if (rotation[1][1] > rotation[2][2]) {
        const double scale = 2.0 * sqrt(1.0 + rotation[1][1] - rotation[0][0] - rotation[2][2]);
        q[0] = (rotation[0][2] - rotation[2][0]) / scale;
        q[1] = (rotation[0][1] + rotation[1][0]) / scale;
        q[2] = 0.25 * scale;
        q[3] = (rotation[1][2] + rotation[2][1]) / scale;
    } else {
        const double scale = 2.0 * sqrt(1.0 + rotation[2][2] - rotation[0][0] - rotation[1][1]);
        q[0] = (rotation[1][0] - rotation[0][1]) / scale;
        q[1] = (rotation[0][2] + rotation[2][0]) / scale;
        q[2] = (rotation[1][2] + rotation[2][1]) / scale;
        q[3] = 0.25 * scale;
    }
    if (q[0] < 0.0) {
        q[0] = -q[0]; q[1] = -q[1]; q[2] = -q[2]; q[3] = -q[3];
    }
}

static int command_from_acceleration(
    const MosimLinearRobustParams *params,
    const MosimLinearRobustInput *input,
    MosimLinearRobustOutput *output)
{
    double force[3];
    double b1_reference[3];
    double b1[3];
    double b2[3];
    double b3[3];
    double rotation[3][3];
    double force_norm;
    double horizontal_acceleration;
    double horizontal_limit;
    int axis;
    horizontal_acceleration = hypot(output->desired_acceleration[0], output->desired_acceleration[1]);
    horizontal_limit = fmax(0.0, output->desired_acceleration[2]) * tan(params->max_tilt_rad);
    if (horizontal_acceleration > horizontal_limit && horizontal_acceleration > 1.0e-12) {
        const double scale = horizontal_limit / horizontal_acceleration;
        output->desired_acceleration[0] *= scale;
        output->desired_acceleration[1] *= scale;
        output->saturated = 1;
    }
    for (axis = 0; axis < 3; ++axis) {
        force[axis] = params->mass_kg * output->desired_acceleration[axis];
        b3[axis] = force[axis];
    }
    force_norm = norm3(force);
    if (normalize3(b3) != 0) return -4;
    b1_reference[0] = cos(input->reference_yaw);
    b1_reference[1] = sin(input->reference_yaw);
    b1_reference[2] = 0.0;
    cross3(b3, b1_reference, b2);
    if (normalize3(b2) != 0) {
        b1_reference[0] = -sin(input->reference_yaw);
        b1_reference[1] = cos(input->reference_yaw);
        cross3(b3, b1_reference, b2);
        if (normalize3(b2) != 0) return -4;
    }
    cross3(b2, b3, b1);
    for (axis = 0; axis < 3; ++axis) {
        rotation[axis][0] = b1[axis];
        rotation[axis][1] = b2[axis];
        rotation[axis][2] = b3[axis];
    }
    quaternion_from_rotation(rotation, output->desired_attitude_wxyz);
    output->collective_thrust_n = clamp_value(
        force_norm,
        params->min_collective_thrust_n,
        params->max_collective_thrust_n);
    if (fabs(output->collective_thrust_n - force_norm) > 1.0e-12) output->saturated = 1;
    output->normalized_thrust = clamp_value(
        output->collective_thrust_n /
            (params->mass_kg * params->gravity_mps2 / params->hover_percentage),
        0.0,
        1.0);
    return 0;
}

void mosim_linear_robust_default_params(MosimLinearRobustParams *params)
{
    const MosimLinearRobustParams defaults = {
        {11.0, 11.0, 4.0}, {6.5, 6.5, 4.0},
        {0.65, 0.65, 0.70}, {0.45, 0.45, 0.50},
        {4.0, 4.0, 2.0}, {2.75, 2.75, 2.0},
        {0.03, 0.03, 0.04}, {0.15, 0.15, 0.20},
        0.67, 9.80665, 0.291, 0.5235987755982988, 0.0, 16.0
    };
    if (params != NULL) *params = defaults;
}

void mosim_linear_robust_reset(MosimLinearRobustState *state)
{
    if (state != NULL) memset(state, 0, sizeof(*state));
}

static void lqg_step(
    const MosimLinearRobustParams *params,
    MosimLinearRobustState *state,
    const MosimLinearRobustInput *input,
    MosimLinearRobustOutput *output)
{
    int initialized_now = 0;
    int axis;
    if (!state->observer_initialized) {
        memcpy(state->estimated_position, input->position, sizeof(state->estimated_position));
        memcpy(state->estimated_velocity, input->velocity, sizeof(state->estimated_velocity));
        state->observer_initialized = 1;
        initialized_now = 1;
    }
    for (axis = 0; axis < 3; ++axis) {
        if (!initialized_now) {
            const double predicted_position =
                state->estimated_position[axis] + state->estimated_velocity[axis] * input->dt;
            const double predicted_velocity =
                state->estimated_velocity[axis] + state->previous_command_acceleration[axis] * input->dt;
            state->estimated_position[axis] = predicted_position +
                params->observer_position_gain[axis] * (input->position[axis] - predicted_position);
            state->estimated_velocity[axis] = predicted_velocity +
                params->observer_velocity_gain[axis] * (input->velocity[axis] - predicted_velocity);
        }
        output->desired_acceleration[axis] = input->reference_acceleration[axis] +
            params->position_gain[axis] *
                (input->reference_position[axis] - state->estimated_position[axis]) +
            params->velocity_gain[axis] *
                (input->reference_velocity[axis] - state->estimated_velocity[axis]);
    }
}

static void nominal_nonlinear_step(
    int controller_id,
    const MosimLinearRobustParams *params,
    MosimLinearRobustState *state,
    const MosimLinearRobustInput *input,
    MosimLinearRobustOutput *output)
{
    int axis;
    for (axis = 0; axis < 3; ++axis) {
        const double position_error = input->reference_position[axis] - input->position[axis];
        const double velocity_error = input->reference_velocity[axis] - input->velocity[axis];
        double feedback = params->position_gain[axis] * position_error +
            params->velocity_gain[axis] * velocity_error;
        if (controller_id == MOSIM_LINEAR_ROBUST_ADAPTIVE_BACKSTEPPING) {
            const double sliding = velocity_error + params->backstepping_k1[axis] * position_error;
            state->adaptive_disturbance[axis] = clamp_value(
                state->adaptive_disturbance[axis] +
                    params->adaptive_gain[axis] * sliding * input->dt,
                -params->adaptive_limit[axis],
                params->adaptive_limit[axis]);
            feedback = params->backstepping_k1[axis] * velocity_error +
                params->backstepping_k2[axis] * sliding + state->adaptive_disturbance[axis];
        }
        output->desired_acceleration[axis] = input->reference_acceleration[axis] + feedback;
        if (controller_id == MOSIM_LINEAR_ROBUST_PASSIVITY) {
            output->storage_function += 0.5 * params->mass_kg * velocity_error * velocity_error +
                0.5 * params->position_gain[axis] * position_error * position_error;
        }
    }
}

int mosim_linear_robust_step(
    int controller_id,
    const MosimLinearRobustParams *params,
    MosimLinearRobustState *state,
    const MosimLinearRobustInput *input,
    MosimLinearRobustOutput *output)
{
    int rc;
    int axis;
    if (params == NULL || state == NULL || input == NULL || output == NULL) return -1;
    memset(output, 0, sizeof(*output));
    output->desired_attitude_wxyz[0] = 1.0;
    if (input->reset) mosim_linear_robust_reset(state);
    if (!input->enable) {
        output->status_code = 1;
        return 0;
    }
    if (!params_valid(params)) {
        output->status_code = -5;
        return -5;
    }
    if (!isfinite(input->dt) || input->dt <= 0.0 || input->dt > 0.1 ||
        !finite3(input->position) || !finite3(input->velocity) ||
        !finite3(input->reference_position) || !finite3(input->reference_velocity) ||
        !finite3(input->reference_acceleration) || !isfinite(input->reference_yaw)) {
        output->status_code = -3;
        return -3;
    }
    if (controller_id == MOSIM_LINEAR_ROBUST_LQG) {
        lqg_step(params, state, input, output);
    } else if (controller_id == MOSIM_LINEAR_ROBUST_FEEDBACK_LINEARIZATION ||
               controller_id == MOSIM_LINEAR_ROBUST_PASSIVITY ||
               controller_id == MOSIM_LINEAR_ROBUST_ADAPTIVE_BACKSTEPPING) {
        nominal_nonlinear_step(controller_id, params, state, input, output);
    } else {
        output->status_code = -2;
        return -2;
    }
    output->desired_acceleration[2] += params->gravity_mps2;
    rc = command_from_acceleration(params, input, output);
    if (rc != 0) {
        output->status_code = rc;
        return rc;
    }
    memcpy(output->estimated_position, state->estimated_position, sizeof(output->estimated_position));
    memcpy(output->estimated_velocity, state->estimated_velocity, sizeof(output->estimated_velocity));
    memcpy(output->adaptive_disturbance, state->adaptive_disturbance, sizeof(output->adaptive_disturbance));
    for (axis = 0; axis < 3; ++axis) {
        state->previous_command_acceleration[axis] =
            output->desired_acceleration[axis] - (axis == 2 ? params->gravity_mps2 : 0.0);
    }
    return 0;
}
