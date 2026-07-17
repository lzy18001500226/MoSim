#ifndef MOSIM_LEARNING_CONTROL_CORE_H
#define MOSIM_LEARNING_CONTROL_CORE_H

#define MOSIM_LEARNING_OBSERVATION_SIZE 12
#define MOSIM_LEARNING_ACTION_SIZE 3
#define MOSIM_NEURAL_HIDDEN_SIZE 12
#define MOSIM_RL_HIDDEN_SIZE 16

#ifdef __cplusplus
extern "C" {
#endif

enum MosimLearningStatus {
    MOSIM_LEARNING_STATUS_OK = 0,
    MOSIM_LEARNING_STATUS_DISABLED = 1,
    MOSIM_LEARNING_STATUS_FALLBACK = 2
};

typedef struct {
    double values[MOSIM_LEARNING_OBSERVATION_SIZE];
    int enable;
} MosimLearningInput;

typedef struct {
    double values[MOSIM_LEARNING_ACTION_SIZE];
    int status_code;
    int fallback_active;
} MosimLearningOutput;

void mosim_learning_zero_output(MosimLearningOutput *output, int status_code);
int mosim_neural_residual_step(const MosimLearningInput *input, MosimLearningOutput *output);
int mosim_rl_gain_scheduler_step(const MosimLearningInput *input, MosimLearningOutput *output);
const char *mosim_learning_artifact_sha256(void);

#ifdef __cplusplus
}
#endif

#endif
