#include "fault_tolerant_control_core.h"

#include <stdio.h>

int main(void) {
    int mode;
    for (mode = MOSIM_FTC_FDI; mode <= MOSIM_FTC_MULTI_FAULT_RECONFIGURATION; ++mode) {
        MosimFtcParams params;
        MosimFtcState state;
        MosimFtcInput input = {0};
        MosimFtcOutput output;
        double effectiveness[4] = {1.0, 1.0, 1.0, 1.0};
        int step;
        mosim_ftc_default_params(&params);
        mosim_ftc_reset(&state);
        input.dt = 0.01;
        input.desired_wrench[0] = 2.4;
        input.desired_wrench[1] = 0.04;
        input.desired_wrench[2] = -0.03;
        input.desired_wrench[3] = 0.02;
        input.airborne = 1;
        input.altitude = 1.2;
        input.enable = 1;
        if (mode == MOSIM_FTC_PASSIVE) effectiveness[0] = 0.75;
        else if (mode == MOSIM_FTC_ACTIVE) effectiveness[1] = 0.55;
        else if (mode == MOSIM_FTC_FAULT_AWARE_ALLOCATION) effectiveness[2] = 0.55;
        else if (mode == MOSIM_FTC_SINGLE_MOTOR_SAFE_LANDING) effectiveness[3] = 0.20;
        else if (mode == MOSIM_FTC_MULTI_FAULT_RECONFIGURATION) {
            effectiveness[0] = 0.55;
            effectiveness[2] = 0.60;
        } else effectiveness[0] = 0.55;
        for (step = 0; step < 80; ++step) {
            double nominal[4];
            int rotor;
            nominal[0] = 0.25 * input.desired_wrench[0] - 0.5 * input.desired_wrench[1] + 0.5 * input.desired_wrench[2] + 0.25 * input.desired_wrench[3];
            nominal[1] = 0.25 * input.desired_wrench[0] + 0.5 * input.desired_wrench[1] + 0.5 * input.desired_wrench[2] - 0.25 * input.desired_wrench[3];
            nominal[2] = 0.25 * input.desired_wrench[0] + 0.5 * input.desired_wrench[1] - 0.5 * input.desired_wrench[2] + 0.25 * input.desired_wrench[3];
            nominal[3] = 0.25 * input.desired_wrench[0] - 0.5 * input.desired_wrench[1] - 0.5 * input.desired_wrench[2] - 0.25 * input.desired_wrench[3];
            for (rotor = 0; rotor < 4; ++rotor)
                input.measured_motor_response[rotor] = nominal[rotor] * effectiveness[rotor];
            if (mosim_ftc_step(mode, &params, &state, &input, &output) != 0) return 10 + mode;
        }
        if (mode != MOSIM_FTC_PASSIVE && output.fault_count == 0) return 20 + mode;
        if (mode == MOSIM_FTC_MULTI_FAULT_RECONFIGURATION && output.fault_count != 2) return 30;
        if (mode == MOSIM_FTC_SINGLE_MOTOR_SAFE_LANDING && output.action != MOSIM_FTC_ACTION_LAND) return 31;
        printf("%d,%d,%u,%d,%.9f,%.9f,%.9f,%.9f\n", mode, output.action,
               output.isolated_mask, output.fault_count, output.effectiveness_estimate[0],
               output.effectiveness_estimate[1], output.motor_command[0],
               output.achieved_wrench[0]);
    }
    return 0;
}
