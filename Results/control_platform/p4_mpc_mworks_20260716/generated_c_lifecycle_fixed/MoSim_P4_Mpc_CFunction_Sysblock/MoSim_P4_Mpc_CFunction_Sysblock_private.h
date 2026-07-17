/********************************************************************************
 * Copyright (C) 2005-2026, Suzhou Tongyuan Software&Control Technology Co.,Ltd.
 * All rights reserved.
 * 版权所有 (C) 2005-2026， 苏州同元软控技术股份有限公司
 * 保留所有权利。
 *
 * 该文件由MWORKS内核代码生成器自动生成。
 *
 * 文件名称: MoSim_P4_Mpc_CFunction_Sysblock_private.h
 * 生成时间: 2026-07-16 23:05:45
 *
********************************************************************************/

#ifndef N_SYSBLOCK_PRIVATE_H
#define N_SYSBLOCK_PRIVATE_H

#include "MoSim_P4_Mpc_CFunction_Sysblock.h"

struct lockExtU
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
  MwbDouble mass_kg_in;
  MwbDouble gravity_mps2_in;
  MwbDouble hover_percentage_in;
  MwbDouble max_tilt_rad_in;
  MwbDouble min_collective_thrust_n_in;
  MwbDouble max_collective_thrust_n_in;
  MwbDouble enable_in;
  MwbDouble reset_in;
};

struct lockExtY
{
  MwbDouble desired_attitude_w_out;
  MwbDouble desired_attitude_x_out;
  MwbDouble desired_attitude_y_out;
  MwbDouble desired_attitude_z_out;
  MwbDouble normalized_thrust_out;
  MwbDouble collective_thrust_n_out;
  MwbDouble desired_acceleration_x_out;
  MwbDouble desired_acceleration_y_out;
  MwbDouble desired_acceleration_z_out;
  MwbDouble unconstrained_acceleration_x_out;
  MwbDouble unconstrained_acceleration_y_out;
  MwbDouble unconstrained_acceleration_z_out;
  MwbDouble auxiliary_x_out;
  MwbDouble auxiliary_y_out;
  MwbDouble auxiliary_z_out;
  MwbDouble solver_cost_out;
  MwbDouble solver_iterations_out;
  MwbDouble saturated_out;
  MwbDouble status_code_out;
};

struct ckDw
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
  MwbDouble mass_kg;
  MwbDouble gravity_mps2;
  MwbDouble hover_percentage;
  MwbDouble max_tilt_rad;
  MwbDouble min_collective_thrust_n;
  MwbDouble max_collective_thrust_n;
  MwbDouble enable;
  MwbDouble reset;
};



#endif /* N_SYSBLOCK_PRIVATE_H */

/********************************************************************************
** end of file
********************************************************************************/
