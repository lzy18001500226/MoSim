#include "learning_attitude_thrust_core.h"

#include <math.h>
#include <stddef.h>
#include <string.h>

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

void mosim_learning_attitude_thrust_reset(MosimLearningAttitudeThrustState *state)
{
    if (state != NULL) memset(state, 0, sizeof(*state));
}

static void build_observation(const MosimLearningAttitudeThrustInput *input,
                              MosimLearningInput *learning)
{
    size_t axis;
    memset(learning, 0, sizeof(*learning));
    for (axis = 0; axis < 3; ++axis) {
        learning->values[axis] = component(input->reference_position_enu_m, axis) -
                                 component(input->position_enu_m, axis);
        learning->values[3 + axis] = component(input->reference_velocity_enu_mps, axis) -
                                     component(input->velocity_enu_mps, axis);
        learning->values[6 + axis] = component(input->reference_acceleration_enu_mps2, axis);
        learning->values[9 + axis] = component(input->velocity_enu_mps, axis);
    }
    learning->enable = input->enable && input->learning_enable;
}

int mosim_learning_attitude_thrust_step(
    MosimLearningAttitudeThrustState *state,
    const MosimLearningAttitudeThrustInput *input,
    MosimLearningAttitudeThrustOutput *output)
{
    MosimLearningInput learning_input;
    MosimPidAttitudeThrustParams params;
    MosimPidAttitudeThrustInput controller_input;
    int inference_result;
    int controller_id = MOSIM_PID_CASCADE;
    size_t axis;
    if (state == NULL || input == NULL || output == NULL) return -1;
    memset(output, 0, sizeof(*output));
    output->mode = input->mode;
    if (input->mode != MOSIM_LEARNING_NEURAL_RESIDUAL &&
        input->mode != MOSIM_LEARNING_RL_GAIN_SCHEDULER) {
        output->status_code = -1;
        output->fallback_active = 1;
        return -1;
    }
    if (input->reset || state->previous_mode != input->mode) {
        mosim_learning_attitude_thrust_reset(state);
        state->previous_mode = input->mode;
    }
    build_observation(input, &learning_input);
    if (input->mode == MOSIM_LEARNING_NEURAL_RESIDUAL) {
        inference_result = mosim_neural_residual_step(&learning_input, &output->learning);
    } else {
        inference_result = mosim_rl_gain_scheduler_step(&learning_input, &output->learning);
        controller_id = MOSIM_PID_GAIN_SCHEDULED;
    }
    output->fallback_active = inference_result != 0 || output->learning.fallback_active;
    if (output->fallback_active) controller_id = MOSIM_PID_CASCADE;

    memset(&controller_input, 0, sizeof(controller_input));
    controller_input.algorithm_id = controller_id;
    controller_input.dt = input->dt;
    controller_input.position_enu_m = input->position_enu_m;
    controller_input.velocity_enu_mps = input->velocity_enu_mps;
    controller_input.attitude_enu_flu_wxyz = input->attitude_enu_flu_wxyz;
    controller_input.angular_velocity_flu_radps = input->angular_velocity_flu_radps;
    controller_input.reference_position_enu_m = input->reference_position_enu_m;
    controller_input.reference_velocity_enu_mps = input->reference_velocity_enu_mps;
    controller_input.reference_acceleration_enu_mps2 = input->reference_acceleration_enu_mps2;
    controller_input.reference_yaw_enu_rad = input->reference_yaw_enu_rad;
    controller_input.enable = input->enable;
    controller_input.reset = input->reset;
    if (input->mode == MOSIM_LEARNING_RL_GAIN_SCHEDULER && !output->fallback_active) {
        for (axis = 0; axis < 3; ++axis) {
            set_component(&controller_input.schedule, axis, output->learning.values[axis]);
        }
    }
    mosim_pid_attitude_thrust_default_params(controller_id, &params);
    params.mass_kg = input->mass_kg;
    params.gravity_mps2 = input->gravity_mps2;
    params.max_tilt_rad = input->max_tilt_rad;
    params.min_collective_thrust_n = input->min_collective_thrust_n;
    params.max_collective_thrust_n = input->max_collective_thrust_n;
    if (!isfinite(input->hover_percentage) || input->hover_percentage <= 0.0 ||
        input->hover_percentage > 1.0) {
        output->status_code = -1;
        output->fallback_active = 1;
        return -1;
    }
    if (controller_id == MOSIM_PID_GAIN_SCHEDULED) {
        for (axis = 0; axis < 3; ++axis) params.velocity[axis].schedule_gain = 2.0;
    }
    if (mosim_pid_attitude_thrust_step(
            &params, &state->controller, &controller_input, &output->control) != 0) {
        output->status_code = -1;
        output->fallback_active = 1;
        return -1;
    }
    if (input->mode == MOSIM_LEARNING_NEURAL_RESIDUAL && !output->fallback_active && input->enable) {
        MosimPidVec3 acceleration = output->control.desired_acceleration_enu_mps2;
        for (axis = 0; axis < 3; ++axis) {
            set_component(&acceleration, axis,
                          component(acceleration, axis) + output->learning.values[axis]);
        }
        if (mosim_pid_attitude_thrust_apply_acceleration(
                &params, input->reference_yaw_enu_rad, acceleration, &output->control) != 0) {
            output->status_code = -1;
            output->fallback_active = 1;
            return -1;
        }
    }
    output->normalized_thrust = output->control.desired_collective_thrust_n /
        (params.mass_kg * params.gravity_mps2 / input->hover_percentage);
    if (!isfinite(output->normalized_thrust)) {
        output->status_code = -1;
        output->fallback_active = 1;
        return -1;
    }
    if (output->normalized_thrust < 0.0) output->normalized_thrust = 0.0;
    if (output->normalized_thrust > 1.0) output->normalized_thrust = 1.0;
    output->status_code = 0;
    return 0;
}
