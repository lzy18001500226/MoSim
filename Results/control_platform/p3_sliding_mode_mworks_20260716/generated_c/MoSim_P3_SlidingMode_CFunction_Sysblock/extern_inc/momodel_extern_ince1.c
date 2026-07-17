#include "MoSim_P3_SlidingMode_CFunction_Sysblock.h"
/*** Current Block Name: cFunction ***/
enum MosimSlidingModeControllerId {
    MOSIM_SMC_INTEGRAL = 1,
    MOSIM_SMC_TERMINAL = 2,
    MOSIM_SMC_NONSINGULAR_TERMINAL = 3,
    MOSIM_SMC_SUPER_TWISTING = 4,
    MOSIM_SMC_ADAPTIVE = 5,
    MOSIM_SMC_FUZZY = 6
};

typedef struct {
    double dt;
    double position[3];
    double velocity[3];
    double reference_position[3];
    double reference_velocity[3];
    double reference_acceleration[3];
    double reference_yaw;
    int enable;
    int reset;
} MosimSlidingModeInput;

typedef struct {
    double lambda[3];
    double linear_gain[3];
    double reaching_gain[3];
    double boundary_layer[3];
    double integral_gain[3];
    double integral_limit[3];
    double terminal_alpha[3];
    double nonsingular_gain[3];
    double super_twisting_k1[3];
    double super_twisting_k2[3];
    double adaptive_rate[3];
    double adaptive_limit[3];
    double fuzzy_gain_delta[3];
    double mass_kg;
    double gravity_mps2;
    double hover_percentage;
    double max_tilt_rad;
    double min_collective_thrust_n;
    double max_collective_thrust_n;
} MosimSlidingModeParams;

typedef struct {
    double position_error_integral[3];
    double super_twisting_integral[3];
    double adaptive_reaching_gain[3];
} MosimSlidingModeState;

typedef struct {
    double desired_acceleration[3];
    double desired_attitude_wxyz[4];
    double normalized_thrust;
    double collective_thrust_n;
    double sliding_surface[3];
    double auxiliary_state[3];
    double effective_reaching_gain[3];
    int saturated;
    int status_code;
} MosimSlidingModeOutput;

void mosim_sliding_mode_default_params(MosimSlidingModeParams *params);
void mosim_sliding_mode_reset(
    const MosimSlidingModeParams *params,
    MosimSlidingModeState *state);
int mosim_sliding_mode_step(
    int controller_id,
    const MosimSlidingModeParams *params,
    MosimSlidingModeState *state,
    const MosimSlidingModeInput *input,
    MosimSlidingModeOutput *output);




#include <math.h>
#include <stddef.h>
#include <string.h>

static double clamp_value(double value, double lower, double upper)
{
    if (value < lower) return lower;
    if (value > upper) return upper;
    return value;
}

static double signed_power(double value, double exponent)
{
    if (value > 0.0) return pow(value, exponent);
    if (value < 0.0) return -pow(-value, exponent);
    return 0.0;
}

static double boundary_sign(double value, double width)
{
    return clamp_value(value / fmax(width, 1.0e-9), -1.0, 1.0);
}

static int finite3(const double value[3])
{
    return isfinite(value[0]) && isfinite(value[1]) && isfinite(value[2]);
}

static int params_valid(const MosimSlidingModeParams *params)
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
        if (!isfinite(params->lambda[axis]) || params->lambda[axis] <= 0.0 ||
            !isfinite(params->linear_gain[axis]) || params->linear_gain[axis] < 0.0 ||
            !isfinite(params->reaching_gain[axis]) || params->reaching_gain[axis] < 0.0 ||
            !isfinite(params->boundary_layer[axis]) || params->boundary_layer[axis] <= 0.0 ||
            !isfinite(params->integral_gain[axis]) || params->integral_gain[axis] < 0.0 ||
            !isfinite(params->integral_limit[axis]) || params->integral_limit[axis] < 0.0 ||
            !isfinite(params->terminal_alpha[axis]) || params->terminal_alpha[axis] <= 0.0 ||
            params->terminal_alpha[axis] >= 1.0 ||
            !isfinite(params->nonsingular_gain[axis]) || params->nonsingular_gain[axis] < 0.0 ||
            !isfinite(params->super_twisting_k1[axis]) || params->super_twisting_k1[axis] < 0.0 ||
            !isfinite(params->super_twisting_k2[axis]) || params->super_twisting_k2[axis] < 0.0 ||
            !isfinite(params->adaptive_rate[axis]) || params->adaptive_rate[axis] < 0.0 ||
            !isfinite(params->adaptive_limit[axis]) ||
            params->adaptive_limit[axis] < params->reaching_gain[axis] ||
            !isfinite(params->fuzzy_gain_delta[axis]) || params->fuzzy_gain_delta[axis] < 0.0) return 0;
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
    const MosimSlidingModeParams *params,
    const MosimSlidingModeInput *input,
    MosimSlidingModeOutput *output)
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
    if (normalize3(b2) != 0) return -4;
    cross3(b2, b3, b1);
    for (axis = 0; axis < 3; ++axis) {
        rotation[axis][0] = b1[axis];
        rotation[axis][1] = b2[axis];
        rotation[axis][2] = b3[axis];
    }
    quaternion_from_rotation(rotation, output->desired_attitude_wxyz);
    output->collective_thrust_n = clamp_value(
        force_norm, params->min_collective_thrust_n, params->max_collective_thrust_n);
    if (fabs(output->collective_thrust_n - force_norm) > 1.0e-12) output->saturated = 1;
    output->normalized_thrust = clamp_value(
        output->collective_thrust_n /
            (params->mass_kg * params->gravity_mps2 / params->hover_percentage),
        0.0, 1.0);
    return 0;
}

