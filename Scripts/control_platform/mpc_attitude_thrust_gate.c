#include "mpc_attitude_thrust_core.h"

#include <math.h>
#include <stdio.h>

static void print_case(int controller_id)
{
    MosimMpcParams params;
    MosimMpcState state;
    MosimMpcInput input = {
        0.02,
        {0.2, -0.1, 0.7}, {-0.3, 0.2, -0.1},
        {1.0, 0.5, 1.2}, {0.1, -0.2, 0.0}, {0.05, -0.04, 0.02},
        0.3, 1, 1
    };
    MosimMpcOutput output;
    int rc;
    mosim_mpc_default_params(&params);
    mosim_mpc_reset(&state);
    rc = mosim_mpc_step(controller_id, &params, &state, &input, &output);
    printf(
        "%d,%d,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,"
        "%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%d,%d,%d\n",
        controller_id, rc,
        output.desired_acceleration[0], output.desired_acceleration[1], output.desired_acceleration[2],
        output.unconstrained_acceleration[0], output.unconstrained_acceleration[1], output.unconstrained_acceleration[2],
        output.auxiliary[0], output.auxiliary[1], output.auxiliary[2],
        output.desired_attitude_wxyz[0], output.desired_attitude_wxyz[1],
        output.desired_attitude_wxyz[2], output.desired_attitude_wxyz[3],
        output.normalized_thrust, output.collective_thrust_n, output.solver_cost,
        state.adaptive_scale, output.solver_iterations, output.saturated, output.status_code);
}

static void print_lifecycle_cases(void)
{
    MosimMpcParams params;
    MosimMpcState state;
    MosimMpcInput input = {
        0.02, {0.0, 0.0, 1.0}, {0.0, 0.0, 0.0},
        {1.0, 0.0, 1.0}, {0.0, 0.0, 0.0}, {0.0, 0.0, 0.0}, 0.0, 1, 0
    };
    MosimMpcOutput output;
    int rc;
    mosim_mpc_default_params(&params);
    mosim_mpc_reset(&state);
    input.enable = 0;
    rc = mosim_mpc_step(MOSIM_MPC_LINEAR, &params, &state, &input, &output);
    printf("L,disabled,%d,%d,%.17g\n", rc, output.status_code, output.normalized_thrust);
    input.enable = 1;
    input.dt = NAN;
    rc = mosim_mpc_step(MOSIM_MPC_LINEAR, &params, &state, &input, &output);
    printf("L,invalid_input,%d,%d,%.17g\n", rc, output.status_code, output.normalized_thrust);
    input.dt = 0.02;
    rc = mosim_mpc_step(99, &params, &state, &input, &output);
    printf("L,unknown_controller,%d,%d,%.17g\n", rc, output.status_code, output.normalized_thrust);
    params.mass_kg = 0.0;
    rc = mosim_mpc_step(MOSIM_MPC_LINEAR, &params, &state, &input, &output);
    printf("L,invalid_params,%d,%d,%.17g\n", rc, output.status_code, output.normalized_thrust);
    mosim_mpc_default_params(&params);
    input.reset = 1;
    rc = mosim_mpc_step(MOSIM_MPC_ADAPTIVE, &params, &state, &input, &output);
    input.reset = 0;
    rc |= mosim_mpc_step(MOSIM_MPC_ADAPTIVE, &params, &state, &input, &output);
    printf("L,adaptive_continuity,%d,%d,%.17g\n", rc, output.status_code, state.adaptive_scale);
    input.reset = 1;
    rc = mosim_mpc_step(MOSIM_MPC_LINEAR, &params, &state, &input, &output);
    printf("L,deterministic_reset,%d,%d,%.17g\n", rc, output.status_code, (double)state.step_count);
}

int main(void)
{
    int controller_id;
    for (controller_id = MOSIM_MPC_LINEAR; controller_id <= MOSIM_MPC_MPPI; ++controller_id) print_case(controller_id);
    print_lifecycle_cases();
    return 0;
}
