/********************************************************************************
 * Copyright (C) 2005-2026, Suzhou Tongyuan Software&Control Technology Co.,Ltd.
 * All rights reserved.
 * 版权所有 (C) 2005-2026， 苏州同元软控技术股份有限公司
 * 保留所有权利。
 *
 * 该文件由MWORKS内核代码生成器自动生成。
 *
 * 文件名称: MoSim_PID_AttitudeThrust_CFunction_Sysblock_private.h
 * 生成时间: 2026-07-16 15:23:16
 *
********************************************************************************/

#ifndef UST_CFUNCTION_SYSBLOCK_PRIVATE_H
#define UST_CFUNCTION_SYSBLOCK_PRIVATE_H

#include "MoSim_PID_AttitudeThrust_CFunction_Sysblock.h"

struct unction_sysblockExtU
{
  MwbDouble algorithm_id_in;
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
  MwbDouble schedule_x_in;
  MwbDouble schedule_y_in;
  MwbDouble schedule_z_in;
  MwbDouble fuzzy_error_x_in;
  MwbDouble fuzzy_error_y_in;
  MwbDouble fuzzy_error_z_in;
  MwbDouble neural_residual_x_in;
  MwbDouble neural_residual_y_in;
  MwbDouble neural_residual_z_in;
  MwbDouble enable_in;
  MwbDouble reset_in;
};

struct unction_sysblockExtY
{
  MwbDouble desired_attitude_w_out;
  MwbDouble desired_attitude_x_out;
  MwbDouble desired_attitude_y_out;
  MwbDouble desired_attitude_z_out;
  MwbDouble desired_collective_thrust_n_out;
  MwbDouble desired_acceleration_x_out;
  MwbDouble desired_acceleration_y_out;
  MwbDouble desired_acceleration_z_out;
  MwbDouble position_error_x_out;
  MwbDouble position_error_y_out;
  MwbDouble position_error_z_out;
  MwbDouble velocity_error_x_out;
  MwbDouble velocity_error_y_out;
  MwbDouble velocity_error_z_out;
  MwbDouble scheduled_gain_x_out;
  MwbDouble scheduled_gain_y_out;
  MwbDouble scheduled_gain_z_out;
  MwbDouble saturated_out;
  MwbDouble status_code_out;
  MwbDouble algorithm_id_out_out;
};

struct ction_sysblockDw
{
  MwbDouble algorithm_id;
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
  MwbDouble schedule_x;
  MwbDouble schedule_y;
  MwbDouble schedule_z;
  MwbDouble fuzzy_error_x;
  MwbDouble fuzzy_error_y;
  MwbDouble fuzzy_error_z;
  MwbDouble neural_residual_x;
  MwbDouble neural_residual_y;
  MwbDouble neural_residual_z;
  MwbDouble enable;
  MwbDouble reset;
};



#endif /* UST_CFUNCTION_SYSBLOCK_PRIVATE_H */

/********************************************************************************
** end of file
********************************************************************************/
