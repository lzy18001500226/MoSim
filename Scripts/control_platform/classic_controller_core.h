#ifndef MOSIM_CLASSIC_CONTROLLER_CORE_H
#define MOSIM_CLASSIC_CONTROLLER_CORE_H

#ifdef __cplusplus
extern "C" {
#endif
#define MOSIM_CLASSIC_FOPID_MEMORY 16

enum MosimClassicControllerId {
    MOSIM_CLASSIC_POLE_PLACEMENT_LUENBERGER = 1,
    MOSIM_CLASSIC_MRAC = 2,
    MOSIM_CLASSIC_NDI = 3,
    MOSIM_CLASSIC_FOPID = 4,
    MOSIM_CLASSIC_H2_STATE_FEEDBACK = 5
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
} MosimClassicInput;

typedef struct {
    double pole_position_gain[3];
    double pole_velocity_gain[3];
    double observer_position_gain[3];
    double observer_velocity_gain[3];
    double mrac_reference_omega[3];
    double mrac_reference_zeta[3];
    double mrac_position_gain[3];
    double mrac_velocity_gain[3];
    double mrac_adaptation_gain[3];
    double mrac_parameter_limit[3];
    double ndi_position_gain[3];
    double ndi_velocity_gain[3];
    double ndi_linear_drag[3];
    double fopid_kp[3];
    double fopid_ki[3];
    double fopid_kd[3];
    double fopid_lambda;
    double fopid_mu;
    double h2_position_gain[3];
    double h2_velocity_gain[3];
    double mass_kg;
    double gravity_mps2;
    double hover_percentage;
    double max_tilt_rad;
    double min_collective_thrust_n;
    double max_collective_thrust_n;
} MosimClassicParams;

typedef struct {
    double observer_position[3];
    double observer_velocity[3];
    double previous_virtual_acceleration[3];
    int observer_initialized;
    double reference_model_position[3];
    double reference_model_velocity[3];
    double mrac_position_delta[3];
    double mrac_velocity_delta[3];
    int reference_model_initialized;
    double fopid_error_history[3][MOSIM_CLASSIC_FOPID_MEMORY];
    int fopid_sample_count;
} MosimClassicState;

typedef struct {
    double desired_acceleration[3];
    double desired_attitude_wxyz[4];
    double normalized_thrust;
    double collective_thrust_n;
    double observer_position[3];
    double observer_velocity[3];
    double reference_model_position[3];
    double reference_model_velocity[3];
    double adaptive_position_delta[3];
    double adaptive_velocity_delta[3];
    double fractional_integral[3];
    double fractional_derivative[3];
    int saturated;
    int status_code;
} MosimClassicOutput;

void mosim_classic_default_params(MosimClassicParams *params);
void mosim_classic_reset(MosimClassicState *state);
int mosim_classic_step(
    int controller_id,
    const MosimClassicParams *params,
    MosimClassicState *state,
    const MosimClassicInput *input,
    MosimClassicOutput *output);

#ifdef __cplusplus
}
#endif

#endif
