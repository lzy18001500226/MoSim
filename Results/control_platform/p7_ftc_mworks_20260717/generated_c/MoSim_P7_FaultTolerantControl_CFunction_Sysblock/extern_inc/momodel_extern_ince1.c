#include "MoSim_P7_FaultTolerantControl_CFunction_Sysblock.h"
/*** Current Block Name: cFunction ***/
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




#include <math.h>
#include <stddef.h>
#include <string.h>

static double clamp_value(double value, double lower, double upper) {
    return value < lower ? lower : (value > upper ? upper : value);
}

static int finite4(const double value[4]) {
    return isfinite(value[0]) && isfinite(value[1]) &&
           isfinite(value[2]) && isfinite(value[3]);
}

static int bit_count(unsigned int value) {
    int count = 0;
    while (value != 0u) {
        count += (int)(value & 1u);
        value >>= 1u;
    }
    return count;
}

static int valid_params(const MosimFtcParams *params) {
    return params != NULL && params->detection_threshold > 0.0 &&
           params->detection_threshold < 1.0 &&
           params->detection_persistence_s > 0.0 &&
           params->estimator_time_constant_s > 0.0 &&
           params->minimum_effectiveness > 0.0 &&
           params->minimum_effectiveness <= params->detection_threshold &&
           params->passive_effectiveness_margin >= params->minimum_effectiveness &&
           params->passive_effectiveness_margin <= 1.0 &&
           params->motor_command_max > params->motor_command_min &&
           params->landing_thrust >= params->motor_command_min &&
           params->landing_thrust <= params->motor_command_max;
}

void mosim_ftc_default_params(MosimFtcParams *params) {
    memset(params, 0, sizeof(*params));
    params->detection_threshold = 0.82;
    params->detection_persistence_s = 0.12;
    params->estimator_time_constant_s = 0.08;
    params->minimum_effectiveness = 0.25;
    params->passive_effectiveness_margin = 0.85;
    params->motor_command_min = 0.0;
    params->motor_command_max = 1.0;
    params->landing_thrust = 0.42;
    params->minimum_detection_command = 0.05;
}

void mosim_ftc_reset(MosimFtcState *state) {
    int rotor;
    memset(state, 0, sizeof(*state));
    for (rotor = 0; rotor < 4; ++rotor) state->effectiveness_estimate[rotor] = 1.0;
}

static void mix_wrench(const double wrench[4], double motor[4]) {
    const double thrust = wrench[0];
    const double roll = wrench[1];
    const double pitch = wrench[2];
    const double yaw = wrench[3];
    motor[0] = 0.25 * thrust - 0.5 * roll + 0.5 * pitch + 0.25 * yaw;
    motor[1] = 0.25 * thrust + 0.5 * roll + 0.5 * pitch - 0.25 * yaw;
    motor[2] = 0.25 * thrust + 0.5 * roll - 0.5 * pitch + 0.25 * yaw;
    motor[3] = 0.25 * thrust - 0.5 * roll - 0.5 * pitch - 0.25 * yaw;
}

static void reconstruct_wrench(const double motor[4], const double eta[4],
                               double wrench[4]) {
    double effective[4];
    int rotor;
    for (rotor = 0; rotor < 4; ++rotor) effective[rotor] = motor[rotor] * eta[rotor];
    wrench[0] = effective[0] + effective[1] + effective[2] + effective[3];
    wrench[1] = 0.5 * (-effective[0] + effective[1] + effective[2] - effective[3]);
    wrench[2] = 0.5 * (effective[0] + effective[1] - effective[2] - effective[3]);
    wrench[3] = effective[0] - effective[1] + effective[2] - effective[3];
}

