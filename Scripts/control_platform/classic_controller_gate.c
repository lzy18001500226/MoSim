#include "classic_controller_core.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void require_true(int condition, const char *message)
{
    if (!condition) {
        fprintf(stderr, "%s\n", message);
        exit(1);
    }
}

static double quaternion_norm(const double q[4])
{
    return sqrt(q[0] * q[0] + q[1] * q[1] + q[2] * q[2] + q[3] * q[3]);
}

static MosimClassicInput default_input(void)
{
    MosimClassicInput input;
    memset(&input, 0, sizeof(input));
    input.dt = 0.01;
    input.position[0] = 0.10; input.position[1] = -0.05; input.position[2] = 0.80;
    input.velocity[0] = 0.02; input.velocity[1] = -0.01; input.velocity[2] = 0.01;
    input.reference_position[0] = 0.25; input.reference_position[1] = 0.10;
    input.reference_position[2] = 1.00;
    input.reference_velocity[0] = 0.0; input.reference_velocity[1] = 0.0;
    input.reference_velocity[2] = 0.0;
    input.reference_acceleration[0] = 0.01; input.reference_acceleration[1] = -0.02;
    input.reference_acceleration[2] = 0.0;
    input.reference_yaw = 0.15;
    input.enable = 1;
    return input;
}

int main(void)
{
    MosimClassicParams params;
    int controller_id;
    mosim_classic_default_params(&params);
    for (controller_id = 1; controller_id <= 5; ++controller_id) {
        MosimClassicState state;
        MosimClassicInput input = default_input();
        MosimClassicOutput first;
        MosimClassicOutput second;
        int rc;
        mosim_classic_reset(&state);
        rc = mosim_classic_step(controller_id, &params, &state, &input, &first);
        require_true(rc == 0 && first.status_code == 0, "controller first step failed");
        require_true(isfinite(first.collective_thrust_n) && first.collective_thrust_n > 0.0,
            "controller produced invalid thrust");
        require_true(fabs(quaternion_norm(first.desired_attitude_wxyz) - 1.0) <= 1.0e-12,
            "controller quaternion is not normalized");
        rc = mosim_classic_step(controller_id, &params, &state, &input, &second);
        require_true(rc == 0 && second.status_code == 0, "controller second step failed");

        if (controller_id == MOSIM_CLASSIC_POLE_PLACEMENT_LUENBERGER) {
            require_true(state.observer_initialized == 1, "Luenberger observer did not initialize");
            require_true(fabs(second.observer_position[0] - first.observer_position[0]) > 1.0e-12,
                "Luenberger observer state did not evolve");
        } else if (controller_id == MOSIM_CLASSIC_MRAC) {
            require_true(state.reference_model_initialized == 1, "MRAC reference model did not initialize");
            require_true(fabs(second.adaptive_position_delta[0]) > 0.0,
                "MRAC adaptive parameter did not evolve");
            require_true(fabs(second.adaptive_position_delta[0]) <= params.mrac_parameter_limit[0],
                "MRAC projection bound failed");
        } else if (controller_id == MOSIM_CLASSIC_NDI) {
            const double expected = input.reference_acceleration[0] +
                params.ndi_position_gain[0] * (input.reference_position[0] - input.position[0]) +
                params.ndi_velocity_gain[0] * (input.reference_velocity[0] - input.velocity[0]) +
                params.ndi_linear_drag[0] * input.velocity[0] / params.mass_kg;
            require_true(fabs(second.desired_acceleration[0] - expected) <= 1.0e-12,
                "NDI model inversion term mismatch");
        } else if (controller_id == MOSIM_CLASSIC_FOPID) {
            require_true(state.fopid_sample_count == 2, "FOPID fixed-memory state did not advance");
            require_true(fabs(second.fractional_integral[0]) > 0.0,
                "FOPID fractional integral is inactive");
            require_true(fabs(second.fractional_derivative[0]) > 0.0,
                "FOPID fractional derivative is inactive");
            require_true(fabs(second.fractional_integral[0] - first.fractional_integral[0]) > 1.0e-12,
                "FOPID finite-memory response did not evolve");
        } else if (controller_id == MOSIM_CLASSIC_H2_STATE_FEEDBACK) {
            const double expected = input.reference_acceleration[0] +
                params.h2_position_gain[0] * (input.reference_position[0] - input.position[0]) +
                params.h2_velocity_gain[0] * (input.reference_velocity[0] - input.velocity[0]);
            require_true(fabs(second.desired_acceleration[0] - expected) <= 1.0e-12,
                "H2 frozen state-feedback gain mismatch");
        }

        printf("%d,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%.17g,%d\n",
            controller_id,
            second.desired_acceleration[0], second.desired_acceleration[1],
            second.desired_acceleration[2], second.normalized_thrust,
            second.observer_position[0], second.reference_model_position[0],
            second.fractional_integral[0], second.fractional_derivative[0],
            second.saturated);
    }

    {
        MosimClassicState state;
        MosimClassicInput input = default_input();
        MosimClassicOutput output;
        int rc;
        mosim_classic_reset(&state);
        input.enable = 0;
        rc = mosim_classic_step(1, &params, &state, &input, &output);
        require_true(rc == 0 && output.status_code == 1, "disabled lifecycle failed");
        input.enable = 1;
        rc = mosim_classic_step(99, &params, &state, &input, &output);
        require_true(rc == -2 && output.status_code == -2, "unknown-controller lifecycle failed");
        input.dt = 0.0;
        rc = mosim_classic_step(1, &params, &state, &input, &output);
        require_true(rc == -3 && output.status_code == -3, "invalid-input lifecycle failed");
        input = default_input();
        params.fopid_lambda = 1.5;
        rc = mosim_classic_step(4, &params, &state, &input, &output);
        require_true(rc == -5 && output.status_code == -5, "invalid-parameter lifecycle failed");
    }
    return 0;
}
