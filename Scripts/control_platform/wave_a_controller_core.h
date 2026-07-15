#ifndef MOSIM_WAVE_A_CONTROLLER_CORE_H
#define MOSIM_WAVE_A_CONTROLLER_CORE_H

#ifdef __cplusplus
extern "C" {
#endif

enum MosimWaveAControllerId {
    MOSIM_WAVE_A_LQR = 1,
    MOSIM_WAVE_A_LQI = 2,
    MOSIM_WAVE_A_SO3 = 3,
    MOSIM_WAVE_A_BACKSTEPPING = 4
};

typedef struct {
    double dt;
    double position[3];
    double velocity[3];
    double attitude_wxyz[4];
    double reference_position[3];
    double reference_velocity[3];
    double reference_acceleration[3];
    double reference_attitude_wxyz[4];
    double reference_body_rate[3];
    double reference_yaw;
    double collective_thrust_n;
    int enable;
    int reset;
} MosimWaveAInput;

typedef struct {
    double kp[3];
    double kv[3];
    double ki[3];
    double integral_limit[3];
    double backstepping_k1[3];
    double backstepping_k2[3];
    double so3_attitude_gain[3];
    double body_rate_limit[3];
    double mass;
    double gravity;
    double hover_percentage;
    double tilt_limit_rad;
} MosimWaveAParams;

typedef struct {
    double integral_position_error[3];
} MosimWaveAState;

typedef struct {
    double desired_attitude_wxyz[4];
    double desired_body_rate[3];
    double desired_acceleration[3];
    double normalized_thrust;
    double collective_thrust_n;
    int command_variant; /* 1=ATTITUDE_THRUST, 2=BODY_RATE_THRUST */
    int saturated;
    int status_code;
} MosimWaveAOutput;

void mosim_wave_a_default_params(MosimWaveAParams *params);
void mosim_wave_a_reset(MosimWaveAState *state);
int mosim_wave_a_step(
    int controller_id,
    const MosimWaveAParams *params,
    MosimWaveAState *state,
    const MosimWaveAInput *input,
    MosimWaveAOutput *output);

#ifdef __cplusplus
}
#endif

#endif