static void update_fdi(const MosimFtcParams *params, MosimFtcState *state,
                       const MosimFtcInput *input, const double nominal[4]) {
    const double alpha = clamp_value(input->dt / params->estimator_time_constant_s, 0.0, 1.0);
    int rotor;
    for (rotor = 0; rotor < 4; ++rotor) {
        double observed = state->effectiveness_estimate[rotor];
        if (fabs(nominal[rotor]) >= params->minimum_detection_command) {
            observed = clamp_value(input->measured_motor_response[rotor] / nominal[rotor],
                                   0.0, 1.0);
        }
        state->residual_lpf[rotor] +=
            alpha * ((1.0 - observed) - state->residual_lpf[rotor]);
        state->effectiveness_estimate[rotor] =
            clamp_value(1.0 - state->residual_lpf[rotor],
                        params->minimum_effectiveness, 1.0);
        if (state->effectiveness_estimate[rotor] < params->detection_threshold) {
            state->fault_timer_s[rotor] += input->dt;
            if (state->fault_timer_s[rotor] >= params->detection_persistence_s)
                state->isolated_mask |= 1u << (unsigned int)rotor;
        } else {
            state->fault_timer_s[rotor] = 0.0;
        }
    }
}

static void bounded_allocation(const MosimFtcParams *params, const double nominal[4],
                               const double eta[4], double output[4], int *saturated) {
    int rotor;
    for (rotor = 0; rotor < 4; ++rotor) {
        const double compensated = nominal[rotor] /
            clamp_value(eta[rotor], params->minimum_effectiveness, 1.0);
        output[rotor] = clamp_value(compensated, params->motor_command_min,
                                    params->motor_command_max);
        if (output[rotor] != compensated) *saturated = 1;
    }
}

