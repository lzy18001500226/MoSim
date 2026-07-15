#include "wave_a_controller_core.h"
#include "wave_b_smc_core.h"

#include <stdio.h>

int main(void)
{
    MosimWaveAParams plant;
    MosimWaveBSmcParams smc;
    MosimWaveAInput input = {
        0.01, {0.2, -0.1, 0.7}, {-0.3, 0.2, -0.1}, {1.0, 0.0, 0.0, 0.0},
        {1.0, 0.5, 1.2}, {0.1, -0.2, 0.0}, {0.05, -0.04, 0.02},
        {1.0, 0.0, 0.0, 0.0}, {0.0, 0.0, 0.0}, 0.3, 0.0, 1, 0
    };
    MosimWaveAOutput output;
    mosim_wave_a_default_params(&plant);
    mosim_wave_b_smc_default_params(&smc);
    if (mosim_wave_b_smc_step(&plant, &smc, &input, &output) != 0) return 2;
    printf("%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g\n",
           output.desired_acceleration[0], output.desired_acceleration[1],
           output.desired_acceleration[2], output.desired_attitude_wxyz[0],
           output.desired_attitude_wxyz[1], output.desired_attitude_wxyz[2],
           output.desired_attitude_wxyz[3], output.normalized_thrust,
           (double)output.command_variant);
    return 0;
}
