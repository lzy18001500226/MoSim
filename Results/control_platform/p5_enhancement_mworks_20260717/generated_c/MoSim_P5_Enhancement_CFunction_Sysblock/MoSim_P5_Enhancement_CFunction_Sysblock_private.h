/********************************************************************************
 * Copyright (C) 2005-2026, Suzhou Tongyuan Software&Control Technology Co.,Ltd.
 * All rights reserved.
 * 版权所有 (C) 2005-2026， 苏州同元软控技术股份有限公司
 * 保留所有权利。
 *
 * 该文件由MWORKS内核代码生成器自动生成。
 *
 * 文件名称: MoSim_P5_Enhancement_CFunction_Sysblock_private.h
 * 生成时间: 2026-07-17 09:21:59
 *
********************************************************************************/

#ifndef CFUNCTION_SYSBLOCK_PRIVATE_H
#define CFUNCTION_SYSBLOCK_PRIVATE_H

#include "MoSim_P5_Enhancement_CFunction_Sysblock.h"

struct ion_sysblockExtU
{
  MwbDouble controller_id_in;
  MwbDouble dt_in;
  MwbDouble position_x_in;
  MwbDouble position_y_in;
  MwbDouble position_z_in;
  MwbDouble velocity_x_in;
  MwbDouble velocity_y_in;
  MwbDouble velocity_z_in;
  MwbDouble measured_acceleration_x_in;
  MwbDouble measured_acceleration_y_in;
  MwbDouble measured_acceleration_z_in;
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
  MwbDouble trajectory_phase_bin_in;
  MwbDouble repeat_complete_in;
  MwbDouble mass_kg_in;
  MwbDouble gravity_mps2_in;
  MwbDouble hover_percentage_in;
  MwbDouble max_tilt_rad_in;
  MwbDouble min_collective_thrust_n_in;
  MwbDouble max_collective_thrust_n_in;
  MwbDouble enable_in;
  MwbDouble reset_in;
};

struct ion_sysblockExtY
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
  MwbDouble nominal_acceleration_x_out;
  MwbDouble nominal_acceleration_y_out;
  MwbDouble nominal_acceleration_z_out;
  MwbDouble compensation_x_out;
  MwbDouble compensation_y_out;
  MwbDouble compensation_z_out;
  MwbDouble observer_state_x_out;
  MwbDouble observer_state_y_out;
  MwbDouble observer_state_z_out;
  MwbDouble effective_gain_scale_out;
  MwbDouble saturated_out;
  MwbDouble status_code_out;
};

struct n_sysblockDw
{
  MwbDouble controller_id;
  MwbDouble dt;
  MwbDouble position_x;
  MwbDouble position_y;
  MwbDouble position_z;
  MwbDouble velocity_x;
  MwbDouble velocity_y;
  MwbDouble velocity_z;
  MwbDouble measured_acceleration_x;
  MwbDouble measured_acceleration_y;
  MwbDouble measured_acceleration_z;
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
  MwbDouble trajectory_phase_bin;
  MwbDouble repeat_complete;
  MwbDouble mass_kg;
  MwbDouble gravity_mps2;
  MwbDouble hover_percentage;
  MwbDouble max_tilt_rad;
  MwbDouble min_collective_thrust_n;
  MwbDouble max_collective_thrust_n;
  MwbDouble enable;
  MwbDouble reset;
};



#endif /* CFUNCTION_SYSBLOCK_PRIVATE_H */

/********************************************************************************
** end of file
********************************************************************************/
