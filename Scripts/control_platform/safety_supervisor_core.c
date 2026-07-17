#include "safety_supervisor_core.h"

#include <math.h>
#include <stddef.h>
#include <string.h>

enum {
    CONSTRAINT_ACCELERATION = 1u << 0,
    CONSTRAINT_THRUST = 1u << 1,
    CONSTRAINT_TILT = 1u << 2,
    CONSTRAINT_CBF = 1u << 3,
    CONSTRAINT_GEOFENCE = 1u << 4,
    CONSTRAINT_TIMEOUT = 1u << 5,
    CONSTRAINT_INVALID_STATE = 1u << 6,
    CONSTRAINT_EMERGENCY = 1u << 7
};

static double clamp_value(double value, double lower, double upper) {
    return value < lower ? lower : (value > upper ? upper : value);
}

static int finite3(const double value[3]) {
    return isfinite(value[0]) && isfinite(value[1]) && isfinite(value[2]);
}

static int valid_params(const MosimSafetyParams *params) {
    int axis;
    if (params == NULL || params->max_tilt_rad <= 0.0 ||
        params->min_thrust < 0.0 || params->max_thrust <= params->min_thrust ||
        params->command_timeout_s <= 0.0 || params->land_speed <= 0.0) return 0;
    for (axis = 0; axis < 3; ++axis) {
        if (params->max_acceleration[axis] <= 0.0 || params->max_speed[axis] <= 0.0 ||
            params->geofence_max[axis] <= params->geofence_min[axis] ||
            params->governor_rate[axis] <= 0.0) return 0;
    }
    return 1;
}

void mosim_safety_default_params(MosimSafetyParams *params) {
    int axis;
    memset(params, 0, sizeof(*params));
    for (axis = 0; axis < 3; ++axis) {
        params->max_acceleration[axis] = axis == 2 ? 4.0 : 5.0;
        params->max_speed[axis] = axis == 2 ? 2.0 : 3.0;
        params->geofence_min[axis] = axis == 2 ? 0.0 : -8.0;
        params->geofence_max[axis] = axis == 2 ? 4.0 : 8.0;
        params->governor_rate[axis] = axis == 2 ? 0.8 : 1.5;
    }
    params->max_tilt_rad = 0.65;
    params->min_thrust = 0.0;
    params->max_thrust = 1.0;
    params->geofence_margin = 0.4;
    params->cbf_alpha = 2.0;
    params->obstacle_min_distance = 0.8;
    params->command_timeout_s = 0.25;
    params->return_altitude = 1.5;
    params->land_speed = 0.3;
}

void mosim_safety_reset(MosimSafetyState *state) {
    memset(state, 0, sizeof(*state));
    state->state = MOSIM_SAFETY_STATE_NOMINAL;
}

static void apply_envelope(const MosimSafetyParams *params,
                           const MosimSafetyInput *input,
                           MosimSafetyOutput *output) {
    int axis;
    for (axis = 0; axis < 3; ++axis) {
        double bounded = clamp_value(input->candidate_acceleration[axis],
                                     -params->max_acceleration[axis],
                                     params->max_acceleration[axis]);
        if (bounded != input->candidate_acceleration[axis]) {
            output->active_constraints |= CONSTRAINT_ACCELERATION;
            output->modified = 1;
        }
        output->safe_acceleration[axis] = bounded;
    }
    output->safe_thrust = clamp_value(input->candidate_thrust,
                                      params->min_thrust, params->max_thrust);
    if (output->safe_thrust != input->candidate_thrust) {
        output->active_constraints |= CONSTRAINT_THRUST;
        output->modified = 1;
    }
    if (fabs(input->candidate_tilt_rad) > params->max_tilt_rad) {
        double scale = params->max_tilt_rad / fabs(input->candidate_tilt_rad);
        output->safe_acceleration[0] *= scale;
        output->safe_acceleration[1] *= scale;
        output->active_constraints |= CONSTRAINT_TILT;
        output->modified = 1;
    }
}

static void apply_geofence(const MosimSafetyParams *params,
                           const MosimSafetyInput *input,
                           MosimSafetyOutput *output) {
    int axis;
    for (axis = 0; axis < 3; ++axis) {
        double lower = params->geofence_min[axis] + params->geofence_margin;
        double upper = params->geofence_max[axis] - params->geofence_margin;
        double bounded = clamp_value(output->safe_reference[axis], lower, upper);
        if (bounded != output->safe_reference[axis] ||
            input->position[axis] <= params->geofence_min[axis] ||
            input->position[axis] >= params->geofence_max[axis]) {
            output->active_constraints |= CONSTRAINT_GEOFENCE;
            output->modified = 1;
        }
        output->safe_reference[axis] = bounded;
    }
}

static void apply_governor(const MosimSafetyParams *params,
                           MosimSafetyState *state,
                           const MosimSafetyInput *input,
                           MosimSafetyOutput *output) {
    int axis;
    for (axis = 0; axis < 3; ++axis) {
        double limit = params->governor_rate[axis] * input->dt;
        double delta = input->reference_position[axis] - state->governed_reference[axis];
        state->governed_reference[axis] += clamp_value(delta, -limit, limit);
        output->safe_reference[axis] = state->governed_reference[axis];
        if (fabs(delta) > limit) output->modified = 1;
    }
}

