#ifndef MOSIM_PID_UNIFIED_CORE_H
#define MOSIM_PID_UNIFIED_CORE_H

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    double kp;
    double ki;
    double kd;
    double feedforward_gain;
    double output_min;
    double output_max;
    double integral_min;
    double integral_max;
    double anti_windup_gain;
    double derivative_filter_tau;
    double schedule_gain;
    double fuzzy_gain;
    double neural_gain;
    double neural_residual_limit;
} MosimPidConfig;

typedef struct {
    double integral;
    double filtered_derivative;
    double previous_error;
    int initialized;
} MosimPidState;

typedef struct {
    double setpoint;
    double measurement;
    double feedforward;
    double schedule;
    double fuzzy_error;
    double neural_residual;
    double dt;
    int reset;
    int enable;
} MosimPidInput;

typedef struct {
    double command;
    double unsaturated_command;
    double error;
    double integral;
    double scheduled_gain;
    int saturated;
    int status_code;
} MosimPidOutput;

typedef struct {
    MosimPidState outer;
    MosimPidState inner;
} MosimCascadePidState;

typedef struct {
    double outer_reference;
    double outer_measurement;
    double inner_measurement;
    double feedforward;
    double schedule;
    double fuzzy_error;
    double neural_residual;
    double dt;
    int reset;
    int enable;
} MosimCascadePidInput;

typedef struct {
    double outer_command;
    double command;
    int saturated;
    int status_code;
} MosimCascadePidOutput;

void mosim_pid_default_config(MosimPidConfig *config);
void mosim_pid_reset(MosimPidState *state);
int mosim_pid_step(const MosimPidConfig *config, MosimPidState *state,
                   const MosimPidInput *input, MosimPidOutput *output);
int mosim_cascade_pid_step(const MosimPidConfig *outer_config,
                           const MosimPidConfig *inner_config,
                           MosimCascadePidState *state,
                           const MosimCascadePidInput *input,
                           MosimCascadePidOutput *output);

#ifdef __cplusplus
}
#endif

#endif
