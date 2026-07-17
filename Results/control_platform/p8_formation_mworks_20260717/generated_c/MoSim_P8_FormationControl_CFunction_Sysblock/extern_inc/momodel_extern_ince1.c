#include "MoSim_P8_FormationControl_CFunction_Sysblock.h"
/*** Current Block Name: cFunction ***/
enum { MOSIM_FORMATION_AGENTS = 3, MOSIM_FORMATION_AXES = 3 };
static int mosim_formation_isfinite(double value) {
    return value == value &&
           value <= 1.7976931348623157e308 &&
           value >= -1.7976931348623157e308;
}
enum {
    MOSIM_FORMATION_LEADER_FOLLOWER = 1,
    MOSIM_FORMATION_VIRTUAL_STRUCTURE = 2,
    MOSIM_FORMATION_CONSENSUS = 3,
    MOSIM_FORMATION_CONTAINMENT = 4,
    MOSIM_FORMATION_TRACKING = 5,
    MOSIM_FORMATION_RECONFIGURATION = 6,
    MOSIM_FORMATION_FAULT_TOLERANT = 7,
    MOSIM_FORMATION_CBF = 8,
    MOSIM_FORMATION_DISTRIBUTED_MPC = 9
};

typedef struct {
    double spacing_m;
    double position_gain;
    double velocity_gain;
    double maximum_speed_mps;
    double minimum_separation_m;
    double cbf_gain;
    double reconfiguration_scale;
    double distributed_mpc_horizon_s;
} MosimFormationParams;

typedef struct {
    double previous_position[MOSIM_FORMATION_AGENTS][MOSIM_FORMATION_AXES];
    int initialized;
} MosimFormationState;

typedef struct {
    double dt;
    double leader_position[MOSIM_FORMATION_AXES];
    double leader_velocity[MOSIM_FORMATION_AXES];
    double leader_yaw_rad;
    double position[MOSIM_FORMATION_AGENTS][MOSIM_FORMATION_AXES];
    double velocity[MOSIM_FORMATION_AGENTS][MOSIM_FORMATION_AXES];
    int healthy[MOSIM_FORMATION_AGENTS];
    int reconfigure;
    int enable;
    int reset;
} MosimFormationInput;

typedef struct {
    double desired_position[MOSIM_FORMATION_AGENTS][MOSIM_FORMATION_AXES];
    double desired_velocity[MOSIM_FORMATION_AGENTS][MOSIM_FORMATION_AXES];
    double minimum_pair_distance_m;
    double formation_rmse_m;
    int active_agents;
    unsigned int failed_mask;
    int safety_corrections;
    int status_code;
} MosimFormationOutput;

void mosim_formation_default_params(MosimFormationParams *params);
void mosim_formation_reset(MosimFormationState *state);
int mosim_formation_step(int mode, const MosimFormationParams *params,
                         MosimFormationState *state,
                         const MosimFormationInput *input,
                         MosimFormationOutput *output);




#include <math.h>
#include <stddef.h>
#include <string.h>

static int finite_input(const MosimFormationInput *input) {
    int agent, axis;
    if (!mosim_formation_isfinite(input->dt) || !mosim_formation_isfinite(input->leader_yaw_rad)) return 0;
    for (axis = 0; axis < MOSIM_FORMATION_AXES; ++axis) {
        if (!mosim_formation_isfinite(input->leader_position[axis]) ||
            !mosim_formation_isfinite(input->leader_velocity[axis])) return 0;
    }
    for (agent = 0; agent < MOSIM_FORMATION_AGENTS; ++agent)
        for (axis = 0; axis < MOSIM_FORMATION_AXES; ++axis)
            if (!mosim_formation_isfinite(input->position[agent][axis]) ||
                !mosim_formation_isfinite(input->velocity[agent][axis])) return 0;
    return 1;
}

static int valid_params(const MosimFormationParams *params) {
    return params != NULL && params->spacing_m > 0.0 &&
           params->position_gain > 0.0 && params->velocity_gain >= 0.0 &&
           params->maximum_speed_mps > 0.0 &&
           params->minimum_separation_m > 0.0 &&
           params->cbf_gain > 0.0 && params->reconfiguration_scale > 0.0 &&
           params->distributed_mpc_horizon_s > 0.0;
}

void mosim_formation_default_params(MosimFormationParams *params) {
    memset(params, 0, sizeof(*params));
    params->spacing_m = 1.5;
    params->position_gain = 1.2;
    params->velocity_gain = 0.35;
    params->maximum_speed_mps = 0.8;
    params->minimum_separation_m = 1.0;
    params->cbf_gain = 0.6;
    params->reconfiguration_scale = 0.65;
    params->distributed_mpc_horizon_s = 0.6;
}

