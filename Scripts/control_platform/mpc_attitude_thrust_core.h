#ifndef MOSIM_MPC_ATTITUDE_THRUST_CORE_H
#define MOSIM_MPC_ATTITUDE_THRUST_CORE_H

#ifdef __cplusplus
extern "C" {
#endif

enum MosimMpcControllerId {
    MOSIM_MPC_LINEAR = 1,
    MOSIM_MPC_ROBUST = 2,
    MOSIM_MPC_ADAPTIVE = 3,
    MOSIM_MPC_TUBE = 4,
    MOSIM_MPC_EXPLICIT_GAIN_SCHEDULED = 5,
    MOSIM_MPC_ILQR = 6,
    MOSIM_MPC_MPPI = 7
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
} MosimMpcInput;

typedef struct {
    double horizon_s;
    double position_weight[3];
    double velocity_weight[3];
    double control_weight[3];
    double acceleration_limit[3];
    double increment_limit[3];
    double robust_bound[3];
    double tube_position_gain[3];
    double tube_velocity_gain[3];
    double adaptive_rate;
    double adaptive_scale_min;
    double adaptive_scale_max;
    double schedule_error_threshold;
    double ilqr_step_size;
    double mppi_temperature;
    double mppi_noise_scale[3];
    double mass_kg;
    double gravity_mps2;
    double hover_percentage;
    double max_tilt_rad;
    double min_collective_thrust_n;
    double max_collective_thrust_n;
} MosimMpcParams;

typedef struct {
    double previous_acceleration[3];
    double adaptive_scale;
    unsigned long step_count;
} MosimMpcState;

typedef struct {
    double desired_acceleration[3];
    double desired_attitude_wxyz[4];
    double normalized_thrust;
    double collective_thrust_n;
    double unconstrained_acceleration[3];
    double auxiliary[3];
    double solver_cost;
    int solver_iterations;
    int saturated;
    int status_code;
} MosimMpcOutput;

void mosim_mpc_default_params(MosimMpcParams *params);
void mosim_mpc_reset(MosimMpcState *state);
int mosim_mpc_step(
    int controller_id,
    const MosimMpcParams *params,
    MosimMpcState *state,
    const MosimMpcInput *input,
    MosimMpcOutput *output);

#ifdef __cplusplus
}
#endif

#endif
