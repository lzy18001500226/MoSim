#include "linear_robust_attitude_thrust_core.h"

#include <math.h>
#include <stdio.h>

static void print_case(int controller_id)
{
    MosimLinearRobustParams params;
    MosimLinearRobustState state;
    MosimLinearRobustInput input = {
        0.02,
        {0.2, -0.1, 0.7}, {-0.3, 0.2, -0.1},
        {1.0, 0.5, 1.2}, {0.1, -0.2, 0.0}, {0.05, -0.04, 0.02},
        0.3, 1, 1
    };
    MosimLinearRobustOutput output;
    int rc;
    mosim_linear_robust_default_params(&params);
    mosim_linear_robust_reset(&state);
    rc = mosim_linear_robust_step(controller_id, &params, &state, &input, &output);
    printf(
        "%d,%d,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,"
        "%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%d,%d\n",
        controller_id, rc,
        output.desired_acceleration[0], output.desired_acceleration[1], output.desired_acceleration[2],
        output.desired_attitude_wxyz[0], output.desired_attitude_wxyz[1],
        output.desired_attitude_wxyz[2], output.desired_attitude_wxyz[3],
        output.normalized_thrust, output.collective_thrust_n,
        output.estimated_position[0], output.estimated_position[1], output.estimated_position[2],
        output.estimated_velocity[0], output.estimated_velocity[1], output.estimated_velocity[2],
        output.adaptive_disturbance[0], output.adaptive_disturbance[1], output.adaptive_disturbance[2],
        output.storage_function, output.saturated, output.status_code);
}

static void print_lifecycle_cases(void)
{
    MosimLinearRobustParams params;
    MosimLinearRobustState state;
    MosimLinearRobustInput input = {
        0.02,
        {0.0, 0.0, 1.0}, {0.0, 0.0, 0.0},
        {1.0, 0.0, 1.0}, {0.0, 0.0, 0.0}, {0.0, 0.0, 0.0},
        0.0, 1, 0
    };
    MosimLinearRobustOutput output;
    int rc;
    mosim_linear_robust_default_params(&params);
    mosim_linear_robust_reset(&state);

    input.enable = 0;
    rc = mosim_linear_robust_step(MOSIM_LINEAR_ROBUST_LQG, &params, &state, &input, &output);
    printf("L,disabled,%d,%d,%.17g\n", rc, output.status_code, output.normalized_thrust);

    input.enable = 1;
    input.dt = NAN;
    rc = mosim_linear_robust_step(MOSIM_LINEAR_ROBUST_LQG, &params, &state, &input, &output);
    printf("L,invalid_input,%d,%d,%.17g\n", rc, output.status_code, output.normalized_thrust);

    input.dt = 0.02;
    rc = mosim_linear_robust_step(99, &params, &state, &input, &output);
    printf("L,unknown_controller,%d,%d,%.17g\n", rc, output.status_code, output.normalized_thrust);

    params.mass_kg = 0.0;
    rc = mosim_linear_robust_step(MOSIM_LINEAR_ROBUST_LQG, &params, &state, &input, &output);
    printf("L,invalid_params,%d,%d,%.17g\n", rc, output.status_code, output.normalized_thrust);

    mosim_linear_robust_default_params(&params);
    input.reference_position[0] = 100.0;
    rc = mosim_linear_robust_step(MOSIM_LINEAR_ROBUST_FEEDBACK_LINEARIZATION, &params, &state, &input, &output);
    printf("L,tilt_limit,%d,%d,%.17g\n", rc, output.status_code,
        atan2(hypot(output.desired_acceleration[0], output.desired_acceleration[1]),
              output.desired_acceleration[2]));

    input.reference_position[0] = 1.0;
    input.reset = 1;
    rc = mosim_linear_robust_step(MOSIM_LINEAR_ROBUST_ADAPTIVE_BACKSTEPPING, &params, &state, &input, &output);
    input.reset = 0;
    rc |= mosim_linear_robust_step(MOSIM_LINEAR_ROBUST_ADAPTIVE_BACKSTEPPING, &params, &state, &input, &output);
    printf("L,adaptive_continuity,%d,%d,%.17g\n", rc, output.status_code,
        fabs(output.adaptive_disturbance[0]));
    input.reset = 1;
    rc = mosim_linear_robust_step(MOSIM_LINEAR_ROBUST_ADAPTIVE_BACKSTEPPING, &params, &state, &input, &output);
    printf("L,deterministic_reset,%d,%d,%.17g\n", rc, output.status_code,
        fabs(output.adaptive_disturbance[0]));
}

int main(void)
{
    print_case(MOSIM_LINEAR_ROBUST_LQG);
    print_case(MOSIM_LINEAR_ROBUST_FEEDBACK_LINEARIZATION);
    print_case(MOSIM_LINEAR_ROBUST_PASSIVITY);
    print_case(MOSIM_LINEAR_ROBUST_ADAPTIVE_BACKSTEPPING);
    print_lifecycle_cases();
    return 0;
}