int mosim_ftc_step(int mode, const MosimFtcParams *params,
                   MosimFtcState *state, const MosimFtcInput *input,
                   MosimFtcOutput *output) {
    double nominal[4];
    double allocation_eta[4];
    int rotor;
    if (state == NULL || input == NULL || output == NULL || !valid_params(params) ||
        mode < MOSIM_FTC_FDI || mode > MOSIM_FTC_MULTI_FAULT_RECONFIGURATION ||
        !isfinite(input->dt) || input->dt <= 0.0 || !finite4(input->desired_wrench) ||
        !finite4(input->measured_motor_response) || !isfinite(input->altitude)) {
        if (output != NULL) { memset(output, 0, sizeof(*output)); output->status_code = -1; }
        return -1;
    }
    if (input->reset) mosim_ftc_reset(state);
    memset(output, 0, sizeof(*output));
    mix_wrench(input->desired_wrench, nominal);
    for (rotor = 0; rotor < 4; ++rotor) {
        nominal[rotor] = clamp_value(nominal[rotor], params->motor_command_min,
                                     params->motor_command_max);
        output->motor_command[rotor] = nominal[rotor];
        allocation_eta[rotor] = 1.0;
    }
    if (!input->enable) { output->status_code = 1; return 0; }

    update_fdi(params, state, input, nominal);
    output->isolated_mask = state->isolated_mask;
    output->fault_count = bit_count(state->isolated_mask);
    for (rotor = 0; rotor < 4; ++rotor) {
        output->effectiveness_estimate[rotor] = state->effectiveness_estimate[rotor];
        output->residual_norm += state->residual_lpf[rotor] * state->residual_lpf[rotor];
    }
    output->residual_norm = sqrt(output->residual_norm);

    if (mode == MOSIM_FTC_PASSIVE) {
        for (rotor = 0; rotor < 4; ++rotor)
            allocation_eta[rotor] = params->passive_effectiveness_margin;
        bounded_allocation(params, nominal, allocation_eta, output->motor_command,
                           &output->allocation_saturated);
        output->action = MOSIM_FTC_ACTION_RECONFIGURE;
    } else if ((mode == MOSIM_FTC_ACTIVE ||
                mode == MOSIM_FTC_FAULT_AWARE_ALLOCATION) && output->fault_count > 0) {
        for (rotor = 0; rotor < 4; ++rotor)
            allocation_eta[rotor] = state->effectiveness_estimate[rotor];
        bounded_allocation(params, nominal, allocation_eta, output->motor_command,
                           &output->allocation_saturated);
        output->action = MOSIM_FTC_ACTION_RECONFIGURE;
    } else if (mode == MOSIM_FTC_SINGLE_MOTOR_SAFE_LANDING && output->fault_count > 0) {
        for (rotor = 0; rotor < 4; ++rotor) {
            allocation_eta[rotor] = state->effectiveness_estimate[rotor];
            output->motor_command[rotor] = params->landing_thrust /
                (4.0 * clamp_value(allocation_eta[rotor], params->minimum_effectiveness, 1.0));
            output->motor_command[rotor] = clamp_value(output->motor_command[rotor],
                params->motor_command_min, params->motor_command_max);
        }
        output->action = input->airborne ? MOSIM_FTC_ACTION_LAND : MOSIM_FTC_ACTION_STOP;
    } else if (mode == MOSIM_FTC_MULTI_FAULT_RECONFIGURATION && output->fault_count > 0) {
        for (rotor = 0; rotor < 4; ++rotor)
            allocation_eta[rotor] = state->effectiveness_estimate[rotor];
        bounded_allocation(params, nominal, allocation_eta, output->motor_command,
                           &output->allocation_saturated);
        output->action = output->fault_count <= 2 ?
            MOSIM_FTC_ACTION_RECONFIGURE : MOSIM_FTC_ACTION_LAND;
    } else if (output->fault_count > 0) {
        output->action = MOSIM_FTC_ACTION_DETECT;
    }
    reconstruct_wrench(output->motor_command, allocation_eta, output->achieved_wrench);
    output->status_code = 1;
    return 0;
}
void MosimFaultTolerantControlStepScalar(
    double mode_id,
    double dt,
    double desired_thrust,
    double desired_roll,
    double desired_pitch,
    double desired_yaw,
    double response_1,
    double response_2,
    double response_3,
    double response_4,
    double airborne,
    double altitude,
    double enable,
    double reset,
    double *motor_command_1,
    double *motor_command_2,
    double *motor_command_3,
    double *motor_command_4,
    double *eta_hat_1,
    double *eta_hat_2,
    double *eta_hat_3,
    double *eta_hat_4,
    double *achieved_thrust,
    double *achieved_roll,
    double *achieved_pitch,
    double *achieved_yaw,
    double *residual_norm,
    double *isolated_mask,
    double *fault_count,
    double *action,
    double *allocation_saturated,
    double *status_code)
{
    static MosimFtcState states[7];
    static int initialized[7];
    MosimFtcParams params;
    MosimFtcInput input;
    MosimFtcOutput output;
    int id = (int)mode_id;
    int result;
    memset(&input, 0, sizeof(input));
    input.dt = dt;
    input.desired_wrench[0] = desired_thrust; input.desired_wrench[1] = desired_roll;
    input.desired_wrench[2] = desired_pitch; input.desired_wrench[3] = desired_yaw;
    input.measured_motor_response[0] = response_1;
    input.measured_motor_response[1] = response_2;
    input.measured_motor_response[2] = response_3;
    input.measured_motor_response[3] = response_4;
    input.airborne = airborne != 0.0; input.altitude = altitude;
    input.enable = enable != 0.0; input.reset = reset != 0.0;
    mosim_ftc_default_params(&params);
    if (id < 1 || id > 6) id = 0;
    if (!initialized[id]) { mosim_ftc_reset(&states[id]); initialized[id] = 1; }
    result = mosim_ftc_step(id, &params, &states[id], &input, &output);
    if (result != 0) { memset(&output, 0, sizeof(output)); output.status_code = result; }
    *motor_command_1 = output.motor_command[0]; *motor_command_2 = output.motor_command[1];
    *motor_command_3 = output.motor_command[2]; *motor_command_4 = output.motor_command[3];
    *eta_hat_1 = output.effectiveness_estimate[0]; *eta_hat_2 = output.effectiveness_estimate[1];
    *eta_hat_3 = output.effectiveness_estimate[2]; *eta_hat_4 = output.effectiveness_estimate[3];
    *achieved_thrust = output.achieved_wrench[0]; *achieved_roll = output.achieved_wrench[1];
    *achieved_pitch = output.achieved_wrench[2]; *achieved_yaw = output.achieved_wrench[3];
    *residual_norm = output.residual_norm; *isolated_mask = (double)output.isolated_mask;
    *fault_count = (double)output.fault_count; *action = (double)output.action;
    *allocation_saturated = (double)output.allocation_saturated;
    *status_code = (double)output.status_code;
}
