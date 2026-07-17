#ifndef MOSIM_FORMATION_CONTROL_CORE_H
#define MOSIM_FORMATION_CONTROL_CORE_H

#ifdef __cplusplus
extern "C" {
#endif

#define MOSIM_FORMATION_AGENTS 3
#define MOSIM_FORMATION_AXES 3

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

#ifdef __cplusplus
}
#endif

#endif
