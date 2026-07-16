#include "pid_unified_core.h"

#include <math.h>
#include <string.h>

static double clamp_value(double value, double lower, double upper)
{
    if (value < lower) return lower;
    if (value > upper) return upper;
    return value;
}

static int finite_config(const MosimPidConfig *config)
{
    const double values[] = {
        config->kp, config->ki, config->kd, config->feedforward_gain,
        config->output_min, config->output_max, config->integral_min,
        config->integral_max, config->anti_windup_gain,
        config->derivative_filter_tau, config->schedule_gain,
        config->fuzzy_gain, config->neural_gain,
        config->neural_residual_limit
    };
    size_t index;
    for (index = 0; index < sizeof(values) / sizeof(values[0]); ++index) {
        if (!isfinite(values[index])) return 0;
    }
    return config->output_min <= config->output_max &&
           config->integral_min <= config->integral_max &&
           config->derivative_filter_tau >= 0.0 &&
           config->neural_residual_limit >= 0.0;
}

static double effective_gain(const MosimPidConfig *config,
                             const MosimPidInput *input)
{
    const double residual = clamp_value(input->neural_residual,
                                        -config->neural_residual_limit,
                                        config->neural_residual_limit);
    const double fuzzy_term = tanh(input->fuzzy_error);
    const double gain = 1.0 + config->schedule_gain * input->schedule +
                        config->fuzzy_gain * fuzzy_term +
                        config->neural_gain * residual;
    return clamp_value(gain, 0.25, 4.0);
}

void mosim_pid_default_config(MosimPidConfig *config)
{
    const MosimPidConfig defaults = {
        1.0, 0.0, 0.0, 0.0, -1.0, 1.0, -1.0, 1.0, 0.2, 0.0,
        0.0, 0.0, 0.0, 0.0
    };
    if (config != NULL) *config = defaults;
}

void mosim_pid_reset(MosimPidState *state)
{
    if (state != NULL) memset(state, 0, sizeof(*state));
}

int mosim_pid_step(const MosimPidConfig *config, MosimPidState *state,
                   const MosimPidInput *input, MosimPidOutput *output)
{
    double error;
    double derivative;
    double gain;
    double unsaturated;
    double command;
    double saturation_error;
    if (config == NULL || state == NULL || input == NULL || output == NULL ||
        !finite_config(config) || !isfinite(input->setpoint) ||
        !isfinite(input->measurement) || !isfinite(input->feedforward) ||
        !isfinite(input->schedule) || !isfinite(input->fuzzy_error) ||
        !isfinite(input->neural_residual) || !isfinite(input->dt) ||
        input->dt <= 0.0) {
        if (output != NULL) memset(output, 0, sizeof(*output));
        if (output != NULL) output->status_code = -1;
        return -1;
    }
    memset(output, 0, sizeof(*output));
    if (input->reset) mosim_pid_reset(state);
    if (!input->enable) {
        output->status_code = 1;
        return 0;
    }
    error = input->setpoint - input->measurement;
    derivative = state->initialized ? (error - state->previous_error) / input->dt : 0.0;
    if (config->derivative_filter_tau > 0.0) {
        const double alpha = input->dt / (config->derivative_filter_tau + input->dt);
        state->filtered_derivative += alpha * (derivative - state->filtered_derivative);
        derivative = state->filtered_derivative;
    } else {
        state->filtered_derivative = derivative;
    }
    gain = effective_gain(config, input);
    state->integral += gain * error * input->dt;
    state->integral = clamp_value(state->integral, config->integral_min,
                                  config->integral_max);
    unsaturated = gain * config->kp * error + config->ki * state->integral +
                  gain * config->kd * derivative +
                  config->feedforward_gain * input->feedforward;
    command = clamp_value(unsaturated, config->output_min, config->output_max);
    saturation_error = command - unsaturated;
    if (config->anti_windup_gain > 0.0) {
        state->integral += config->anti_windup_gain * saturation_error * input->dt;
        state->integral = clamp_value(state->integral, config->integral_min,
                                      config->integral_max);
    }
    state->previous_error = error;
    state->initialized = 1;
    output->command = command;
    output->unsaturated_command = unsaturated;
    output->error = error;
    output->integral = state->integral;
    output->scheduled_gain = gain;
    output->saturated = fabs(command - unsaturated) > 1e-12;
    return 0;
}

int mosim_cascade_pid_step(const MosimPidConfig *outer_config,
                           const MosimPidConfig *inner_config,
                           MosimCascadePidState *state,
                           const MosimCascadePidInput *input,
                           MosimCascadePidOutput *output)
{
    MosimPidInput outer_input;
    MosimPidInput inner_input;
    MosimPidOutput outer_output;
    MosimPidOutput inner_output;
    int result;
    if (outer_config == NULL || inner_config == NULL || state == NULL ||
        input == NULL || output == NULL) return -1;
    memset(output, 0, sizeof(*output));
    if (input->reset) {
        mosim_pid_reset(&state->outer);
        mosim_pid_reset(&state->inner);
    }
    outer_input.setpoint = input->outer_reference;
    outer_input.measurement = input->outer_measurement;
    outer_input.feedforward = input->feedforward;
    outer_input.schedule = input->schedule;
    outer_input.fuzzy_error = input->fuzzy_error;
    outer_input.neural_residual = input->neural_residual;
    outer_input.dt = input->dt;
    outer_input.reset = 0;
    outer_input.enable = input->enable;
    result = mosim_pid_step(outer_config, &state->outer, &outer_input, &outer_output);
    if (result != 0) { output->status_code = result; return result; }
    if (!input->enable) {
        output->status_code = outer_output.status_code;
        return 0;
    }
    inner_input = outer_input;
    inner_input.setpoint = outer_output.command;
    inner_input.measurement = input->inner_measurement;
    inner_input.reset = 0;
    result = mosim_pid_step(inner_config, &state->inner, &inner_input, &inner_output);
    if (result != 0) { output->status_code = result; return result; }
    output->outer_command = outer_output.command;
    output->command = inner_output.command;
    output->saturated = outer_output.saturated || inner_output.saturated;
    return 0;
}
