#ifndef MOSIM_PX4CTRL_G9A_CORE_C_H
#define MOSIM_PX4CTRL_G9A_CORE_C_H

#ifdef __cplusplus
extern "C" {
#endif

typedef struct MosimPx4ctrlG9ACVec3
{
    double x;
    double y;
    double z;
} MosimPx4ctrlG9ACVec3;

typedef struct MosimPx4ctrlG9ACQuat
{
    double w;
    double x;
    double y;
    double z;
} MosimPx4ctrlG9ACQuat;

typedef struct MosimPx4ctrlG9ACParams
{
    double kp_x;
    double kp_y;
    double kp_z;
    double kv_x;
    double kv_y;
    double kv_z;
    double ki_x;
    double ki_y;
    double ki_z;
    double integral_limit_x;
    double integral_limit_y;
    double integral_limit_z;
    double mass;
    double gravity;
    double hover_percentage;
    double min_normalized_thrust;
    double max_normalized_thrust;
    double tilt_limit_rad;
} MosimPx4ctrlG9ACParams;

typedef struct MosimPx4ctrlG9ACState
{
    double thr2acc;
    double covariance;
    MosimPx4ctrlG9ACVec3 integral_position_error;
} MosimPx4ctrlG9ACState;

typedef struct MosimPx4ctrlG9ACInput
{
    double dt;
    MosimPx4ctrlG9ACVec3 position;
    MosimPx4ctrlG9ACVec3 velocity;
    MosimPx4ctrlG9ACQuat attitude;
    MosimPx4ctrlG9ACVec3 angular_velocity;
    MosimPx4ctrlG9ACVec3 reference_position;
    MosimPx4ctrlG9ACVec3 reference_velocity;
    MosimPx4ctrlG9ACVec3 reference_acceleration;
    double reference_yaw;
    double reference_yaw_rate;
    MosimPx4ctrlG9ACQuat imu_attitude;
    MosimPx4ctrlG9ACVec3 imu_angular_velocity;
    int enable;
    int reset;
} MosimPx4ctrlG9ACInput;

typedef struct MosimPx4ctrlG9ACOutput
{
    MosimPx4ctrlG9ACQuat desired_attitude;
    double normalized_thrust;
    double collective_thrust_n;
    MosimPx4ctrlG9ACVec3 position_error;
    MosimPx4ctrlG9ACVec3 velocity_error;
    MosimPx4ctrlG9ACVec3 desired_acceleration;
    MosimPx4ctrlG9ACVec3 desired_force_n;
    double saturated;
    int status_code;
} MosimPx4ctrlG9ACOutput;

void mosim_px4ctrl_g9a_c_reset(
    const MosimPx4ctrlG9ACParams *params,
    MosimPx4ctrlG9ACState *state);

void mosim_px4ctrl_g9a_c_step(
    const MosimPx4ctrlG9ACParams *params,
    MosimPx4ctrlG9ACState *state,
    const MosimPx4ctrlG9ACInput *input,
    MosimPx4ctrlG9ACOutput *output);

void MosimPx4ctrlG9AOfficialPidCStepScalar(
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
    double reference_yaw,
    double reference_yaw_rate,
    double imu_attitude_w,
    double imu_attitude_x,
    double imu_attitude_y,
    double imu_attitude_z,
    double imu_angular_velocity_x,
    double imu_angular_velocity_y,
    double imu_angular_velocity_z,
    double enable,
    double reset,
    double kp_x,
    double kp_y,
    double kp_z,
    double kv_x,
    double kv_y,
    double kv_z,
    double ki_x,
    double ki_y,
    double ki_z,
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
    double *desired_acceleration_x,
    double *desired_acceleration_y,
    double *desired_acceleration_z,
    double *desired_force_N_x,
    double *desired_force_N_y,
    double *desired_force_N_z,
    double *saturated,
    double *status_code);

#ifdef __cplusplus
}
#endif

#endif
