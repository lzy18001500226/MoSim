#ifndef MOSIM_PID_ATTITUDE_THRUST_CORE_H
#define MOSIM_PID_ATTITUDE_THRUST_CORE_H

#include "pid_unified_core.h"

#ifdef __cplusplus
extern "C" {
#endif

enum MosimPidAttitudeThrustAlgorithm {
    MOSIM_PID_CASCADE = 1,
    MOSIM_PID_GAIN_SCHEDULED = 2,
    MOSIM_PID_FUZZY = 3,
    MOSIM_PID_NEURAL = 4,
    MOSIM_PID_ANTI_WINDUP = 5,
    MOSIM_PID_FEEDFORWARD_PROFILE = 6
};

typedef struct {
    double x;
    double y;
    double z;
} MosimPidVec3;

typedef struct {
    double w;
    double x;
    double y;
    double z;
} MosimPidQuat;

typedef struct {
    int algorithm_id;
    MosimPidConfig position[3];
    MosimPidConfig velocity[3];
    double mass_kg;
    double gravity_mps2;
    double max_tilt_rad;
    double min_collective_thrust_n;
    double max_collective_thrust_n;
} MosimPidAttitudeThrustParams;

typedef struct {
    MosimPidState position[3];
    MosimPidState velocity[3];
} MosimPidAttitudeThrustState;

typedef struct {
    int algorithm_id;
    double dt;
    MosimPidVec3 position_enu_m;
    MosimPidVec3 velocity_enu_mps;
    MosimPidQuat attitude_enu_flu_wxyz;
    MosimPidVec3 angular_velocity_flu_radps;
    MosimPidVec3 reference_position_enu_m;
    MosimPidVec3 reference_velocity_enu_mps;
    MosimPidVec3 reference_acceleration_enu_mps2;
    double reference_yaw_enu_rad;
    MosimPidVec3 schedule;
    MosimPidVec3 fuzzy_error;
    MosimPidVec3 neural_residual;
    int reset;
    int enable;
} MosimPidAttitudeThrustInput;

typedef struct {
    MosimPidQuat desired_attitude_enu_flu_wxyz;
    double desired_collective_thrust_n;
    MosimPidVec3 desired_acceleration_enu_mps2;
    MosimPidVec3 position_error_enu_m;
    MosimPidVec3 velocity_error_enu_mps;
    MosimPidVec3 scheduled_gain;
    int saturated;
    int status_code;
    int algorithm_id;
} MosimPidAttitudeThrustOutput;

void mosim_pid_attitude_thrust_default_params(
    int algorithm_id,
    MosimPidAttitudeThrustParams *params);
void mosim_pid_attitude_thrust_reset(MosimPidAttitudeThrustState *state);
int mosim_pid_attitude_thrust_step(
    const MosimPidAttitudeThrustParams *params,
    MosimPidAttitudeThrustState *state,
    const MosimPidAttitudeThrustInput *input,
    MosimPidAttitudeThrustOutput *output);

#ifdef __cplusplus
}
#endif

#endif
