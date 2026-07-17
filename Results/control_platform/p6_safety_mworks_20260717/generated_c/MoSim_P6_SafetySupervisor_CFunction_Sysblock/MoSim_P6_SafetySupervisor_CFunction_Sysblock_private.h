/********************************************************************************
 * Copyright (C) 2005-2026, Suzhou Tongyuan Software&Control Technology Co.,Ltd.
 * All rights reserved.
 * 版权所有 (C) 2005-2026， 苏州同元软控技术股份有限公司
 * 保留所有权利。
 *
 * 该文件由MWORKS内核代码生成器自动生成。
 *
 * 文件名称: MoSim_P6_SafetySupervisor_CFunction_Sysblock_private.h
 * 生成时间: 2026-07-17 03:12:19
 *
********************************************************************************/

#ifndef ISOR_CFUNCTION_SYSBLOCK_PRIVATE_H
#define ISOR_CFUNCTION_SYSBLOCK_PRIVATE_H

#include "MoSim_P6_SafetySupervisor_CFunction_Sysblock.h"

struct function_sysblockExtU
{
  MwbDouble mode_id_in;
  MwbDouble dt_in;
  MwbDouble position_x_in;
  MwbDouble position_y_in;
  MwbDouble position_z_in;
  MwbDouble velocity_x_in;
  MwbDouble velocity_y_in;
  MwbDouble velocity_z_in;
  MwbDouble candidate_acceleration_x_in;
  MwbDouble candidate_acceleration_y_in;
  MwbDouble candidate_acceleration_z_in;
  MwbDouble candidate_thrust_in;
  MwbDouble candidate_tilt_rad_in;
  MwbDouble reference_position_x_in;
  MwbDouble reference_position_y_in;
  MwbDouble reference_position_z_in;
  MwbDouble home_position_x_in;
  MwbDouble home_position_y_in;
  MwbDouble home_position_z_in;
  MwbDouble obstacle_distance_in;
  MwbDouble command_age_s_in;
  MwbDouble state_valid_in;
  MwbDouble offboard_valid_in;
  MwbDouble emergency_request_in;
  MwbDouble return_request_in;
  MwbDouble land_request_in;
  MwbDouble enable_in;
  MwbDouble reset_in;
};

struct function_sysblockExtY
{
  MwbDouble safe_acceleration_x_out;
  MwbDouble safe_acceleration_y_out;
  MwbDouble safe_acceleration_z_out;
  MwbDouble safe_thrust_out;
  MwbDouble safe_reference_x_out;
  MwbDouble safe_reference_y_out;
  MwbDouble safe_reference_z_out;
  MwbDouble action_out;
  MwbDouble state_out;
  MwbDouble active_constraints_out;
  MwbDouble modified_out;
  MwbDouble status_code_out;
};

struct nction_sysblockDw
{
  MwbDouble mode_id;
  MwbDouble dt;
  MwbDouble position_x;
  MwbDouble position_y;
  MwbDouble position_z;
  MwbDouble velocity_x;
  MwbDouble velocity_y;
  MwbDouble velocity_z;
  MwbDouble candidate_acceleration_x;
  MwbDouble candidate_acceleration_y;
  MwbDouble candidate_acceleration_z;
  MwbDouble candidate_thrust;
  MwbDouble candidate_tilt_rad;
  MwbDouble reference_position_x;
  MwbDouble reference_position_y;
  MwbDouble reference_position_z;
  MwbDouble home_position_x;
  MwbDouble home_position_y;
  MwbDouble home_position_z;
  MwbDouble obstacle_distance;
  MwbDouble command_age_s;
  MwbDouble state_valid;
  MwbDouble offboard_valid;
  MwbDouble emergency_request;
  MwbDouble return_request;
  MwbDouble land_request;
  MwbDouble enable;
  MwbDouble reset;
};



#endif /* ISOR_CFUNCTION_SYSBLOCK_PRIVATE_H */

/********************************************************************************
** end of file
********************************************************************************/