void mosim_sliding_mode_default_params(MosimSlidingModeParams *params)
{
    const MosimSlidingModeParams defaults = {
        {4.0, 4.0, 2.0}, {2.75, 2.75, 2.0}, {0.08, 0.08, 0.08}, {0.35, 0.35, 0.35},
        {0.08, 0.08, 0.08}, {0.20, 0.20, 0.20}, {0.90, 0.90, 0.92},
        {0.10, 0.10, 0.10}, {1.6, 1.6, 2.0}, {1.2, 1.2, 1.5},
        {0.04, 0.04, 0.04}, {0.30, 0.30, 0.35}, {0.04, 0.04, 0.04},
        0.67, 9.80665, 0.291, 0.5235987755982988, 0.0, 16.0
    };
    if (params != NULL) *params = defaults;
}

void mosim_sliding_mode_reset(
    const MosimSlidingModeParams *params,
    MosimSlidingModeState *state)
{
    int axis;
    if (state == NULL) return;
    memset(state, 0, sizeof(*state));
    if (params != NULL) {
        for (axis = 0; axis < 3; ++axis) {
            state->adaptive_reaching_gain[axis] = params->reaching_gain[axis];
        }
    }
}

static void controller_axis_step(
    int controller_id,
    int axis,
    const MosimSlidingModeParams *params,
    MosimSlidingModeState *state,
    const MosimSlidingModeInput *input,
    MosimSlidingModeOutput *output)
{
    const double position_error = input->reference_position[axis] - input->position[axis];
    const double velocity_error = input->reference_velocity[axis] - input->velocity[axis];
    double sliding = velocity_error + params->lambda[axis] * position_error;
    double robust;
    double effective_gain = params->reaching_gain[axis];
    if (controller_id == MOSIM_SMC_INTEGRAL) {
        state->position_error_integral[axis] = clamp_value(
            state->position_error_integral[axis] + position_error * input->dt,
            -params->integral_limit[axis], params->integral_limit[axis]);
        sliding += params->integral_gain[axis] * state->position_error_integral[axis];
    } else if (controller_id == MOSIM_SMC_TERMINAL) {
        sliding = velocity_error + params->lambda[axis] *
            signed_power(position_error, params->terminal_alpha[axis]);
    } else if (controller_id == MOSIM_SMC_NONSINGULAR_TERMINAL) {
        sliding += params->nonsingular_gain[axis] * signed_power(position_error, 1.5);
    } else if (controller_id == MOSIM_SMC_SUPER_TWISTING) {
        const double sign = boundary_sign(sliding, params->boundary_layer[axis]);
        state->super_twisting_integral[axis] = clamp_value(
            state->super_twisting_integral[axis] + params->super_twisting_k2[axis] * sign * input->dt,
            -params->adaptive_limit[axis], params->adaptive_limit[axis]);
        robust = params->super_twisting_k1[axis] * sqrt(fabs(sliding)) * sign +
            state->super_twisting_integral[axis];
        output->sliding_surface[axis] = sliding;
        output->auxiliary_state[axis] = state->super_twisting_integral[axis];
        output->effective_reaching_gain[axis] = params->super_twisting_k1[axis];
        output->desired_acceleration[axis] = input->reference_acceleration[axis] +
            params->lambda[axis] * velocity_error + params->linear_gain[axis] * sliding + robust;
        return;
    } else if (controller_id == MOSIM_SMC_ADAPTIVE) {
        state->adaptive_reaching_gain[axis] = clamp_value(
            state->adaptive_reaching_gain[axis] +
                params->adaptive_rate[axis] * (fabs(sliding) - 0.05) * input->dt,
            params->reaching_gain[axis], params->adaptive_limit[axis]);
        effective_gain = state->adaptive_reaching_gain[axis];
    } else if (controller_id == MOSIM_SMC_FUZZY) {
        const double normalized_error = clamp_value(
            fabs(sliding) / (4.0 * params->boundary_layer[axis]), 0.0, 1.0);
        effective_gain += params->fuzzy_gain_delta[axis] *
            normalized_error * (2.0 - normalized_error);
    }
    robust = effective_gain * boundary_sign(sliding, params->boundary_layer[axis]);
    output->sliding_surface[axis] = sliding;
    output->auxiliary_state[axis] = state->position_error_integral[axis];
    output->effective_reaching_gain[axis] = effective_gain;
    output->desired_acceleration[axis] = input->reference_acceleration[axis] +
        params->lambda[axis] * velocity_error + params->linear_gain[axis] * sliding + robust;
}

