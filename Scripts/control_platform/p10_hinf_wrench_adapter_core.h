#ifndef MOSIM_P10_HINF_WRENCH_ADAPTER_CORE_H
#define MOSIM_P10_HINF_WRENCH_ADAPTER_CORE_H

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    double state[12];
    double reference[12];
    int enable;
    int reset;
} MosimP10HinfAdapterInput;

typedef struct {
    double mass;
    double gravity;
    double force_min_n;
    double force_max_n;
    double torque_limit_nm;
    double attitude_stiffness[3];
    double hover_percentage;
    double tilt_limit_rad;
    double yaw_correction_limit_rad;
    double min_normalized_thrust;
    double max_normalized_thrust;
} MosimP10HinfAdapterParams;

typedef struct {
    double wrench[4];
    double desired_attitude[4];
    double normalized_thrust;
    double collective_thrust_n;
    double adapted_euler[3];
    int saturated;
    int status_code;
    int source_command_variant;
    int adapted_command_variant;
} MosimP10HinfAdapterOutput;

void mosim_p10_hinf_adapter_default_params(MosimP10HinfAdapterParams *params);
int mosim_p10_hinf_adapter_step(
    const MosimP10HinfAdapterParams *params,
    const MosimP10HinfAdapterInput *input,
    MosimP10HinfAdapterOutput *output);

void MosimP10HinfWrenchAdapterStepScalar(
    double state_roll,
    double state_pitch,
    double state_yaw,
    double state_p,
    double state_q,
    double state_r,
    double state_u,
    double state_v,
    double state_w,
    double state_x,
    double state_y,
    double state_z,
    double reference_roll,
    double reference_pitch,
    double reference_yaw,
    double reference_p,
    double reference_q,
    double reference_r,
    double reference_u,
    double reference_v,
    double reference_w,
    double reference_x,
    double reference_y,
    double reference_z,
    double enable,
    double reset,
    double mass,
    double gravity,
    double force_min_n,
    double force_max_n,
    double torque_limit_nm,
    double roll_stiffness_nm_per_rad,
    double pitch_stiffness_nm_per_rad,
    double yaw_stiffness_nm_per_rad,
    double hover_percentage,
    double tilt_limit_rad,
    double yaw_correction_limit_rad,
    double min_normalized_thrust,
    double max_normalized_thrust,
    double *wrench_force_n,
    double *wrench_tau_x_nm,
    double *wrench_tau_y_nm,
    double *wrench_tau_z_nm,
    double *desired_attitude_w,
    double *desired_attitude_x,
    double *desired_attitude_y,
    double *desired_attitude_z,
    double *normalized_thrust,
    double *collective_thrust_n,
    double *adapted_roll_rad,
    double *adapted_pitch_rad,
    double *adapted_yaw_rad,
    double *saturated,
    double *status_code,
    double *source_command_variant,
    double *adapted_command_variant);

#ifdef __cplusplus
}
#endif

#endif
