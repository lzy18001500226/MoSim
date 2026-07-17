#ifndef MOSIM_FAULT_TOLERANT_CONTROL_CORE_H
#define MOSIM_FAULT_TOLERANT_CONTROL_CORE_H

#ifdef __cplusplus
extern "C" {
#endif

enum {
    MOSIM_FTC_FDI = 1,
    MOSIM_FTC_PASSIVE = 2,
    MOSIM_FTC_ACTIVE = 3,
    MOSIM_FTC_FAULT_AWARE_ALLOCATION = 4,
    MOSIM_FTC_SINGLE_MOTOR_SAFE_LANDING = 5,
    MOSIM_FTC_MULTI_FAULT_RECONFIGURATION = 6
};

enum {
    MOSIM_FTC_ACTION_PASS = 0,
    MOSIM_FTC_ACTION_DETECT = 1,
    MOSIM_FTC_ACTION_RECONFIGURE = 2,
    MOSIM_FTC_ACTION_LAND = 3,
    MOSIM_FTC_ACTION_STOP = 4
};

typedef struct {
    double detection_threshold;
    double detection_persistence_s;
    double estimator_time_constant_s;
    double minimum_effectiveness;
    double passive_effectiveness_margin;
    double motor_command_min;
    double motor_command_max;
    double landing_thrust;
    double minimum_detection_command;
} MosimFtcParams;

typedef struct {
    double effectiveness_estimate[4];
    double residual_lpf[4];
    double fault_timer_s[4];
    unsigned int isolated_mask;
} MosimFtcState;

typedef struct {
    double dt;
    double desired_wrench[4];
    double measured_motor_response[4];
    int airborne;
    double altitude;
    int enable;
    int reset;
} MosimFtcInput;

typedef struct {
    double motor_command[4];
    double effectiveness_estimate[4];
    double achieved_wrench[4];
    double residual_norm;
    unsigned int isolated_mask;
    int fault_count;
    int action;
    int allocation_saturated;
    int status_code;
} MosimFtcOutput;

void mosim_ftc_default_params(MosimFtcParams *params);
void mosim_ftc_reset(MosimFtcState *state);
int mosim_ftc_step(int mode, const MosimFtcParams *params,
                   MosimFtcState *state, const MosimFtcInput *input,
                   MosimFtcOutput *output);

#ifdef __cplusplus
}
#endif

#endif
