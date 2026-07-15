#include "wave_b_hinf_core.h"

#include <stdio.h>

static int run_case(int case_id, const MosimWaveBHinfInput *input)
{
    MosimWaveBHinfParams params;
    MosimWaveBHinfOutput output;
    int rc;
    mosim_wave_b_hinf_default_params(&params);
    rc = mosim_wave_b_hinf_step(&params, input, &output);
    if (rc != 0) return rc;
    printf("%d,%.17g,%.17g,%.17g,%.17g,%d,%d,%d\n", case_id,
           output.wrench[0], output.wrench[1], output.wrench[2], output.wrench[3],
           output.saturated, output.status_code, output.command_variant);
    return 0;
}

int main(void)
{
    MosimWaveBHinfInput hover = {{0}, {0}, 1, 0};
    MosimWaveBHinfInput small = {
        {0.001, -0.001, 0.002, 0.01, -0.02, 0.005,
         0.01, -0.01, 0.02, 0.001, -0.002, 0.005},
        {0}, 1, 0
    };
    MosimWaveBHinfInput saturated = {
        {0.1, -0.1, 0.2, 0.5, -0.5, 0.2,
         0.5, -0.5, 0.5, 0.2, -0.2, 0.3},
        {0}, 1, 0
    };
    MosimWaveBHinfInput disabled = {{0}, {0}, 0, 1};
    if (run_case(0, &hover) != 0) return 2;
    if (run_case(1, &small) != 0) return 3;
    if (run_case(2, &saturated) != 0) return 4;
    if (run_case(3, &disabled) != 0) return 5;
    return 0;
}
