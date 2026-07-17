/********************************************************************************
 * Copyright (C) 2005-2026, Suzhou Tongyuan Software&Control Technology Co.,Ltd.
 * All rights reserved.
 * 版权所有 (C) 2005-2026， 苏州同元软控技术股份有限公司
 * 保留所有权利。
 *
 * 该文件由MWORKS内核代码生成器自动生成。
 *
 * 文件名称: MoSim_Classic_CFunction_Sysblock_private.h
 * 生成时间: 2026-07-17 20:29:46
 *
********************************************************************************/

#ifndef ON_SYSBLOCK_PRIVATE_H
#define ON_SYSBLOCK_PRIVATE_H

#include "MoSim_Classic_CFunction_Sysblock.h"

struct blockExtU
{
  MwbDouble controller_id_in;
  MwbDouble dt_in;
  MwbDouble position_x_in;
  MwbDouble position_y_in;
  MwbDouble position_z_in;
  MwbDouble velocity_x_in;
  MwbDouble velocity_y_in;
  MwbDouble velocity_z_in;
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
  MwbDouble enable_in;
  MwbDouble reset_in;
};

struct blockExtY
{
  MwbDouble desired_acceleration_x_out;
  MwbDouble desired_acceleration_y_out;
  MwbDouble desired_acceleration_z_out;
  MwbDouble desired_attitude_w_out;
  MwbDouble desired_attitude_x_out;
  MwbDouble desired_attitude_y_out;
  MwbDouble desired_attitude_z_out;
  MwbDouble observer_position_x_out;
  MwbDouble observer_position_y_out;
  MwbDouble observer_position_z_out;
  MwbDouble observer_velocity_x_out;
  MwbDouble observer_velocity_y_out;
  MwbDouble observer_velocity_z_out;
  MwbDouble reference_model_position_x_out;
  MwbDouble reference_model_position_y_out;
  MwbDouble reference_model_position_z_out;
  MwbDouble reference_model_velocity_x_out;
  MwbDouble reference_model_velocity_y_out;
  MwbDouble reference_model_velocity_z_out;
  MwbDouble adaptive_position_delta_x_out;
  MwbDouble adaptive_position_delta_y_out;
  MwbDouble adaptive_position_delta_z_out;
  MwbDouble adaptive_velocity_delta_x_out;
  MwbDouble adaptive_velocity_delta_y_out;
  MwbDouble adaptive_velocity_delta_z_out;
  MwbDouble fractional_integral_x_out;
  MwbDouble fractional_integral_y_out;
  MwbDouble fractional_integral_z_out;
  MwbDouble fractional_derivative_x_out;
  MwbDouble fractional_derivative_y_out;
  MwbDouble fractional_derivative_z_out;
  MwbDouble normalized_thrust_out;
  MwbDouble collective_thrust_n_out;
  MwbDouble saturated_out;
  MwbDouble status_code_out;
};

struct ockDw
{
  MwbDouble controller_id;
  MwbDouble dt;
  MwbDouble position_x;
  MwbDouble position_y;
  MwbDouble position_z;
  MwbDouble velocity_x;
  MwbDouble velocity_y;
  MwbDouble velocity_z;
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
  MwbDouble enable;
  MwbDouble reset;
};



#endif /* ON_SYSBLOCK_PRIVATE_H */

/********************************************************************************
** end of file
********************************************************************************/
