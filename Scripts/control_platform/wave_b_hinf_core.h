#ifndef MOSIM_WAVE_B_HINF_CORE_H
#define MOSIM_WAVE_B_HINF_CORE_H

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    double state[12];
    double reference[12];
    int enable;
    int reset;
} MosimWaveBHinfInput;

typedef struct {
    double gain[4][12];
    double mass;
    double gravity;
    double force_min_n;
    double force_max_n;
    double torque_limit_nm;
} MosimWaveBHinfParams;

typedef struct {
    double wrench[4];
    int saturated;
    int status_code;
    int command_variant; /* 3=WRENCH */
} MosimWaveBHinfOutput;

void mosim_wave_b_hinf_default_params(MosimWaveBHinfParams *params);
int mosim_wave_b_hinf_step(
    const MosimWaveBHinfParams *params,
    const MosimWaveBHinfInput *input,
    MosimWaveBHinfOutput *output);

#ifdef __cplusplus
}
#endif

#endif
