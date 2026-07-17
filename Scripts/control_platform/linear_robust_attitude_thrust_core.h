#ifndef MOSIM_LINEAR_ROBUST_ATTITUDE_THRUST_CORE_H
#define MOSIM_LINEAR_ROBUST_ATTITUDE_THRUST_CORE_H

#ifdef __cplusplus
extern "C" {
#endif

enum MosimLinearRobustControllerId {
    MOSIM_LINEAR_ROBUST_LQG = 1,
    MOSIM_LINEAR_ROBUST_FEEDBACK_LINEARIZATION = 2,
    MOSIM_LINEAR_ROBUST_PASSIVITY = 3,
    MOSIM_LINEAR_ROBUST_ADAPTIVE_BACKSTEPPING = 4
};

typedef struct {
    double dt;
    double position[3];
    double velocity[3];
    double reference_position[3];
    double reference_velocity[3];
    double reference_acceleration[3];
    double reference_yaw;
    int enable;
    int reset;
} MosimLinearRobustInput;

typedef struct {
    double position_gain[3];
    double velocity_gain[3];
    double observer_position_gain[3];
    double observer_velocity_gain[3];
    double backstepping_k1[3];
    double backstepping_k2[3];
    double adaptive_gain[3];
    double adaptive_limit[3];
    double mass_kg;
    double gravity_mps2;
    double hover_percentage;
    double max_tilt_rad;
    double min_collective_thrust_n;
    double max_collective_thrust_n;
} MosimLinearRobustParams;

typedef struct {
    double estimated_position[3];
    double estimated_velocity[3];
    double previous_command_acceleration[3];
    double adaptive_disturbance[3];
    int observer_initialized;
} MosimLinearRobustState;

typedef struct {
    double desired_acceleration[3];
    double desired_attitude_wxyz[4];
    double normalized_thrust;
    double collective_thrust_n;
    double estimated_position[3];
    double estimated_velocity[3];
    double adaptive_disturbance[3];
    double storage_function;
    int saturated;
    int status_code;
} MosimLinearRobustOutput;

void mosim_linear_robust_default_params(MosimLinearRobustParams *params);
void mosim_linear_robust_reset(MosimLinearRobustState *state);
int mosim_linear_robust_step(
    int controller_id,
    const MosimLinearRobustParams *params,
    MosimLinearRobustState *state,
    const MosimLinearRobustInput *input,
    MosimLinearRobustOutput *output);

#ifdef __cplusplus
}
#endif

#endif
