#include "formation_control_core.h"

#include <math.h>
#include <stdio.h>
#include <string.h>

int main(void) {
    MosimFormationParams params;
    int mode;
    mosim_formation_default_params(&params);
    printf("mode,status,active,failed_mask,safety_corrections,min_distance,rmse,signature,desired_follower_distance\n");
    for (mode = MOSIM_FORMATION_LEADER_FOLLOWER;
         mode <= MOSIM_FORMATION_DISTRIBUTED_MPC; ++mode) {
        MosimFormationState state;
        MosimFormationInput input;
        MosimFormationOutput output;
        int step, agent;
        memset(&input, 0, sizeof(input));
        mosim_formation_reset(&state);
        input.dt = 0.02;
        input.leader_position[0] = 2.0;
        input.leader_position[1] = 1.0;
        input.leader_position[2] = 1.2;
        input.leader_velocity[0] = 0.35;
        input.leader_yaw_rad = 0.4;
        input.enable = 1;
        input.reset = 1;
        input.reconfigure = 1;
        for (agent = 0; agent < 3; ++agent) {
            input.healthy[agent] = 1;
            input.position[agent][0] = 0.15 * agent;
            input.position[agent][1] = -0.20 * agent;
            input.position[agent][2] = 1.0;
        }
        if (mode == MOSIM_FORMATION_FAULT_TOLERANT) input.healthy[1] = 0;
        for (step = 0; step < 20; ++step) {
            if (mosim_formation_step(mode, &params, &state, &input, &output) != 0)
                return 2;
            input.reset = 0;
        }
        printf("%d,%d,%d,%u,%d,%.9f,%.9f,%.9f,%.9f\n", mode,
               output.status_code, output.active_agents, output.failed_mask,
               output.safety_corrections, output.minimum_pair_distance_m,
               output.formation_rmse_m,
               output.desired_position[1][0] + output.desired_position[2][1],
               hypot(output.desired_position[1][0] - output.desired_position[2][0],
                     output.desired_position[1][1] - output.desired_position[2][1]));
    }
    return 0;
}
