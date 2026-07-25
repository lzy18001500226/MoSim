#include "enhancement_attitude_thrust_core.h"

#include <math.h>
#include <stddef.h>
#include <string.h>

static double clamp_value(double value, double lower, double upper)
{
    if (value < lower) return lower;
    if (value > upper) return upper;
    return value;
}

static double norm3(const double value[3])
{
    return sqrt(value[0] * value[0] + value[1] * value[1] + value[2] * value[2]);
}

static int finite3(const double value[3])
{
    return isfinite(value[0]) && isfinite(value[1]) && isfinite(value[2]);
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

static void quaternion_from_rotation(double rotation[3][3], double q[4])
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

static double signed_power(double value, double alpha)
{
    if (fabs(value) < 1.0e-12) return 0.0;
    return copysign(pow(fabs(value), alpha), value);
}

static int params_valid(const MosimEnhancementParams *params)
{
    int axis;
    if (!isfinite(params->l1_filter_time_constant) || params->l1_filter_time_constant <= 0.0 ||
        !isfinite(params->adrc_nonlinear_alpha) || params->adrc_nonlinear_alpha <= 0.0 || params->adrc_nonlinear_alpha > 1.0 ||
        !isfinite(params->schedule_error_threshold) || params->schedule_error_threshold <= 0.0 ||
        !isfinite(params->schedule_high_gain_scale) || params->schedule_high_gain_scale < 1.0 ||
        !isfinite(params->ilc_forgetting_factor) || params->ilc_forgetting_factor < 0.0 || params->ilc_forgetting_factor > 1.0 ||
        !isfinite(params->mass_kg) || params->mass_kg <= 0.0 ||
        !isfinite(params->gravity_mps2) || params->gravity_mps2 <= 0.0 ||
        !isfinite(params->hover_percentage) || params->hover_percentage <= 0.0 || params->hover_percentage > 1.0 ||
        !isfinite(params->max_tilt_rad) || params->max_tilt_rad <= 0.0 || params->max_tilt_rad >= 1.5707963267948966 ||
        !isfinite(params->min_collective_thrust_n) || !isfinite(params->max_collective_thrust_n) ||
        params->min_collective_thrust_n < 0.0 || params->max_collective_thrust_n <= params->min_collective_thrust_n) return 0;
    for (axis = 0; axis < 3; ++axis) {
        if (!isfinite(params->position_gain[axis]) || params->position_gain[axis] <= 0.0 ||
            !isfinite(params->velocity_gain[axis]) || params->velocity_gain[axis] < 0.0 ||
            !isfinite(params->acceleration_limit[axis]) || params->acceleration_limit[axis] <= 0.0 ||
            !isfinite(params->compensation_limit[axis]) || params->compensation_limit[axis] <= 0.0 ||
            !isfinite(params->observer_bandwidth[axis]) || params->observer_bandwidth[axis] <= 0.0 ||
            !isfinite(params->l1_adaptation_gain[axis]) || params->l1_adaptation_gain[axis] < 0.0 ||
            !isfinite(params->awff_drag_gain[axis]) || params->awff_drag_gain[axis] < 0.0 ||
            !isfinite(params->indi_gain[axis]) || params->indi_gain[axis] < 0.0 ||
            !isfinite(params->indi_increment_limit[axis]) || params->indi_increment_limit[axis] <= 0.0 ||
            !isfinite(params->adrc_td_bandwidth[axis]) || params->adrc_td_bandwidth[axis] <= 0.0 ||
            !isfinite(params->adrc_eso_bandwidth[axis]) || params->adrc_eso_bandwidth[axis] <= 0.0 ||
            !isfinite(params->ilc_learning_gain[axis]) || params->ilc_learning_gain[axis] < 0.0) return 0;
    }
    return 1;
}

void mosim_enhancement_default_params(MosimEnhancementParams *params)
{
    int axis;
    if (params == NULL) return;
    memset(params, 0, sizeof(*params));
    for (axis = 0; axis < 3; ++axis) {
        params->position_gain[axis] = axis == 2 ? 4.0 : 11.0;
        params->velocity_gain[axis] = axis == 2 ? 4.0 : 6.5;
        params->acceleration_limit[axis] = axis == 2 ? 2.5 : 4.0;
        params->compensation_limit[axis] = axis == 2 ? 1.2 : 1.5;
        params->observer_bandwidth[axis] = 5.0;
        params->l1_adaptation_gain[axis] = 0.32;
        params->awff_drag_gain[axis] = axis == 2 ? 0.05 : 0.12;
        params->indi_gain[axis] = axis == 2 ? 0.08 : 0.12;
        params->indi_increment_limit[axis] = axis == 2 ? 0.20 : 0.35;
        params->adrc_td_bandwidth[axis] = 4.0;
        params->adrc_eso_bandwidth[axis] = 8.0;
        params->ilc_learning_gain[axis] = 0.08;
    }
    params->l1_filter_time_constant = 0.20;
    params->adrc_nonlinear_alpha = 0.75;
    params->schedule_error_threshold = 0.35;
    params->schedule_high_gain_scale = 1.35;
    params->ilc_forgetting_factor = 0.995;
    params->mass_kg = 1.0;
    params->gravity_mps2 = 9.80665;
    params->hover_percentage = 0.37;
    params->max_tilt_rad = 0.65;
    params->min_collective_thrust_n = 0.0;
    params->max_collective_thrust_n = 2.5 * params->mass_kg * params->gravity_mps2;
}

void mosim_enhancement_reset(MosimEnhancementState *state)
{
    if (state != NULL) memset(state, 0, sizeof(*state));
}

static int finalize_output(
    const MosimEnhancementParams *params,
    const MosimEnhancementInput *input,
    MosimEnhancementOutput *output)
{
    double force[3];
    double body_x_hint[3] = {cos(input->reference_yaw), sin(input->reference_yaw), 0.0};
    double body_x[3];
    double body_y[3];
    double body_z[3];
    double rotation[3][3];
    double horizontal;
    double max_horizontal;
    double collective;
    int axis;

    horizontal = hypot(output->desired_acceleration[0], output->desired_acceleration[1]);
    max_horizontal = tan(params->max_tilt_rad) * fmax(params->gravity_mps2 + output->desired_acceleration[2], 0.1);
    if (horizontal > max_horizontal && horizontal > 1.0e-12) {
        const double scale = max_horizontal / horizontal;
        output->desired_acceleration[0] *= scale;
        output->desired_acceleration[1] *= scale;
        output->saturated = 1;
    }
    for (axis = 0; axis < 3; ++axis) force[axis] = params->mass_kg * output->desired_acceleration[axis];
    force[2] += params->mass_kg * params->gravity_mps2;
    body_z[0] = force[0]; body_z[1] = force[1]; body_z[2] = force[2];
    if (normalize3(body_z) != 0) return -1;
    cross3(body_z, body_x_hint, body_y);
    if (normalize3(body_y) != 0) return -1;
    cross3(body_y, body_z, body_x);
    if (normalize3(body_x) != 0) return -1;
    for (axis = 0; axis < 3; ++axis) {
        rotation[axis][0] = body_x[axis];
        rotation[axis][1] = body_y[axis];
        rotation[axis][2] = body_z[axis];
    }
    quaternion_from_rotation(rotation, output->desired_attitude_wxyz);
    collective = norm3(force);
    output->collective_thrust_n = clamp_value(collective, params->min_collective_thrust_n, params->max_collective_thrust_n);
    if (fabs(output->collective_thrust_n - collective) > 1.0e-12) output->saturated = 1;
    output->normalized_thrust = clamp_value(
        params->hover_percentage * output->collective_thrust_n / (params->mass_kg * params->gravity_mps2), 0.0, 1.0);
    return 0;
}

int mosim_enhancement_step(
    int controller_id,
    const MosimEnhancementParams *params,
    MosimEnhancementState *state,
    const MosimEnhancementInput *input,
    MosimEnhancementOutput *output)
{
    double position_error[3];
    double velocity_error[3];
    double error_norm;
    int axis;
    int bin;
    if (params == NULL || state == NULL || input == NULL || output == NULL) return -1;
    memset(output, 0, sizeof(*output));
    if (controller_id < MOSIM_ENHANCEMENT_L1_ADAPTIVE || controller_id > MOSIM_ENHANCEMENT_ILC ||
        !params_valid(params) || !isfinite(input->dt) || input->dt <= 0.0 || input->dt > 0.1 ||
        !finite3(input->position) || !finite3(input->velocity) || !finite3(input->measured_acceleration) ||
        !finite3(input->reference_position) || !finite3(input->reference_velocity) ||
        !finite3(input->reference_acceleration) || !isfinite(input->reference_yaw)) {
        output->status_code = -1;
        return -1;
    }
    if (input->reset) mosim_enhancement_reset(state);
    if (!input->enable) return 0;
    if (input->reset || state->step_count == 0UL) {
        for (axis = 0; axis < 3; ++axis) {
            state->td_position[axis] = input->reference_position[axis];
            state->td_velocity[axis] = input->reference_velocity[axis];
            state->eso_position[axis] = input->position[axis];
            state->eso_velocity[axis] = input->velocity[axis];
            state->previous_command_acceleration[axis] = input->measured_acceleration[axis];
        }
    }
    for (axis = 0; axis < 3; ++axis) {
        position_error[axis] = input->reference_position[axis] - input->position[axis];
        velocity_error[axis] = input->reference_velocity[axis] - input->velocity[axis];
        output->nominal_acceleration[axis] = input->reference_acceleration[axis] +
            params->position_gain[axis] * position_error[axis] +
            params->velocity_gain[axis] * velocity_error[axis];
    }
    error_norm = norm3(position_error);
    output->effective_gain_scale = 1.0;
    bin = input->trajectory_phase_bin;
    if (bin < 0) bin = 0;
    if (bin >= MOSIM_ENHANCEMENT_ILC_BINS) bin = MOSIM_ENHANCEMENT_ILC_BINS - 1;

    for (axis = 0; axis < 3; ++axis) {
        const double residual = input->measured_acceleration[axis] - state->previous_command_acceleration[axis];
        double compensation = 0.0;
        if (controller_id == MOSIM_ENHANCEMENT_L1_ADAPTIVE) {
            const double alpha = input->dt /
                (params->l1_filter_time_constant + input->dt);
            state->disturbance_estimate[axis] += alpha *
                (residual - state->disturbance_estimate[axis]);
            compensation = -state->disturbance_estimate[axis];
        } else if (controller_id == MOSIM_ENHANCEMENT_AWFF) {
            const double alpha = clamp_value(input->dt * params->observer_bandwidth[axis], 0.0, 1.0);
            state->disturbance_estimate[axis] += alpha * (residual - state->disturbance_estimate[axis]);
            compensation = params->awff_drag_gain[axis] * input->velocity[axis] - state->disturbance_estimate[axis];
        } else if (controller_id == MOSIM_ENHANCEMENT_COMPLETE_ADRC) {
            const double td_error = state->td_position[axis] - input->reference_position[axis];
            const double td_acceleration = -2.0 * params->adrc_td_bandwidth[axis] * state->td_velocity[axis] -
                params->adrc_td_bandwidth[axis] * params->adrc_td_bandwidth[axis] * td_error;
            const double observer_error = state->eso_position[axis] - input->position[axis];
            const double bandwidth = params->adrc_eso_bandwidth[axis];
            state->td_position[axis] += input->dt * state->td_velocity[axis];
            state->td_velocity[axis] += input->dt * td_acceleration;
            state->eso_position[axis] += input->dt * (state->eso_velocity[axis] - 3.0 * bandwidth * observer_error);
            state->eso_velocity[axis] += input->dt * (state->eso_disturbance[axis] +
                output->nominal_acceleration[axis] - 3.0 * bandwidth * bandwidth * signed_power(observer_error, params->adrc_nonlinear_alpha));
            state->eso_disturbance[axis] += input->dt *
                (-bandwidth * bandwidth * bandwidth * signed_power(observer_error, params->adrc_nonlinear_alpha));
            output->nominal_acceleration[axis] = input->reference_acceleration[axis] +
                params->position_gain[axis] * (state->td_position[axis] - state->eso_position[axis]) +
                params->velocity_gain[axis] * (state->td_velocity[axis] - state->eso_velocity[axis]);
            compensation = -state->eso_disturbance[axis];
            output->observer_state[axis] = state->eso_disturbance[axis];
        } else if (controller_id == MOSIM_ENHANCEMENT_STANDARDIZED_INDI) {
            compensation = clamp_value(
                params->indi_gain[axis] * (output->nominal_acceleration[axis] - input->measured_acceleration[axis]),
                -params->indi_increment_limit[axis], params->indi_increment_limit[axis]);
        } else if (controller_id == MOSIM_ENHANCEMENT_PARAMETER_SCHEDULING) {
            const double blend = clamp_value(error_norm / params->schedule_error_threshold, 0.0, 1.0);
            output->effective_gain_scale = 1.0 + blend * (params->schedule_high_gain_scale - 1.0);
            output->nominal_acceleration[axis] = input->reference_acceleration[axis] +
                output->effective_gain_scale * (params->position_gain[axis] * position_error[axis] +
                params->velocity_gain[axis] * velocity_error[axis]);
        } else {
            compensation = state->ilc_memory[bin][axis];
            state->ilc_memory[bin][axis] = clamp_value(
                params->ilc_forgetting_factor * state->ilc_memory[bin][axis] +
                params->ilc_learning_gain[axis] * position_error[axis],
                -params->compensation_limit[axis], params->compensation_limit[axis]);
            if (input->repeat_complete) {
                state->ilc_memory[bin][axis] *= params->ilc_forgetting_factor;
            }
        }
        compensation = clamp_value(compensation, -params->compensation_limit[axis], params->compensation_limit[axis]);
        output->compensation[axis] = compensation;
        output->observer_state[axis] = controller_id == MOSIM_ENHANCEMENT_COMPLETE_ADRC ?
            output->observer_state[axis] : state->disturbance_estimate[axis];
        output->desired_acceleration[axis] = clamp_value(
            output->nominal_acceleration[axis] + compensation,
            -params->acceleration_limit[axis], params->acceleration_limit[axis]);
        if (fabs(output->desired_acceleration[axis] - (output->nominal_acceleration[axis] + compensation)) > 1.0e-12)
            output->saturated = 1;
        state->previous_command_acceleration[axis] = output->desired_acceleration[axis];
    }
    state->step_count += 1UL;
    if (finalize_output(params, input, output) != 0 || !finite3(output->desired_acceleration)) {
        memset(output, 0, sizeof(*output));
        output->status_code = -2;
        return -2;
    }
    output->status_code = 1;
    return 0;
}
