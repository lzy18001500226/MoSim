#ifndef MOSIM_PX4CTRL_G9_FAMILY_CORE_C_H
#define MOSIM_PX4CTRL_G9_FAMILY_CORE_C_H

#ifdef __cplusplus
extern "C" {
#endif

enum MosimPx4ctrlG9ControllerId
{
    MOSIM_PX4CTRL_G9_OFFICIAL_PID = 1,
    MOSIM_PX4CTRL_G9_SE3_BASIC = 2,
    MOSIM_PX4CTRL_G9_DFBC_BASIC = 3,
    MOSIM_PX4CTRL_G9_SMC_BOUNDARY_LAYER = 4,
    MOSIM_PX4CTRL_G9_PID_INDI = 5,
    MOSIM_PX4CTRL_G9_NMPC_OUTER = 6,
    MOSIM_PX4CTRL_G10_L1_AWFF = 7,
    MOSIM_PX4CTRL_G10_SAFETY_FILTER = 8,
    MOSIM_PX4CTRL_G10_FAULT_ALLOCATION = 9,
    MOSIM_PX4CTRL_P10_DFBC_HIGH_ORDER = 10,
    MOSIM_PX4CTRL_P10_DFBC_SMOOTH_ROBUST = 11
};

typedef struct MosimPx4ctrlG9FamilyCVec3
{
    double x;
    double y;
    double z;
} MosimPx4ctrlG9FamilyCVec3;

typedef struct MosimPx4ctrlG9FamilyCQuat
{
    double w;
    double x;
    double y;
    double z;
} MosimPx4ctrlG9FamilyCQuat;

typedef struct MosimPx4ctrlG9FamilyCParams
{
    double kp[3];
    double kv[3];
    double ki[3];
    double smc_lambda[3];
    double smc_eta[3];
    double smc_phi[3];
    double smc_surface_limit[3];
    double indi_gain[3];
    double indi_increment_limit[3];
    double indi_measured_accel_limit[3];
    double indi_accel_lpf_alpha;
    double nmpc_horizon_s;
    double nmpc_position_weight[3];
    double nmpc_velocity_weight[3];
    double nmpc_control_weight[3];
    double nmpc_accel_limit[3];
    double nmpc_increment_limit[3];
    double high_order_body_rate_limit[3];
    double high_order_body_accel_limit[3];
    double smooth_feedback_gain[3];
    double smooth_feedback_bound[3];
    double disturbance_observer_gain[3];
    double disturbance_compensation_limit[3];
    double l1_model_decay;
    double l1_filter_T;
    double l1_gain[3];
    double l1_comp_limit[3];
    double drag_feedforward_gain[3];
    double safety_accel_limit[3];
    double fault_rotor_efficiency[4];
    double fault_allocation_blend;
    double fault_min_efficiency;
    double fault_thrust_comp_limit;
    double integral_limit[3];
    double mass;
    double gravity;
    double hover_percentage;
    double min_normalized_thrust;
    double max_normalized_thrust;
    double tilt_limit_rad;
} MosimPx4ctrlG9FamilyCParams;

typedef struct MosimPx4ctrlG9FamilyCState
{
    double thr2acc;
    double covariance;
    MosimPx4ctrlG9FamilyCVec3 integral_position_error;
    MosimPx4ctrlG9FamilyCVec3 previous_velocity;
    MosimPx4ctrlG9FamilyCVec3 measured_acceleration_lpf;
    MosimPx4ctrlG9FamilyCVec3 previous_command_acceleration;
    MosimPx4ctrlG9FamilyCVec3 disturbance_estimate;
    double previous_measurement_stamp_s;
    int has_previous_velocity;
    int has_previous_measurement_stamp;
} MosimPx4ctrlG9FamilyCState;

typedef struct MosimPx4ctrlG9FamilyCInput
{
    int controller_id;
    double dt;
    MosimPx4ctrlG9FamilyCVec3 position;
    MosimPx4ctrlG9FamilyCVec3 velocity;
    MosimPx4ctrlG9FamilyCQuat attitude;
    MosimPx4ctrlG9FamilyCVec3 angular_velocity;
    MosimPx4ctrlG9FamilyCVec3 reference_position;
    MosimPx4ctrlG9FamilyCVec3 reference_velocity;
    MosimPx4ctrlG9FamilyCVec3 reference_acceleration;
    MosimPx4ctrlG9FamilyCVec3 reference_jerk;
    MosimPx4ctrlG9FamilyCVec3 reference_snap;
    double reference_yaw;
    double reference_yaw_rate;
    double reference_yaw_acceleration;
    double measurement_stamp_s;
    MosimPx4ctrlG9FamilyCQuat imu_attitude;
    MosimPx4ctrlG9FamilyCVec3 imu_angular_velocity;
    int enable;
    int reset;
    int measurement_stamp_valid;
    int enable_disturbance_observer;
} MosimPx4ctrlG9FamilyCInput;

typedef struct MosimPx4ctrlG9FamilyCOutput
{
    MosimPx4ctrlG9FamilyCQuat desired_attitude;
    double normalized_thrust;
    double collective_thrust_n;
    MosimPx4ctrlG9FamilyCVec3 position_error;
    MosimPx4ctrlG9FamilyCVec3 velocity_error;
    MosimPx4ctrlG9FamilyCVec3 sliding_surface;
    MosimPx4ctrlG9FamilyCVec3 desired_acceleration;
    MosimPx4ctrlG9FamilyCVec3 desired_body_rate;
    MosimPx4ctrlG9FamilyCVec3 desired_body_acceleration;
    MosimPx4ctrlG9FamilyCVec3 disturbance_estimate;
    MosimPx4ctrlG9FamilyCVec3 desired_force_n;
    double saturated;
    int status_code;
} MosimPx4ctrlG9FamilyCOutput;

void mosim_px4ctrl_g9_family_c_reset(
    const MosimPx4ctrlG9FamilyCParams *params,
    MosimPx4ctrlG9FamilyCState *state);

void mosim_px4ctrl_g9_family_c_step(
    const MosimPx4ctrlG9FamilyCParams *params,
    MosimPx4ctrlG9FamilyCState *state,
    const MosimPx4ctrlG9FamilyCInput *input,
    MosimPx4ctrlG9FamilyCOutput *output);

void MosimPx4ctrlG9FamilyCStepScalar(
    double controller_id,
    double dt,
    double position_x,
    double position_y,
    double position_z,
    double velocity_x,
    double velocity_y,
    double velocity_z,
    double attitude_w,
    double attitude_x,
    double attitude_y,
    double attitude_z,
    double angular_velocity_x,
    double angular_velocity_y,
    double angular_velocity_z,
    double reference_position_x,
    double reference_position_y,
    double reference_position_z,
    double reference_velocity_x,
    double reference_velocity_y,
    double reference_velocity_z,
    double reference_acceleration_x,
    double reference_acceleration_y,
    double reference_acceleration_z,
    double reference_jerk_x,
    double reference_jerk_y,
    double reference_jerk_z,
    double reference_snap_x,
    double reference_snap_y,
    double reference_snap_z,
    double reference_yaw,
    double reference_yaw_rate,
    double reference_yaw_acceleration,
    double measurement_stamp_s,
    double imu_attitude_w,
    double imu_attitude_x,
    double imu_attitude_y,
    double imu_attitude_z,
    double imu_angular_velocity_x,
    double imu_angular_velocity_y,
    double imu_angular_velocity_z,
    double enable,
    double reset,
    double measurement_stamp_valid,
    double enable_disturbance_observer,
    double kp_x,
    double kp_y,
    double kp_z,
    double kv_x,
    double kv_y,
    double kv_z,
    double ki_x,
    double ki_y,
    double ki_z,
    double smc_lambda_x,
    double smc_lambda_y,
    double smc_lambda_z,
    double smc_eta_x,
    double smc_eta_y,
    double smc_eta_z,
    double smc_phi_x,
    double smc_phi_y,
    double smc_phi_z,
    double smc_surface_limit_x,
    double smc_surface_limit_y,
    double smc_surface_limit_z,
    double indi_gain_x,
    double indi_gain_y,
    double indi_gain_z,
    double indi_increment_limit_x,
    double indi_increment_limit_y,
    double indi_increment_limit_z,
    double indi_measured_accel_limit_x,
    double indi_measured_accel_limit_y,
    double indi_measured_accel_limit_z,
    double indi_accel_lpf_alpha,
    double nmpc_horizon_s,
    double nmpc_position_weight_x,
    double nmpc_position_weight_y,
    double nmpc_position_weight_z,
    double nmpc_velocity_weight_x,
    double nmpc_velocity_weight_y,
    double nmpc_velocity_weight_z,
    double nmpc_control_weight_x,
    double nmpc_control_weight_y,
    double nmpc_control_weight_z,
    double nmpc_accel_limit_x,
    double nmpc_accel_limit_y,
    double nmpc_accel_limit_z,
    double nmpc_increment_limit_x,
    double nmpc_increment_limit_y,
    double nmpc_increment_limit_z,
    double high_order_body_rate_limit_x,
    double high_order_body_rate_limit_y,
    double high_order_body_rate_limit_z,
    double high_order_body_accel_limit_x,
    double high_order_body_accel_limit_y,
    double high_order_body_accel_limit_z,
    double smooth_feedback_gain_x,
    double smooth_feedback_gain_y,
    double smooth_feedback_gain_z,
    double smooth_feedback_bound_x,
    double smooth_feedback_bound_y,
    double smooth_feedback_bound_z,
    double disturbance_observer_gain_x,
    double disturbance_observer_gain_y,
    double disturbance_observer_gain_z,
    double disturbance_compensation_limit_x,
    double disturbance_compensation_limit_y,
    double disturbance_compensation_limit_z,
    double l1_model_decay,
    double l1_filter_T,
    double l1_gain_x,
    double l1_gain_y,
    double l1_gain_z,
    double l1_comp_limit_x,
    double l1_comp_limit_y,
    double l1_comp_limit_z,
    double drag_feedforward_gain_x,
    double drag_feedforward_gain_y,
    double drag_feedforward_gain_z,
    double safety_accel_limit_x,
    double safety_accel_limit_y,
    double safety_accel_limit_z,
    double fault_rotor_efficiency_1,
    double fault_rotor_efficiency_2,
    double fault_rotor_efficiency_3,
    double fault_rotor_efficiency_4,
    double fault_allocation_blend,
    double fault_min_efficiency,
    double fault_thrust_comp_limit,
    double integral_limit_x,
    double integral_limit_y,
    double integral_limit_z,
    double mass,
    double gravity,
    double hover_percentage,
    double min_normalized_thrust,
    double max_normalized_thrust,
    double tilt_limit_rad,
    double *desired_attitude_w,
    double *desired_attitude_x,
    double *desired_attitude_y,
    double *desired_attitude_z,
    double *normalized_thrust,
    double *collective_thrust_N,
    double *position_error_x,
    double *position_error_y,
    double *position_error_z,
    double *velocity_error_x,
    double *velocity_error_y,
    double *velocity_error_z,
    double *sliding_surface_x,
    double *sliding_surface_y,
    double *sliding_surface_z,
    double *desired_acceleration_x,
    double *desired_acceleration_y,
    double *desired_acceleration_z,
    double *desired_body_rate_x,
    double *desired_body_rate_y,
    double *desired_body_rate_z,
    double *desired_body_acceleration_x,
    double *desired_body_acceleration_y,
    double *desired_body_acceleration_z,
    double *disturbance_estimate_x,
    double *disturbance_estimate_y,
    double *disturbance_estimate_z,
    double *desired_force_N_x,
    double *desired_force_N_y,
    double *desired_force_N_z,
    double *saturated,
    double *status_code);

#ifdef __cplusplus
}
#endif

#endif
