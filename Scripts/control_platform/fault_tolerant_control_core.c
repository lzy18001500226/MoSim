#include "fault_tolerant_control_core.h"

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
