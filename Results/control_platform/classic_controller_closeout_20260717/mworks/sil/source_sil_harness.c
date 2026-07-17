#include <stdio.h>
#include <string.h>
#include "classic_controller_core.h"

int main(void)
{
    MosimClassicParams params;
    int id;
    mosim_classic_default_params(&params);
    for (id = 1; id <= 5; ++id) {
        MosimClassicState state;
        MosimClassicInput in;
        MosimClassicOutput out;
        int step;
        mosim_classic_reset(&state);
        memset(&in, 0, sizeof(in));
    in.position[0] = 0.10000000000000001;
    in.position[1] = -0.050000000000000003;
    in.position[2] = 0.80000000000000004;
    in.velocity[0] = 0.02;
    in.velocity[1] = -0.01;
    in.velocity[2] = 0.01;
    in.reference_position[0] = 0.25;
    in.reference_position[1] = 0.10000000000000001;
    in.reference_position[2] = 1;
    in.reference_velocity[0] = 0;
    in.reference_velocity[1] = 0;
    in.reference_velocity[2] = 0;
    in.reference_acceleration[0] = 0.01;
    in.reference_acceleration[1] = -0.02;
    in.reference_acceleration[2] = 0;
    in.dt = 0.01;
    in.reference_yaw = 0.14999999999999999;
    in.enable = 1;
        for (step = 0; step < 4; ++step) {
            in.reset = step == 0;
            if (mosim_classic_step(id, &params, &state, &in, &out) != 0) return 2;
            printf("%d,%d,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g\n", id, step,
            out.desired_acceleration[0],
            out.desired_acceleration[1],
            out.desired_acceleration[2],
            out.desired_attitude_wxyz[0],
            out.desired_attitude_wxyz[1],
            out.desired_attitude_wxyz[2],
            out.desired_attitude_wxyz[3],
            out.observer_position[0],
            out.observer_position[1],
            out.observer_position[2],
            out.observer_velocity[0],
            out.observer_velocity[1],
            out.observer_velocity[2],
            out.reference_model_position[0],
            out.reference_model_position[1],
            out.reference_model_position[2],
            out.reference_model_velocity[0],
            out.reference_model_velocity[1],
            out.reference_model_velocity[2],
            out.adaptive_position_delta[0],
            out.adaptive_position_delta[1],
            out.adaptive_position_delta[2],
            out.adaptive_velocity_delta[0],
            out.adaptive_velocity_delta[1],
            out.adaptive_velocity_delta[2],
            out.fractional_integral[0],
            out.fractional_integral[1],
            out.fractional_integral[2],
            out.fractional_derivative[0],
            out.fractional_derivative[1],
            out.fractional_derivative[2],
            out.normalized_thrust,
            out.collective_thrust_n,
            (double)out.saturated,
            (double)out.status_code);
        }
    }
    return 0;
}
