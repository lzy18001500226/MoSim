#include "safety_supervisor_core.h"

#include <stdio.h>
#include <string.h>

static int run_case(int mode) {
    MosimSafetyParams params;
    MosimSafetyState state;
    MosimSafetyInput input;
    MosimSafetyOutput output;
    int rc;
    memset(&input, 0, sizeof(input));
    mosim_safety_default_params(&params);
    mosim_safety_reset(&state);
    input.dt = 0.01;
    input.position[2] = 1.0;
    input.reference_position[0] = 12.0;
    input.reference_position[2] = 1.0;
    input.candidate_acceleration[0] = 8.0;
    input.candidate_thrust = 1.2;
    input.candidate_tilt_rad = 0.8;
    input.obstacle_distance = 0.4;
    input.state_valid = 1;
    input.offboard_valid = 1;
    input.enable = 1;
    input.reset = 1;
    if (mode == MOSIM_SAFETY_EMERGENCY_STOP) input.emergency_request = 1;
    if (mode == MOSIM_SAFETY_RETURN_AND_LAND) input.return_request = 1;
    if (mode == MOSIM_SAFETY_FAILSAFE) input.command_age_s = 1.0;
    rc = mosim_safety_step(mode, &params, &state, &input, &output);
    printf("%d,%d,%d,%d,%u,%.17g,%.17g,%.17g\n", mode, rc, output.status_code,
           output.action, output.active_constraints, output.safe_acceleration[0],
           output.safe_thrust, output.safe_reference[0]);
    return rc != 0 || output.status_code != 1;
}

int main(void) {
    int mode;
    int failures = 0;
    for (mode = MOSIM_SAFETY_FILTER; mode <= MOSIM_SAFETY_FAILSAFE; ++mode)
        failures += run_case(mode);
    return failures == 0 ? 0 : 1;
}