void mosim_formation_reset(MosimFormationState *state) {
    memset(state, 0, sizeof(*state));
}

static void triangle_offsets(double spacing, double offsets[3][3]) {
    const double h = 0.8660254037844386 * spacing;
    memset(offsets, 0, 9 * sizeof(double));
    offsets[1][0] = h;
    offsets[1][1] = -0.5 * spacing;
    offsets[2][1] = -spacing;
}

static void rotate_offsets(double yaw, double offsets[3][3]) {
    const double c = cos(yaw), s = sin(yaw);
    int agent;
    for (agent = 0; agent < MOSIM_FORMATION_AGENTS; ++agent) {
        const double x = offsets[agent][0], y = offsets[agent][1];
        offsets[agent][0] = c * x - s * y;
        offsets[agent][1] = s * x + c * y;
    }
}

static void base_reference(const MosimFormationInput *input,
                           const double offsets[3][3],
                           MosimFormationOutput *output) {
    int agent, axis;
    for (agent = 0; agent < MOSIM_FORMATION_AGENTS; ++agent)
        for (axis = 0; axis < MOSIM_FORMATION_AXES; ++axis) {
            output->desired_position[agent][axis] =
                input->leader_position[axis] + offsets[agent][axis];
            output->desired_velocity[agent][axis] = input->leader_velocity[axis];
        }
}

static void apply_speed_limit(const MosimFormationParams *params,
                              MosimFormationOutput *output) {
    int agent, axis;
    for (agent = 0; agent < MOSIM_FORMATION_AGENTS; ++agent) {
        double norm = 0.0;
        for (axis = 0; axis < MOSIM_FORMATION_AXES; ++axis)
            norm += output->desired_velocity[agent][axis] *
                    output->desired_velocity[agent][axis];
        norm = sqrt(norm);
        if (norm > params->maximum_speed_mps)
            for (axis = 0; axis < MOSIM_FORMATION_AXES; ++axis)
                output->desired_velocity[agent][axis] *=
                    params->maximum_speed_mps / norm;
    }
}

static void apply_cbf(const MosimFormationParams *params,
                      const MosimFormationInput *input,
                      MosimFormationOutput *output) {
    int first, second, axis;
    for (first = 0; first < MOSIM_FORMATION_AGENTS; ++first) {
        for (second = first + 1; second < MOSIM_FORMATION_AGENTS; ++second) {
            double delta[3], distance = 0.0;
            for (axis = 0; axis < 3; ++axis) {
                delta[axis] = input->position[first][axis] - input->position[second][axis];
                distance += delta[axis] * delta[axis];
            }
            distance = sqrt(distance);
            if (distance < params->minimum_separation_m) {
                const double safe_distance = distance > 1e-6 ? distance : 1e-6;
                const double correction = params->cbf_gain *
                    (params->minimum_separation_m - distance);
                if (distance <= 1e-6) delta[0] = first == 0 ? -1.0 : 1.0;
                for (axis = 0; axis < 3; ++axis) {
                    const double push = correction * delta[axis] / safe_distance;
                    output->desired_position[first][axis] += 0.5 * push;
                    output->desired_position[second][axis] -= 0.5 * push;
                }
                output->safety_corrections += 1;
            }
        }
    }
}

static void diagnostics(const MosimFormationInput *input,
                        const MosimFormationOutput *reference,
                        MosimFormationOutput *output) {
    double squared_error = 0.0;
    int error_count = 0, first, second, axis;
    output->minimum_pair_distance_m = 1e9;
    for (first = 0; first < MOSIM_FORMATION_AGENTS; ++first) {
        if (input->healthy[first]) output->active_agents += 1;
        else output->failed_mask |= 1u << (unsigned int)first;
        for (axis = 0; axis < 3; ++axis) {
            const double error = input->position[first][axis] -
                reference->desired_position[first][axis];
            squared_error += error * error;
            error_count += 1;
        }
        for (second = first + 1; second < MOSIM_FORMATION_AGENTS; ++second) {
            double distance = 0.0;
            for (axis = 0; axis < 3; ++axis) {
                const double delta = input->position[first][axis] -
                    input->position[second][axis];
                distance += delta * delta;
            }
            distance = sqrt(distance);
            if (distance < output->minimum_pair_distance_m)
                output->minimum_pair_distance_m = distance;
        }
    }
    output->formation_rmse_m = sqrt(squared_error / (double)error_count);
}

