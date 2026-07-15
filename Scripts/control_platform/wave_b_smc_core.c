#include "wave_b_smc_core.h"

#include <math.h>
#include <string.h>

static double clamp_value(double value, double lower, double upper)
{
    if (value < lower) return lower;
    if (value > upper) return upper;
    return value;
}

static double boundary_sign(double value, double width)
{
    const double safe_width = width > 1.0e-9 ? width : 1.0e-9;
    return clamp_value(value / safe_width, -1.0, 1.0);
}

static void normalize_quaternion(const double in[4], double out[4])
{
    const double norm = sqrt(in[0] * in[0] + in[1] * in[1] + in[2] * in[2] + in[3] * in[3]);
    if (norm <= 1.0e-12) {
        out[0] = 1.0; out[1] = 0.0; out[2] = 0.0; out[3] = 0.0;
        return;
    }
    out[0] = in[0] / norm;
    out[1] = in[1] / norm;
    out[2] = in[2] / norm;
    out[3] = in[3] / norm;
}

static void map_acceleration_to_attitude(
    const MosimWaveAParams *params,
    const MosimWaveAInput *input,
    MosimWaveAOutput *output)
{
    double roll = clamp_value(-output->desired_acceleration[1] / params->gravity,
                              -params->tilt_limit_rad, params->tilt_limit_rad);
    double pitch = clamp_value(output->desired_acceleration[0] / params->gravity,
                               -params->tilt_limit_rad, params->tilt_limit_rad);
    const double cy = cos(0.5 * input->reference_yaw);
    const double sy = sin(0.5 * input->reference_yaw);
    const double cp = cos(0.5 * pitch);
    const double sp = sin(0.5 * pitch);
    const double cr = cos(0.5 * roll);
    const double sr = sin(0.5 * roll);
    const double attitude[4] = {
        cy * cp * cr + sy * sp * sr,
        cy * cp * sr - sy * sp * cr,
        sy * cp * sr + cy * sp * cr,
        sy * cp * cr - cy * sp * sr
    };
    normalize_quaternion(attitude, output->desired_attitude_wxyz);
    output->normalized_thrust = output->desired_acceleration[2] /
        (params->gravity / params->hover_percentage);
    {
        const double unclamped = output->normalized_thrust;
        output->normalized_thrust = clamp_value(unclamped, 0.0, 1.0);
        if (fabs(unclamped - output->normalized_thrust) > 1.0e-12) output->saturated = 1;
    }
    output->collective_thrust_n = output->normalized_thrust * params->mass * params->gravity /
        params->hover_percentage;
    output->command_variant = 1;
}

void mosim_wave_b_smc_default_params(MosimWaveBSmcParams *params)
{
    const MosimWaveBSmcParams defaults = {
        {1.2, 1.2, 1.4}, {2.2, 2.2, 2.8}, {0.8, 0.8, 1.0}, {0.12, 0.12, 0.15}
    };
    if (params != NULL) *params = defaults;
}

int mosim_wave_b_smc_step(
    const MosimWaveAParams *plant_params,
    const MosimWaveBSmcParams *smc_params,
    const MosimWaveAInput *input,
    MosimWaveAOutput *output)
{
    int i;
    if (plant_params == NULL || smc_params == NULL || input == NULL || output == NULL) return -1;
    memset(output, 0, sizeof(*output));
    output->desired_attitude_wxyz[0] = 1.0;
    if (!input->enable) {
        output->status_code = 1;
        return 0;
    }
    for (i = 0; i < 3; ++i) {
        const double ep = input->reference_position[i] - input->position[i];
        const double ev = input->reference_velocity[i] - input->velocity[i];
        const double sliding = ev + smc_params->lambda[i] * ep;
        const double robust = smc_params->sliding_gain[i] *
            boundary_sign(sliding, smc_params->boundary_layer[i]);
        output->desired_acceleration[i] = input->reference_acceleration[i] +
            smc_params->linear_gain[i] * sliding + robust;
    }
    output->desired_acceleration[2] += plant_params->gravity;
    map_acceleration_to_attitude(plant_params, input, output);
    return 0;
}
