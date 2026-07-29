/********************************************************************************
 * Copyright (C) 2005-2026, Suzhou Tongyuan Software&Control Technology Co.,Ltd.
 * All rights reserved.
 * 版权所有 (C) 2005-2026， 苏州同元软控技术股份有限公司
 * 保留所有权利。
 *
 * 该文件由MWORKS内核代码生成器自动生成。
 *
 * 文件名称: PX4CTRL_Core_CFunction_Sysblock_private.h
 * 生成时间: 2026-06-29 09:26:55
 *
********************************************************************************/

#ifndef N_SYSBLOCK_PRIVATE_H
#define N_SYSBLOCK_PRIVATE_H

#include "PX4CTRL_Core_CFunction_Sysblock.h"

struct lockExtU
{
  MwbDouble dt_in;
  MwbDouble position_x_in;
  MwbDouble position_y_in;
  MwbDouble position_z_in;
  MwbDouble velocity_x_in;
  MwbDouble velocity_y_in;
  MwbDouble velocity_z_in;
  MwbDouble attitude_w_in;
  MwbDouble attitude_x_in;
  MwbDouble attitude_y_in;
  MwbDouble attitude_z_in;
  MwbDouble angular_velocity_x_in;
  MwbDouble angular_velocity_y_in;
  MwbDouble angular_velocity_z_in;
  MwbDouble reference_position_x_in;
  MwbDouble reference_position_y_in;
  MwbDouble reference_position_z_in;
  MwbDouble reference_velocity_x_in;
  MwbDouble reference_velocity_y_in;
  MwbDouble reference_velocity_z_in;
  MwbDouble reference_acceleration_x_in;
  MwbDouble reference_acceleration_y_in;
  MwbDouble reference_acceleration_z_in;
  MwbDouble reference_yaw_in;
  MwbDouble reference_yaw_rate_in;
  MwbDouble imu_attitude_w_in;
  MwbDouble imu_attitude_x_in;
  MwbDouble imu_attitude_y_in;
  MwbDouble imu_attitude_z_in;
  MwbDouble imu_angular_velocity_x_in;
  MwbDouble imu_angular_velocity_y_in;
  MwbDouble imu_angular_velocity_z_in;
  MwbDouble enable_in;
  MwbDouble reset_in;
  MwbDouble kp_x_in;
  MwbDouble kp_y_in;
  MwbDouble kp_z_in;
  MwbDouble kv_x_in;
  MwbDouble kv_y_in;
  MwbDouble kv_z_in;
  MwbDouble mass_in;
  MwbDouble gravity_in;
  MwbDouble hover_percentage_in;
};

struct lockExtY
{
  MwbDouble desired_attitude_w_out;
  MwbDouble desired_attitude_x_out;
  MwbDouble desired_attitude_y_out;
  MwbDouble desired_attitude_z_out;
  MwbDouble normalized_thrust_out;
  MwbDouble collective_thrust_N_out;
  MwbDouble position_error_x_out;
  MwbDouble position_error_y_out;
  MwbDouble position_error_z_out;
  MwbDouble velocity_error_x_out;
  MwbDouble velocity_error_y_out;
  MwbDouble velocity_error_z_out;
  MwbDouble desired_acceleration_x_out;
  MwbDouble desired_acceleration_y_out;
  MwbDouble desired_acceleration_z_out;
  MwbDouble desired_force_N_x_out;
  MwbDouble desired_force_N_y_out;
  MwbDouble desired_force_N_z_out;
  MwbDouble status_code_out;
};

struct ckDw
{
  MwbDouble dt;
  MwbDouble position_x;
  MwbDouble position_y;
  MwbDouble position_z;
  MwbDouble velocity_x;
  MwbDouble velocity_y;
  MwbDouble velocity_z;
  MwbDouble attitude_w;
  MwbDouble attitude_x;
  MwbDouble attitude_y;
  MwbDouble attitude_z;
  MwbDouble angular_velocity_x;
  MwbDouble angular_velocity_y;
  MwbDouble angular_velocity_z;
  MwbDouble reference_position_x;
  MwbDouble reference_position_y;
  MwbDouble reference_position_z;
  MwbDouble reference_velocity_x;
  MwbDouble reference_velocity_y;
  MwbDouble reference_velocity_z;
  MwbDouble reference_acceleration_x;
  MwbDouble reference_acceleration_y;
  MwbDouble reference_acceleration_z;
  MwbDouble reference_yaw;
  MwbDouble reference_yaw_rate;
  MwbDouble imu_attitude_w;
  MwbDouble imu_attitude_x;
  MwbDouble imu_attitude_y;
  MwbDouble imu_attitude_z;
  MwbDouble imu_angular_velocity_x;
  MwbDouble imu_angular_velocity_y;
  MwbDouble imu_angular_velocity_z;
  MwbDouble enable;
  MwbDouble reset;
  MwbDouble kp_x;
  MwbDouble kp_y;
  MwbDouble kp_z;
  MwbDouble kv_x;
  MwbDouble kv_y;
  MwbDouble kv_z;
  MwbDouble mass;
  MwbDouble gravity;
  MwbDouble hover_percentage;
};



#endif /* N_SYSBLOCK_PRIVATE_H */

/********************************************************************************
** end of file
********************************************************************************/
