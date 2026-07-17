#include "enhancement_attitude_thrust_core.h"

#include <math.h>
#include <stdio.h>
#include <string.h>

static int failures = 0;

static void require_true(int condition, const char *message)
{
    if (!condition) {
        fprintf(stderr, "FAIL: %s\n", message);
        failures += 1;
    }
}

static MosimEnhancementInput hover_input(void)
{
    MosimEnhancementInput input;
    memset(&input, 0, sizeof(input));
    input.dt = 0.01;
    input.enable = 1;
    return input;
}

int main(void)
{
    MosimEnhancementParams params;
    int controller_id;
    mosim_enhancement_default_params(&params);
    for (controller_id = MOSIM_ENHANCEMENT_L1_ADAPTIVE; controller_id <= MOSIM_ENHANCEMENT_ILC; ++controller_id) {
        MosimEnhancementState state;
        MosimEnhancementInput input = hover_input();
        MosimEnhancementOutput output;
        mosim_enhancement_reset(&state);
        require_true(mosim_enhancement_step(controller_id, &params, &state, &input, &output) == 0,
            "hover step must succeed");
        require_true(output.status_code == 1, "enabled controller must report active status");
        require_true(isfinite(output.normalized_thrust), "normalized thrust must be finite");
        require_true(fabs(output.normalized_thrust - params.hover_percentage) < 1.0e-9,
            "zero-error hover must preserve hover thrust");
    }
    {
        MosimEnhancementState state;
        MosimEnhancementInput input = hover_input();
        MosimEnhancementOutput output;
        mosim_enhancement_reset(&state);
        input.reference_position[0] = 0.5;
        input.position[0] = 0.2;
        input.measured_acceleration[0] = 1.0;
        require_true(mosim_enhancement_step(MOSIM_ENHANCEMENT_COMPLETE_ADRC, &params, &state, &input, &output) == 0,
            "ADRC initialization step must succeed");
        input.position[0] = 0.1;
        require_true(mosim_enhancement_step(MOSIM_ENHANCEMENT_COMPLETE_ADRC, &params, &state, &input, &output) == 0,
            "ADRC dynamic step must succeed");
        require_true(fabs(state.eso_disturbance[0]) > 0.0, "ADRC ESO disturbance state must update");
    }
    {
        MosimEnhancementState state;
        MosimEnhancementInput input = hover_input();
        MosimEnhancementOutput first;
        MosimEnhancementOutput second;
        mosim_enhancement_reset(&state);
        input.reference_position[0] = 0.25;
        input.trajectory_phase_bin = 7;
        require_true(mosim_enhancement_step(MOSIM_ENHANCEMENT_ILC, &params, &state, &input, &first) == 0,
            "ILC first pass must succeed");
        require_true(mosim_enhancement_step(MOSIM_ENHANCEMENT_ILC, &params, &state, &input, &second) == 0,
            "ILC second pass must succeed");
        require_true(second.compensation[0] > first.compensation[0], "ILC must reuse learned phase-bin compensation");
    }
    {
        MosimEnhancementState state;
        MosimEnhancementInput input = hover_input();
        MosimEnhancementOutput output;
        mosim_enhancement_reset(&state);
        input.dt = NAN;
        require_true(mosim_enhancement_step(MOSIM_ENHANCEMENT_AWFF, &params, &state, &input, &output) != 0,
            "non-finite dt must fail closed");
        require_true(output.status_code < 0, "invalid input must expose failed status");
    }
    printf("{\"status\":\"%s\",\"controller_count\":6,\"failures\":%d}\n",
        failures == 0 ? "passed" : "failed", failures);
    return failures == 0 ? 0 : 1;
}
