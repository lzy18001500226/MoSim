#include "wave_b_hinf_core.h"

#include <math.h>
#include <string.h>

static double clamp_value(double value, double lower, double upper, int *saturated)
{
    if (value < lower) {
        *saturated = 1;
        return lower;
    }
    if (value > upper) {
        *saturated = 1;
        return upper;
    }
    return value;
}

void mosim_wave_b_hinf_default_params(MosimWaveBHinfParams *params)
{
    static const double gain[4][12] = {
        {0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 102.07465646871916, 0.0, 0.0, 160.7556564350713},
        {-521.4516779287975, 0.0, 0.0, -10.806018318480602, 0.0, 0.0, 0.0, -437.5189132603606, 0.0, 0.0, -1050.0326682458417, 0.0},
        {0.0, -521.451677928797, 0.0, 0.0, -10.806018318480536, 0.0, 437.51891326036105, 0.0, 0.0, 1050.0326682458376, 0.0, 0.0},
        {0.0, 0.0, -125.5903565899079, 0.0, 0.0, -25.26141057148942, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0}
    };
    int row;
    if (params == NULL) return;
    memset(params, 0, sizeof(*params));
    for (row = 0; row < 4; ++row) {
        memcpy(params->gain[row], gain[row], sizeof(gain[row]));
    }
    params->mass = 1.0;
    params->gravity = 9.8;
    params->force_min_n = 0.0;
    params->force_max_n = 25.0;
    params->torque_limit_nm = 8.0;
}

int mosim_wave_b_hinf_step(
    const MosimWaveBHinfParams *params,
    const MosimWaveBHinfInput *input,
    MosimWaveBHinfOutput *output)
{
    int command;
    int state_index;
    if (params == NULL || input == NULL || output == NULL) return -1;
    memset(output, 0, sizeof(*output));
    output->command_variant = 3;
    if (!input->enable) {
        output->status_code = 1;
        return 0;
    }
    if (!isfinite(params->mass) || !isfinite(params->gravity) ||
        params->force_max_n < params->force_min_n || params->torque_limit_nm <= 0.0) {
        output->status_code = 2;
        return -2;
    }
    for (state_index = 0; state_index < 12; ++state_index) {
        if (!isfinite(input->state[state_index]) || !isfinite(input->reference[state_index])) {
            output->status_code = 2;
            return -2;
        }
    }
    output->wrench[0] = params->mass * params->gravity;
    for (command = 0; command < 4; ++command) {
        for (state_index = 0; state_index < 12; ++state_index) {
            output->wrench[command] += params->gain[command][state_index] *
                (input->state[state_index] - input->reference[state_index]);
        }
    }
    output->wrench[0] = clamp_value(output->wrench[0], params->force_min_n,
                                    params->force_max_n, &output->saturated);
    for (command = 1; command < 4; ++command) {
        output->wrench[command] = clamp_value(output->wrench[command],
            -params->torque_limit_nm, params->torque_limit_nm, &output->saturated);
    }
    return 0;
}
