#include "sliding_mode_attitude_thrust_core.h"

#include <math.h>
#include <stdio.h>

static void print_case(int controller_id)
{
    MosimSlidingModeParams params;
    MosimSlidingModeState state;
    MosimSlidingModeInput input = {
        0.02,
        {0.2, -0.1, 0.7}, {-0.3, 0.2, -0.1},
        {1.0, 0.5, 1.2}, {0.1, -0.2, 0.0}, {0.05, -0.04, 0.02},
        0.3, 1, 1
    };
    MosimSlidingModeOutput output;
    int rc;
    mosim_sliding_mode_default_params(&params);
    mosim_sliding_mode_reset(&params, &state);
    rc = mosim_sliding_mode_step(controller_id, &params, &state, &input, &output);
    printf(
        "%d,%d,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,"
        "%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%d,%d\n",
        controller_id, rc,
        output.desired_acceleration[0], output.desired_acceleration[1], output.desired_acceleration[2],
        output.sliding_surface[0], output.sliding_surface[1], output.sliding_surface[2],
        output.auxiliary_state[0], output.auxiliary_state[1], output.auxiliary_state[2],
        output.effective_reaching_gain[0], output.effective_reaching_gain[1], output.effective_reaching_gain[2],
        output.desired_attitude_wxyz[0], output.desired_attitude_wxyz[1],
        output.desired_attitude_wxyz[2], output.desired_attitude_wxyz[3],
        output.normalized_thrust, output.collective_thrust_n,
        state.super_twisting_integral[0], state.adaptive_reaching_gain[0],
        output.saturated, output.status_code);
}

static void print_lifecycle_cases(void)
{
    MosimSlidingModeParams params;
    MosimSlidingModeState state;
    MosimSlidingModeInput input = {
        0.02,
        {0.0, 0.0, 1.0}, {0.0, 0.0, 0.0},
        {1.0, 0.0, 1.0}, {0.0, 0.0, 0.0}, {0.0, 0.0, 0.0},
        0.0, 1, 0
    };
    MosimSlidingModeOutput output;
    int rc;
    mosim_sliding_mode_default_params(&params);
    mosim_sliding_mode_reset(&params, &state);
    input.enable = 0;
    rc = mosim_sliding_mode_step(MOSIM_SMC_INTEGRAL, &params, &state, &input, &output);
    printf("L,disabled,%d,%d,%.17g\n", rc, output.status_code, output.normalized_thrust);
    input.enable = 1;
    input.dt = NAN;
    rc = mosim_sliding_mode_step(MOSIM_SMC_INTEGRAL, &params, &state, &input, &output);
    printf("L,invalid_input,%d,%d,%.17g\n", rc, output.status_code, output.normalized_thrust);
    input.dt = 0.02;
    rc = mosim_sliding_mode_step(99, &params, &state, &input, &output);
    printf("L,unknown_controller,%d,%d,%.17g\n", rc, output.status_code, output.normalized_thrust);
    params.mass_kg = 0.0;
    rc = mosim_sliding_mode_step(MOSIM_SMC_INTEGRAL, &params, &state, &input, &output);
    printf("L,invalid_params,%d,%d,%.17g\n", rc, output.status_code, output.normalized_thrust);
    mosim_sliding_mode_default_params(&params);
    input.reset = 1;
    rc = mosim_sliding_mode_step(MOSIM_SMC_SUPER_TWISTING, &params, &state, &input, &output);
    input.reset = 0;
    rc |= mosim_sliding_mode_step(MOSIM_SMC_SUPER_TWISTING, &params, &state, &input, &output);
    printf("L,super_twisting_continuity,%d,%d,%.17g\n", rc, output.status_code,
        fabs(state.super_twisting_integral[0]));
    input.reset = 1;
    rc = mosim_sliding_mode_step(MOSIM_SMC_SUPER_TWISTING, &params, &state, &input, &output);
    printf("L,deterministic_reset,%d,%d,%.17g\n", rc, output.status_code,
        fabs(state.super_twisting_integral[0]));
}

int main(void)
{
    int controller_id;
    for (controller_id = MOSIM_SMC_INTEGRAL; controller_id <= MOSIM_SMC_FUZZY; ++controller_id) {
        print_case(controller_id);
    }
    print_lifecycle_cases();
    return 0;
}
