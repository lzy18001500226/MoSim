#ifndef MOSIM_ENHANCEMENT_ATTITUDE_THRUST_CORE_H
#define MOSIM_ENHANCEMENT_ATTITUDE_THRUST_CORE_H

#ifdef __cplusplus
extern "C" {
#endif

enum { MOSIM_ENHANCEMENT_ILC_BINS = 64 };

enum MosimEnhancementControllerId {
    MOSIM_ENHANCEMENT_L1_ADAPTIVE = 1,
    MOSIM_ENHANCEMENT_AWFF = 2,
    MOSIM_ENHANCEMENT_COMPLETE_ADRC = 3,
    MOSIM_ENHANCEMENT_STANDARDIZED_INDI = 4,
    MOSIM_ENHANCEMENT_PARAMETER_SCHEDULING = 5,
    MOSIM_ENHANCEMENT_ILC = 6
};

typedef struct {
    double dt;
    double position[3];
    double velocity[3];
    double measured_acceleration[3];
    double reference_position[3];
    double reference_velocity[3];
    double reference_acceleration[3];
    double reference_yaw;
    int trajectory_phase_bin;
    int repeat_complete;
    int enable;
    int reset;
} MosimEnhancementInput;

typedef struct {
    double position_gain[3];
    double velocity_gain[3];
    double acceleration_limit[3];
    double compensation_limit[3];
    double observer_bandwidth[3];
    double l1_adaptation_gain[3];
    double l1_filter_time_constant;
    double awff_drag_gain[3];
    double indi_gain[3];
    double indi_increment_limit[3];
    double adrc_td_bandwidth[3];
    double adrc_eso_bandwidth[3];
    double adrc_nonlinear_alpha;
    double schedule_error_threshold;
    double schedule_high_gain_scale;
    double ilc_learning_gain[3];
    double ilc_forgetting_factor;
    double mass_kg;
    double gravity_mps2;
    double hover_percentage;
    double max_tilt_rad;
    double min_collective_thrust_n;
    double max_collective_thrust_n;
} MosimEnhancementParams;

typedef struct {
    double disturbance_estimate[3];
    double previous_command_acceleration[3];
    double td_position[3];
    double td_velocity[3];
    double eso_position[3];
    double eso_velocity[3];
    double eso_disturbance[3];
    double ilc_memory[MOSIM_ENHANCEMENT_ILC_BINS][3];
    unsigned long step_count;
} MosimEnhancementState;

typedef struct {
    double desired_acceleration[3];
    double desired_attitude_wxyz[4];
    double normalized_thrust;
    double collective_thrust_n;
    double nominal_acceleration[3];
    double compensation[3];
    double observer_state[3];
    double effective_gain_scale;
    int saturated;
    int status_code;
} MosimEnhancementOutput;

void mosim_enhancement_default_params(MosimEnhancementParams *params);
void mosim_enhancement_reset(MosimEnhancementState *state);
int mosim_enhancement_step(
    int controller_id,
    const MosimEnhancementParams *params,
    MosimEnhancementState *state,
    const MosimEnhancementInput *input,
    MosimEnhancementOutput *output);

#ifdef __cplusplus
}
#endif

#endif
