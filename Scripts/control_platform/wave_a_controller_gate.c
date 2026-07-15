#include "wave_a_controller_core.h"

#include <stdio.h>
#include <string.h>

static void print_case(int controller_id, MosimWaveAState *state, MosimWaveAInput *input)
{
    MosimWaveAParams params;
    MosimWaveAOutput out;
    mosim_wave_a_default_params(&params);
    mosim_wave_a_step(controller_id, &params, state, input, &out);
    printf("%d", controller_id);
    printf(",%.17g,%.17g,%.17g", out.desired_acceleration[0], out.desired_acceleration[1], out.desired_acceleration[2]);
    printf(",%.17g,%.17g,%.17g,%.17g", out.desired_attitude_wxyz[0], out.desired_attitude_wxyz[1], out.desired_attitude_wxyz[2], out.desired_attitude_wxyz[3]);
    printf(",%.17g,%.17g,%.17g", out.desired_body_rate[0], out.desired_body_rate[1], out.desired_body_rate[2]);
    printf(",%.17g,%.17g,%d,%d,%d\n", out.normalized_thrust, out.collective_thrust_n, out.command_variant, out.saturated, out.status_code);
}

int main(void)
{
    MosimWaveAState state;
    MosimWaveAInput input;
    memset(&input, 0, sizeof(input));
    mosim_wave_a_reset(&state);
    input.dt = 0.02;
    input.enable = 1;
    input.attitude_wxyz[0] = 1.0;
    input.reference_attitude_wxyz[0] = 0.9800665778412416;
    input.reference_attitude_wxyz[2] = 0.19866933079506122;
    input.position[0] = 0.2; input.position[1] = -0.1; input.position[2] = 0.7;
    input.velocity[0] = -0.3; input.velocity[1] = 0.2; input.velocity[2] = -0.1;
    input.reference_position[0] = 1.0; input.reference_position[1] = 0.5; input.reference_position[2] = 1.2;
    input.reference_velocity[0] = 0.1; input.reference_velocity[1] = -0.2; input.reference_velocity[2] = 0.0;
    input.reference_acceleration[0] = 0.05; input.reference_acceleration[1] = -0.04; input.reference_acceleration[2] = 0.02;
    input.reference_body_rate[0] = 0.1; input.reference_body_rate[1] = -0.05; input.reference_body_rate[2] = 0.02;
    input.reference_yaw = 0.3;
    input.collective_thrust_n = 6.8;

    print_case(MOSIM_WAVE_A_LQR, &state, &input);
    mosim_wave_a_reset(&state);
    print_case(MOSIM_WAVE_A_LQI, &state, &input);
    print_case(MOSIM_WAVE_A_LQI, &state, &input);
    mosim_wave_a_reset(&state);
    print_case(MOSIM_WAVE_A_SO3, &state, &input);
    mosim_wave_a_reset(&state);
    print_case(MOSIM_WAVE_A_BACKSTEPPING, &state, &input);
    return 0;
}