int mosim_formation_step(int mode, const MosimFormationParams *params,
                         MosimFormationState *state,
                         const MosimFormationInput *input,
                         MosimFormationOutput *output) {
    double offsets[3][3];
    int agent, axis;
    if (state == NULL || input == NULL || output == NULL || !valid_params(params) ||
        !finite_input(input) || input->dt <= 0.0 ||
        mode < MOSIM_FORMATION_LEADER_FOLLOWER ||
        mode > MOSIM_FORMATION_DISTRIBUTED_MPC) {
        if (output != NULL) { memset(output, 0, sizeof(*output)); output->status_code = -1; }
        return -1;
    }
    if (input->reset) mosim_formation_reset(state);
    memset(output, 0, sizeof(*output));
    triangle_offsets(params->spacing_m, offsets);
    if (mode == MOSIM_FORMATION_VIRTUAL_STRUCTURE) rotate_offsets(input->leader_yaw_rad, offsets);
    if (mode == MOSIM_FORMATION_RECONFIGURATION && input->reconfigure)
        for (agent = 0; agent < 3; ++agent)
            for (axis = 0; axis < 3; ++axis)
                offsets[agent][axis] *= params->reconfiguration_scale;
    base_reference(input, offsets, output);

    if (!input->enable) { output->status_code = 1; return 0; }
    if (mode == MOSIM_FORMATION_CONSENSUS) {
        double centroid[3] = {0.0, 0.0, 0.0};
        for (agent = 0; agent < 3; ++agent)
            for (axis = 0; axis < 3; ++axis) centroid[axis] += input->position[agent][axis] / 3.0;
        for (agent = 0; agent < 3; ++agent)
            for (axis = 0; axis < 3; ++axis)
                output->desired_position[agent][axis] += 0.35 *
                    (input->leader_position[axis] - centroid[axis]);
    } else if (mode == MOSIM_FORMATION_CONTAINMENT) {
        for (agent = 1; agent < 3; ++agent) {
            const double side = agent == 1 ? 0.5 : -0.5;
            output->desired_position[agent][0] = input->leader_position[0] +
                side * params->spacing_m;
            output->desired_position[agent][1] = input->leader_position[1] - params->spacing_m;
        }
    } else if (mode == MOSIM_FORMATION_TRACKING) {
        for (agent = 0; agent < 3; ++agent)
            for (axis = 0; axis < 3; ++axis)
                output->desired_position[agent][axis] += params->velocity_gain *
                    (input->leader_velocity[axis] - input->velocity[agent][axis]);
    } else if (mode == MOSIM_FORMATION_FAULT_TOLERANT) {
        int healthy_rank = 0;
        for (agent = 0; agent < 3; ++agent) {
            if (!input->healthy[agent]) {
                for (axis = 0; axis < 3; ++axis) {
                    output->desired_position[agent][axis] = input->position[agent][axis];
                    output->desired_velocity[agent][axis] = 0.0;
                }
            } else {
                output->desired_position[agent][0] = input->leader_position[0];
                output->desired_position[agent][1] = input->leader_position[1] -
                    healthy_rank * params->spacing_m;
                healthy_rank += 1;
            }
        }
    } else if (mode == MOSIM_FORMATION_CBF) {
        apply_cbf(params, input, output);
    } else if (mode == MOSIM_FORMATION_DISTRIBUTED_MPC) {
        const double horizon = params->distributed_mpc_horizon_s;
        for (agent = 0; agent < 3; ++agent) {
            double delta[3], norm = 0.0;
            for (axis = 0; axis < 3; ++axis) {
                delta[axis] = output->desired_position[agent][axis] - input->position[agent][axis];
                norm += delta[axis] * delta[axis];
            }
            norm = sqrt(norm);
            if (norm > params->maximum_speed_mps * horizon)
                for (axis = 0; axis < 3; ++axis)
                    delta[axis] *= params->maximum_speed_mps * horizon / norm;
            for (axis = 0; axis < 3; ++axis) {
                output->desired_position[agent][axis] = input->position[agent][axis] + delta[axis];
                output->desired_velocity[agent][axis] = delta[axis] / horizon;
            }
        }
    }

    if (mode != MOSIM_FORMATION_DISTRIBUTED_MPC) {
        for (agent = 0; agent < 3; ++agent)
            for (axis = 0; axis < 3; ++axis)
                output->desired_velocity[agent][axis] += params->position_gain *
                    (output->desired_position[agent][axis] - input->position[agent][axis]);
    }
    apply_speed_limit(params, output);
    diagnostics(input, output, output);
    for (agent = 0; agent < 3; ++agent)
        for (axis = 0; axis < 3; ++axis)
            state->previous_position[agent][axis] = output->desired_position[agent][axis];
    state->initialized = 1;
    output->status_code = 1;
    return 0;
}
void MosimFormationControlStepScalar(
    double mode_id,
    double dt,
    double leader_x,
    double leader_y,
    double leader_z,
    double leader_vx,
    double leader_vy,
    double leader_vz,
    double leader_yaw,
    double position_1_x,
    double position_1_y,
    double position_1_z,
    double position_2_x,
    double position_2_y,
    double position_2_z,
    double position_3_x,
    double position_3_y,
    double position_3_z,
    double velocity_1_x,
    double velocity_1_y,
    double velocity_1_z,
    double velocity_2_x,
    double velocity_2_y,
    double velocity_2_z,
    double velocity_3_x,
    double velocity_3_y,
    double velocity_3_z,
    double healthy_1,
    double healthy_2,
    double healthy_3,
    double reconfigure,
    double enable,
    double reset,
    double *desired_position_1_x,
    double *desired_position_1_y,
    double *desired_position_1_z,
    double *desired_position_2_x,
    double *desired_position_2_y,
    double *desired_position_2_z,
    double *desired_position_3_x,
    double *desired_position_3_y,
    double *desired_position_3_z,
    double *desired_velocity_1_x,
    double *desired_velocity_1_y,
    double *desired_velocity_1_z,
    double *desired_velocity_2_x,
    double *desired_velocity_2_y,
    double *desired_velocity_2_z,
    double *desired_velocity_3_x,
    double *desired_velocity_3_y,
    double *desired_velocity_3_z,
    double *minimum_pair_distance,
    double *formation_rmse,
    double *active_agents,
    double *failed_mask,
    double *safety_corrections,
    double *status_code)
{
    static MosimFormationState states[10];
    static int initialized[10];
    MosimFormationParams params;
    MosimFormationInput input;
    MosimFormationOutput output;
    int id = (int)mode_id;
    int result;
    memset(&input, 0, sizeof(input));
    input.dt = dt;
    input.leader_position[0] = leader_x; input.leader_position[1] = leader_y;
    input.leader_position[2] = leader_z; input.leader_velocity[0] = leader_vx;
    input.leader_velocity[1] = leader_vy; input.leader_velocity[2] = leader_vz;
    input.leader_yaw_rad = leader_yaw;
    input.position[0][0] = position_1_x;
    input.velocity[0][0] = velocity_1_x;
    input.position[0][1] = position_1_y;
    input.velocity[0][1] = velocity_1_y;
    input.position[0][2] = position_1_z;
    input.velocity[0][2] = velocity_1_z;
    input.position[1][0] = position_2_x;
    input.velocity[1][0] = velocity_2_x;
    input.position[1][1] = position_2_y;
    input.velocity[1][1] = velocity_2_y;
    input.position[1][2] = position_2_z;
    input.velocity[1][2] = velocity_2_z;
    input.position[2][0] = position_3_x;
    input.velocity[2][0] = velocity_3_x;
    input.position[2][1] = position_3_y;
    input.velocity[2][1] = velocity_3_y;
    input.position[2][2] = position_3_z;
    input.velocity[2][2] = velocity_3_z;
    input.healthy[0] = healthy_1 != 0.0; input.healthy[1] = healthy_2 != 0.0;
    input.healthy[2] = healthy_3 != 0.0; input.reconfigure = reconfigure != 0.0;
    input.enable = enable != 0.0; input.reset = reset != 0.0;
    mosim_formation_default_params(&params);
    if (id < 1 || id > 9) id = 0;
    if (!initialized[id]) { mosim_formation_reset(&states[id]); initialized[id] = 1; }
    result = mosim_formation_step(id, &params, &states[id], &input, &output);
    if (result != 0) { memset(&output, 0, sizeof(output)); output.status_code = result; }
    *desired_position_1_x = output.desired_position[0][0];
    *desired_velocity_1_x = output.desired_velocity[0][0];
    *desired_position_1_y = output.desired_position[0][1];
    *desired_velocity_1_y = output.desired_velocity[0][1];
    *desired_position_1_z = output.desired_position[0][2];
    *desired_velocity_1_z = output.desired_velocity[0][2];
    *desired_position_2_x = output.desired_position[1][0];
    *desired_velocity_2_x = output.desired_velocity[1][0];
    *desired_position_2_y = output.desired_position[1][1];
    *desired_velocity_2_y = output.desired_velocity[1][1];
    *desired_position_2_z = output.desired_position[1][2];
    *desired_velocity_2_z = output.desired_velocity[1][2];
    *desired_position_3_x = output.desired_position[2][0];
    *desired_velocity_3_x = output.desired_velocity[2][0];
    *desired_position_3_y = output.desired_position[2][1];
    *desired_velocity_3_y = output.desired_velocity[2][1];
    *desired_position_3_z = output.desired_position[2][2];
    *desired_velocity_3_z = output.desired_velocity[2][2];
    *minimum_pair_distance = output.minimum_pair_distance_m;
    *formation_rmse = output.formation_rmse_m;
    *active_agents = (double)output.active_agents;
    *failed_mask = (double)output.failed_mask;
    *safety_corrections = (double)output.safety_corrections;
    *status_code = (double)output.status_code;
}
