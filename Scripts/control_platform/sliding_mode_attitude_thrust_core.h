#ifndef MOSIM_SLIDING_MODE_ATTITUDE_THRUST_CORE_H
#define MOSIM_SLIDING_MODE_ATTITUDE_THRUST_CORE_H

#ifdef __cplusplus
extern "C" {
#endif

enum MosimSlidingModeControllerId {
    MOSIM_SMC_INTEGRAL = 1,
    MOSIM_SMC_TERMINAL = 2,
    MOSIM_SMC_NONSINGULAR_TERMINAL = 3,
    MOSIM_SMC_SUPER_TWISTING = 4,
    MOSIM_SMC_ADAPTIVE = 5,
    MOSIM_SMC_FUZZY = 6
};

typedef struct {
    double dt;
    double position[3];
    double velocity[3];
    double reference_position[3];
    double reference_velocity[3];
    double reference_acceleration[3];
    double reference_yaw;
    int enable;
    int reset;
} MosimSlidingModeInput;

typedef struct {
    double lambda[3];
    double linear_gain[3];
    double reaching_gain[3];
    double boundary_layer[3];
    double integral_gain[3];
    double integral_limit[3];
    double terminal_alpha[3];
    double nonsingular_gain[3];
    double super_twisting_k1[3];
    double super_twisting_k2[3];
    double adaptive_rate[3];
    double adaptive_limit[3];
    double fuzzy_gain_delta[3];
    double mass_kg;
    double gravity_mps2;
    double hover_percentage;
    double max_tilt_rad;
    double min_collective_thrust_n;
    double max_collective_thrust_n;
} MosimSlidingModeParams;

typedef struct {
    double position_error_integral[3];
    double super_twisting_integral[3];
    double adaptive_reaching_gain[3];
} MosimSlidingModeState;

typedef struct {
    double desired_acceleration[3];
    double desired_attitude_wxyz[4];
    double normalized_thrust;
    double collective_thrust_n;
    double sliding_surface[3];
    double auxiliary_state[3];
    double effective_reaching_gain[3];
    int saturated;
    int status_code;
} MosimSlidingModeOutput;

void mosim_sliding_mode_default_params(MosimSlidingModeParams *params);
void mosim_sliding_mode_reset(
    const MosimSlidingModeParams *params,
    MosimSlidingModeState *state);
int mosim_sliding_mode_step(
    int controller_id,
    const MosimSlidingModeParams *params,
    MosimSlidingModeState *state,
    const MosimSlidingModeInput *input,
    MosimSlidingModeOutput *output);

#ifdef __cplusplus
}
#endif

#endif