int mosim_sliding_mode_step(
    int controller_id,
    const MosimSlidingModeParams *params,
    MosimSlidingModeState *state,
    const MosimSlidingModeInput *input,
    MosimSlidingModeOutput *output)
{
    int axis;
    int rc;
    if (params == NULL || state == NULL || input == NULL || output == NULL) return -1;
    memset(output, 0, sizeof(*output));
    output->desired_attitude_wxyz[0] = 1.0;
    if (input->reset) mosim_sliding_mode_reset(params, state);
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
    if (controller_id < MOSIM_SMC_INTEGRAL || controller_id > MOSIM_SMC_FUZZY) {
        output->status_code = -2;
        return -2;
    }
    for (axis = 0; axis < 3; ++axis) {
        controller_axis_step(controller_id, axis, params, state, input, output);
    }
    output->desired_acceleration[2] += params->gravity_mps2;
    rc = command_from_acceleration(params, input, output);
    if (rc != 0) {
        output->status_code = rc;
        return rc;
    }
    return 0;
}
void MosimSlidingModeStepScalar(
    double controller_id,
    double dt,
    double position_x,
    double position_y,
    double position_z,
    double velocity_x,
    double velocity_y,
    double velocity_z,
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
    double mass_kg,
    double gravity_mps2,
    double hover_percentage,
    double max_tilt_rad,
    double min_collective_thrust_n,
    double max_collective_thrust_n,
    double enable,
    double reset,
    double *desired_attitude_w,
    double *desired_attitude_x,
    double *desired_attitude_y,
    double *desired_attitude_z,
    double *normalized_thrust,
    double *collective_thrust_n,
    double *desired_acceleration_x,
    double *desired_acceleration_y,
    double *desired_acceleration_z,
    double *sliding_surface_x,
    double *sliding_surface_y,
    double *sliding_surface_z,
    double *auxiliary_state_x,
    double *auxiliary_state_y,
    double *auxiliary_state_z,
    double *effective_reaching_gain_x,
    double *effective_reaching_gain_y,
    double *effective_reaching_gain_z,
    double *saturated,
    double *status_code)
{
    static MosimSlidingModeState states[7];
    MosimSlidingModeParams params;
    MosimSlidingModeInput input;
    MosimSlidingModeOutput output;
    int id = (int)controller_id;
    int result;
    memset(&input, 0, sizeof(input));
    input.dt = dt;
    input.position[0] = position_x; input.position[1] = position_y; input.position[2] = position_z;
    input.velocity[0] = velocity_x; input.velocity[1] = velocity_y; input.velocity[2] = velocity_z;
    input.reference_position[0] = reference_position_x;
    input.reference_position[1] = reference_position_y;
    input.reference_position[2] = reference_position_z;
    input.reference_velocity[0] = reference_velocity_x;
    input.reference_velocity[1] = reference_velocity_y;
    input.reference_velocity[2] = reference_velocity_z;
    input.reference_acceleration[0] = reference_acceleration_x;
    input.reference_acceleration[1] = reference_acceleration_y;
    input.reference_acceleration[2] = reference_acceleration_z;
    input.reference_yaw = reference_yaw;
    input.enable = enable != 0.0;
    input.reset = reset != 0.0;
    mosim_sliding_mode_default_params(&params);
    params.mass_kg = mass_kg;
    params.gravity_mps2 = gravity_mps2;
    params.hover_percentage = hover_percentage;
    params.max_tilt_rad = max_tilt_rad;
    params.min_collective_thrust_n = min_collective_thrust_n;
    params.max_collective_thrust_n = max_collective_thrust_n;
    if (id < 1 || id > 6) id = 0;
    result = mosim_sliding_mode_step(id, &params, &states[id], &input, &output);
    if (result != 0) {
        memset(&output, 0, sizeof(output));
        output.desired_attitude_wxyz[0] = 1.0;
        output.status_code = result;
    }
    *desired_attitude_w = output.desired_attitude_wxyz[0];
    *desired_attitude_x = output.desired_attitude_wxyz[1];
    *desired_attitude_y = output.desired_attitude_wxyz[2];
    *desired_attitude_z = output.desired_attitude_wxyz[3];
    *normalized_thrust = output.normalized_thrust;
    *collective_thrust_n = output.collective_thrust_n;
    *desired_acceleration_x = output.desired_acceleration[0];
    *desired_acceleration_y = output.desired_acceleration[1];
    *desired_acceleration_z = output.desired_acceleration[2];
    *sliding_surface_x = output.sliding_surface[0];
    *sliding_surface_y = output.sliding_surface[1];
    *sliding_surface_z = output.sliding_surface[2];
    *auxiliary_state_x = output.auxiliary_state[0];
    *auxiliary_state_y = output.auxiliary_state[1];
    *auxiliary_state_z = output.auxiliary_state[2];
    *effective_reaching_gain_x = output.effective_reaching_gain[0];
    *effective_reaching_gain_y = output.effective_reaching_gain[1];
    *effective_reaching_gain_z = output.effective_reaching_gain[2];
    *saturated = (double)output.saturated;
    *status_code = (double)output.status_code;
}
