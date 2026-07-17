#ifndef MOSIM_LEARNING_ATTITUDE_THRUST_CORE_H
#define MOSIM_LEARNING_ATTITUDE_THRUST_CORE_H

#include "learning_control_core.h"
#include "pid_attitude_thrust_core.h"

#ifdef __cplusplus
extern "C" {
#endif

enum MosimLearningControllerMode {
    MOSIM_LEARNING_NEURAL_RESIDUAL = 1,
    MOSIM_LEARNING_RL_GAIN_SCHEDULER = 2
};

typedef struct {
    int mode;
    double dt;
    MosimPidVec3 position_enu_m;
    MosimPidVec3 velocity_enu_mps;
    MosimPidQuat attitude_enu_flu_wxyz;
    MosimPidVec3 angular_velocity_flu_radps;
    MosimPidVec3 reference_position_enu_m;
    MosimPidVec3 reference_velocity_enu_mps;
    MosimPidVec3 reference_acceleration_enu_mps2;
    double reference_yaw_enu_rad;
    double mass_kg;
    double gravity_mps2;
    double hover_percentage;
    double max_tilt_rad;
    double min_collective_thrust_n;
    double max_collective_thrust_n;
    int reset;
    int enable;
    int learning_enable;
} MosimLearningAttitudeThrustInput;

typedef struct {
    MosimPidAttitudeThrustOutput control;
    MosimLearningOutput learning;
    double normalized_thrust;
    int mode;
    int fallback_active;
    int status_code;
} MosimLearningAttitudeThrustOutput;

typedef struct {
    MosimPidAttitudeThrustState controller;
    int previous_mode;
} MosimLearningAttitudeThrustState;

void mosim_learning_attitude_thrust_reset(MosimLearningAttitudeThrustState *state);
int mosim_learning_attitude_thrust_step(
    MosimLearningAttitudeThrustState *state,
    const MosimLearningAttitudeThrustInput *input,
    MosimLearningAttitudeThrustOutput *output);

#ifdef __cplusplus
}
#endif

#endif