static void set_state_action(MosimSafetyState *state, MosimSafetyOutput *output,
                             int next_state, int action) {
    state->state = next_state;
    output->state = next_state;
    output->action = action;
    output->modified = action != MOSIM_SAFETY_ACTION_PASS;
}

int mosim_safety_step(int mode, const MosimSafetyParams *params,
                      MosimSafetyState *state, const MosimSafetyInput *input,
                      MosimSafetyOutput *output) {
    int axis;
    if (state == NULL || input == NULL || output == NULL || !valid_params(params) ||
        mode < MOSIM_SAFETY_FILTER || mode > MOSIM_SAFETY_FAILSAFE ||
        !isfinite(input->dt) || input->dt <= 0.0 || !finite3(input->position) ||
        !finite3(input->velocity) || !finite3(input->candidate_acceleration) ||
        !finite3(input->reference_position) || !finite3(input->home_position) ||
        !isfinite(input->candidate_thrust) || !isfinite(input->candidate_tilt_rad)) {
        if (output != NULL) { memset(output, 0, sizeof(*output)); output->status_code = -1; }
        return -1;
    }
    if (input->reset) {
        mosim_safety_reset(state);
        for (axis = 0; axis < 3; ++axis) state->governed_reference[axis] = input->position[axis];
    }
    memset(output, 0, sizeof(*output));
    output->safe_thrust = input->candidate_thrust;
    output->state = state->state;
    for (axis = 0; axis < 3; ++axis) {
        output->safe_acceleration[axis] = input->candidate_acceleration[axis];
        output->safe_reference[axis] = input->reference_position[axis];
    }
    if (!input->enable) { output->status_code = 1; return 0; }

    apply_envelope(params, input, output);
    if (mode == MOSIM_SAFETY_CBF && input->obstacle_distance < params->obstacle_min_distance) {
        double barrier = params->cbf_alpha * (params->obstacle_min_distance - input->obstacle_distance);
        output->safe_acceleration[0] = fmin(output->safe_acceleration[0], -barrier);
        output->active_constraints |= CONSTRAINT_CBF;
        output->modified = 1;
    }
    if (mode == MOSIM_SAFETY_REFERENCE_GOVERNOR) apply_governor(params, state, input, output);
    if (mode == MOSIM_SAFETY_GEOFENCE || mode == MOSIM_SAFETY_CBF) apply_geofence(params, input, output);

    if (mode == MOSIM_SAFETY_EMERGENCY_STOP && input->emergency_request) {
        for (axis = 0; axis < 3; ++axis) output->safe_acceleration[axis] = 0.0;
        output->safe_thrust = 0.0;
        output->active_constraints |= CONSTRAINT_EMERGENCY;
        set_state_action(state, output, MOSIM_SAFETY_STATE_STOP, MOSIM_SAFETY_ACTION_STOP);
    } else if (mode == MOSIM_SAFETY_RETURN_AND_LAND) {
        if (input->land_request || state->state == MOSIM_SAFETY_STATE_LAND) {
            output->safe_reference[0] = input->home_position[0];
            output->safe_reference[1] = input->home_position[1];
            output->safe_reference[2] = fmax(0.0, input->position[2] - params->land_speed * input->dt);
            set_state_action(state, output, MOSIM_SAFETY_STATE_LAND, MOSIM_SAFETY_ACTION_LAND);
        } else if (input->return_request || state->state == MOSIM_SAFETY_STATE_RETURN) {
            output->safe_reference[0] = input->home_position[0];
            output->safe_reference[1] = input->home_position[1];
            output->safe_reference[2] = fmax(input->home_position[2], params->return_altitude);
            set_state_action(state, output, MOSIM_SAFETY_STATE_RETURN, MOSIM_SAFETY_ACTION_RETURN);
        }
    } else if (mode == MOSIM_SAFETY_FAILSAFE) {
        if (input->emergency_request) {
            output->active_constraints |= CONSTRAINT_EMERGENCY;
            output->safe_thrust = 0.0;
            set_state_action(state, output, MOSIM_SAFETY_STATE_STOP, MOSIM_SAFETY_ACTION_STOP);
        } else if (!input->state_valid) {
            output->active_constraints |= CONSTRAINT_INVALID_STATE;
            for (axis = 0; axis < 3; ++axis) output->safe_reference[axis] = input->position[axis];
            set_state_action(state, output, MOSIM_SAFETY_STATE_LAND, MOSIM_SAFETY_ACTION_LAND);
        } else if (!input->offboard_valid || input->command_age_s > params->command_timeout_s) {
            output->active_constraints |= CONSTRAINT_TIMEOUT;
            for (axis = 0; axis < 3; ++axis) output->safe_reference[axis] = input->position[axis];
            set_state_action(state, output, MOSIM_SAFETY_STATE_HOLD, MOSIM_SAFETY_ACTION_HOLD);
        }
    }
    if (output->action == MOSIM_SAFETY_ACTION_PASS && output->modified)
        output->action = MOSIM_SAFETY_ACTION_MODIFY;
    output->status_code = 1;
    return 0;
}
