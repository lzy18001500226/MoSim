#include "learning_control_core.h"
#include "learning_control_weights.h"

#include <math.h>
#include <stddef.h>

#define MOSIM_NEURAL_RESIDUAL_LIMIT 0.6
#define MOSIM_RL_SCHEDULE_LIMIT 0.25

static double clamp_value(double value, double lower, double upper)
{
    if (value < lower) return lower;
    if (value > upper) return upper;
    return value;
}

void mosim_learning_zero_output(MosimLearningOutput *output, int status_code)
{
    size_t index;
    if (output == NULL) return;
    for (index = 0; index < MOSIM_LEARNING_ACTION_SIZE; ++index) output->values[index] = 0.0;
    output->status_code = status_code;
    output->fallback_active = status_code != MOSIM_LEARNING_STATUS_OK;
}

static int valid_input(const MosimLearningInput *input)
{
    size_t index;
    if (input == NULL) return 0;
    for (index = 0; index < MOSIM_LEARNING_OBSERVATION_SIZE; ++index) {
        if (!isfinite(input->values[index])) return 0;
    }
    return 1;
}

static int prepare_input(const MosimLearningInput *input, double normalized[MOSIM_LEARNING_OBSERVATION_SIZE])
{
    size_t index;
    if (!valid_input(input)) return 0;
    for (index = 0; index < MOSIM_LEARNING_OBSERVATION_SIZE; ++index) {
        normalized[index] = clamp_value(
            input->values[index] / MOSIM_LEARNING_OBSERVATION_SCALE[index], -1.0, 1.0);
    }
    return 1;
}

int mosim_neural_residual_step(const MosimLearningInput *input, MosimLearningOutput *output)
{
    double normalized[MOSIM_LEARNING_OBSERVATION_SIZE];
    double hidden[MOSIM_NEURAL_HIDDEN_SIZE];
    size_t input_index;
    size_t hidden_index;
    size_t output_index;
    if (output == NULL) return -1;
    mosim_learning_zero_output(output, MOSIM_LEARNING_STATUS_FALLBACK);
    if (!valid_input(input)) return -1;
    if (!input->enable) {
        mosim_learning_zero_output(output, MOSIM_LEARNING_STATUS_DISABLED);
        return 0;
    }
    if (!prepare_input(input, normalized)) return -1;
    for (hidden_index = 0; hidden_index < MOSIM_NEURAL_HIDDEN_SIZE; ++hidden_index) {
        double value = MOSIM_NEURAL_B1[hidden_index];
        for (input_index = 0; input_index < MOSIM_LEARNING_OBSERVATION_SIZE; ++input_index) {
            value += normalized[input_index] *
                     MOSIM_NEURAL_W1[input_index * MOSIM_NEURAL_HIDDEN_SIZE + hidden_index];
        }
        hidden[hidden_index] = tanh(value);
    }
    for (output_index = 0; output_index < MOSIM_LEARNING_ACTION_SIZE; ++output_index) {
        double value = MOSIM_NEURAL_B2[output_index];
        for (hidden_index = 0; hidden_index < MOSIM_NEURAL_HIDDEN_SIZE; ++hidden_index) {
            value += hidden[hidden_index] *
                     MOSIM_NEURAL_W2[hidden_index * MOSIM_LEARNING_ACTION_SIZE + output_index];
        }
        if (!isfinite(value)) return -1;
        output->values[output_index] = clamp_value(
            value, -MOSIM_NEURAL_RESIDUAL_LIMIT, MOSIM_NEURAL_RESIDUAL_LIMIT);
    }
    output->status_code = MOSIM_LEARNING_STATUS_OK;
    output->fallback_active = 0;
    return 0;
}

int mosim_rl_gain_scheduler_step(const MosimLearningInput *input, MosimLearningOutput *output)
{
    double normalized[MOSIM_LEARNING_OBSERVATION_SIZE];
    double hidden1[MOSIM_RL_HIDDEN_SIZE];
    double hidden2[MOSIM_RL_HIDDEN_SIZE];
    size_t input_index;
    size_t hidden_index;
    size_t output_index;
    if (output == NULL) return -1;
    mosim_learning_zero_output(output, MOSIM_LEARNING_STATUS_FALLBACK);
    if (!valid_input(input)) return -1;
    if (!input->enable) {
        mosim_learning_zero_output(output, MOSIM_LEARNING_STATUS_DISABLED);
        return 0;
    }
    if (!prepare_input(input, normalized)) return -1;
    for (hidden_index = 0; hidden_index < MOSIM_RL_HIDDEN_SIZE; ++hidden_index) {
        double value = MOSIM_RL_B1[hidden_index];
        for (input_index = 0; input_index < MOSIM_LEARNING_OBSERVATION_SIZE; ++input_index) {
            value += normalized[input_index] *
                     MOSIM_RL_W1[input_index * MOSIM_RL_HIDDEN_SIZE + hidden_index];
        }
        hidden1[hidden_index] = tanh(value);
    }
    for (hidden_index = 0; hidden_index < MOSIM_RL_HIDDEN_SIZE; ++hidden_index) {
        double value = MOSIM_RL_B2[hidden_index];
        for (input_index = 0; input_index < MOSIM_RL_HIDDEN_SIZE; ++input_index) {
            value += hidden1[input_index] *
                     MOSIM_RL_W2[input_index * MOSIM_RL_HIDDEN_SIZE + hidden_index];
        }
        hidden2[hidden_index] = tanh(value);
    }
    for (output_index = 0; output_index < MOSIM_LEARNING_ACTION_SIZE; ++output_index) {
        double value = MOSIM_RL_B3[output_index];
        for (hidden_index = 0; hidden_index < MOSIM_RL_HIDDEN_SIZE; ++hidden_index) {
            value += hidden2[hidden_index] *
                     MOSIM_RL_W3[hidden_index * MOSIM_LEARNING_ACTION_SIZE + output_index];
        }
        if (!isfinite(value)) return -1;
        output->values[output_index] = clamp_value(
            value, 0.0, MOSIM_RL_SCHEDULE_LIMIT);
    }
    output->status_code = MOSIM_LEARNING_STATUS_OK;
    output->fallback_active = 0;
    return 0;
}

const char *mosim_learning_artifact_sha256(void)
{
    return MOSIM_LEARNING_ARTIFACT_SHA256;
}
