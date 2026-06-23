#ifndef MOSIM_PX4CTRL_GOLDEN_SLICE_CORE_C_H
#define MOSIM_PX4CTRL_GOLDEN_SLICE_CORE_C_H

#ifdef __cplusplus
extern "C" {
#endif

typedef struct MosimPx4ctrlCoreCVec3
{
    double x;
    double y;
    double z;
} MosimPx4ctrlCoreCVec3;

typedef struct MosimPx4ctrlCoreCQuat
{
    double w;
    double x;
    double y;
    double z;
} MosimPx4ctrlCoreCQuat;

typedef struct MosimPx4ctrlCoreCParams
{
    double kp_x;
    double kp_y;
    double kp_z;
    double kv_x;
    double kv_y;
    double kv_z;
    double mass;
    double gravity;
    double hover_percentage;
} MosimPx4ctrlCoreCParams;

typedef struct MosimPx4ctrlCoreCState
{
    double thr2acc;
    double covariance;
} MosimPx4ctrlCoreCState;

typedef struct MosimPx4ctrlCoreCInput
{
    double dt;
    MosimPx4ctrlCoreCVec3 position;
    MosimPx4ctrlCoreCVec3 velocity;
    MosimPx4ctrlCoreCQuat attitude;
    MosimPx4ctrlCoreCVec3 angular_velocity;
    MosimPx4ctrlCoreCVec3 reference_position;
    MosimPx4ctrlCoreCVec3 reference_velocity;
    MosimPx4ctrlCoreCVec3 reference_acceleration;
    double reference_yaw;
    double reference_yaw_rate;
    MosimPx4ctrlCoreCQuat imu_attitude;
    MosimPx4ctrlCoreCVec3 imu_angular_velocity;
    int enable;
    int reset;
} MosimPx4ctrlCoreCInput;

typedef struct MosimPx4ctrlCoreCOutput
{
    MosimPx4ctrlCoreCQuat desired_attitude;
    double normalized_thrust;
    double collective_thrust_n;
    MosimPx4ctrlCoreCVec3 position_error;
    MosimPx4ctrlCoreCVec3 velocity_error;
    MosimPx4ctrlCoreCVec3 desired_acceleration;
    MosimPx4ctrlCoreCVec3 desired_force_n;
    int status_code;
} MosimPx4ctrlCoreCOutput;

void mosim_px4ctrl_core_c_reset(
    const MosimPx4ctrlCoreCParams *params,
    MosimPx4ctrlCoreCState *state);

void mosim_px4ctrl_core_c_step(
    const MosimPx4ctrlCoreCParams *params,
    MosimPx4ctrlCoreCState *state,
    const MosimPx4ctrlCoreCInput *input,
    MosimPx4ctrlCoreCOutput *output);

void MosimPx4ctrlCoreCStepScalar(
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
    double mass,
    double gravity,
    double hover_percentage,
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
    double *status_code);

#ifdef __cplusplus
}
#endif

#endif
