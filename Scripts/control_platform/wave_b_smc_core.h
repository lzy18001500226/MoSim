#ifndef MOSIM_WAVE_B_SMC_CORE_H
#define MOSIM_WAVE_B_SMC_CORE_H

#include "wave_a_controller_core.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    double lambda[3];
    double sliding_gain[3];
    double linear_gain[3];
    double boundary_layer[3];
} MosimWaveBSmcParams;

void mosim_wave_b_smc_default_params(MosimWaveBSmcParams *params);
int mosim_wave_b_smc_step(
    const MosimWaveAParams *plant_params,
    const MosimWaveBSmcParams *smc_params,
    const MosimWaveAInput *input,
    MosimWaveAOutput *output);

#ifdef __cplusplus
}
#endif

#endif
