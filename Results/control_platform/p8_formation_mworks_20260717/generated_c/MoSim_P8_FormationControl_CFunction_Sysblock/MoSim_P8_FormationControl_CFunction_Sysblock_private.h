/********************************************************************************
 * Copyright (C) 2005-2026, Suzhou Tongyuan Software&Control Technology Co.,Ltd.
 * All rights reserved.
 * 版权所有 (C) 2005-2026， 苏州同元软控技术股份有限公司
 * 保留所有权利。
 *
 * 该文件由MWORKS内核代码生成器自动生成。
 *
 * 文件名称: MoSim_P8_FormationControl_CFunction_Sysblock_private.h
 * 生成时间: 2026-07-17 07:15:29
 *
********************************************************************************/

#ifndef TROL_CFUNCTION_SYSBLOCK_PRIVATE_H
#define TROL_CFUNCTION_SYSBLOCK_PRIVATE_H

#include "MoSim_P8_FormationControl_CFunction_Sysblock.h"

struct function_sysblockExtU
{
  MwbDouble mode_id_in;
  MwbDouble dt_in;
  MwbDouble leader_x_in;
  MwbDouble leader_y_in;
  MwbDouble leader_z_in;
  MwbDouble leader_vx_in;
  MwbDouble leader_vy_in;
  MwbDouble leader_vz_in;
  MwbDouble leader_yaw_in;
  MwbDouble position_1_x_in;
  MwbDouble position_1_y_in;
  MwbDouble position_1_z_in;
  MwbDouble position_2_x_in;
  MwbDouble position_2_y_in;
  MwbDouble position_2_z_in;
  MwbDouble position_3_x_in;
  MwbDouble position_3_y_in;
  MwbDouble position_3_z_in;
  MwbDouble velocity_1_x_in;
  MwbDouble velocity_1_y_in;
  MwbDouble velocity_1_z_in;
  MwbDouble velocity_2_x_in;
  MwbDouble velocity_2_y_in;
  MwbDouble velocity_2_z_in;
  MwbDouble velocity_3_x_in;
  MwbDouble velocity_3_y_in;
  MwbDouble velocity_3_z_in;
  MwbDouble healthy_1_in;
  MwbDouble healthy_2_in;
  MwbDouble healthy_3_in;
  MwbDouble reconfigure_in;
  MwbDouble enable_in;
  MwbDouble reset_in;
};

struct function_sysblockExtY
{
  MwbDouble desired_position_1_x_out;
  MwbDouble desired_position_1_y_out;
  MwbDouble desired_position_1_z_out;
  MwbDouble desired_position_2_x_out;
  MwbDouble desired_position_2_y_out;
  MwbDouble desired_position_2_z_out;
  MwbDouble desired_position_3_x_out;
  MwbDouble desired_position_3_y_out;
  MwbDouble desired_position_3_z_out;
  MwbDouble desired_velocity_1_x_out;
  MwbDouble desired_velocity_1_y_out;
  MwbDouble desired_velocity_1_z_out;
  MwbDouble desired_velocity_2_x_out;
  MwbDouble desired_velocity_2_y_out;
  MwbDouble desired_velocity_2_z_out;
  MwbDouble desired_velocity_3_x_out;
  MwbDouble desired_velocity_3_y_out;
  MwbDouble desired_velocity_3_z_out;
  MwbDouble minimum_pair_distance_out;
  MwbDouble formation_rmse_out;
  MwbDouble active_agents_out;
  MwbDouble failed_mask_out;
  MwbDouble safety_corrections_out;
  MwbDouble status_code_out;
};

struct nction_sysblockDw
{
  MwbDouble mode_id;
  MwbDouble dt;
  MwbDouble leader_x;
  MwbDouble leader_y;
  MwbDouble leader_z;
  MwbDouble leader_vx;
  MwbDouble leader_vy;
  MwbDouble leader_vz;
  MwbDouble leader_yaw;
  MwbDouble position_1_x;
  MwbDouble position_1_y;
  MwbDouble position_1_z;
  MwbDouble position_2_x;
  MwbDouble position_2_y;
  MwbDouble position_2_z;
  MwbDouble position_3_x;
  MwbDouble position_3_y;
  MwbDouble position_3_z;
  MwbDouble velocity_1_x;
  MwbDouble velocity_1_y;
  MwbDouble velocity_1_z;
  MwbDouble velocity_2_x;
  MwbDouble velocity_2_y;
  MwbDouble velocity_2_z;
  MwbDouble velocity_3_x;
  MwbDouble velocity_3_y;
  MwbDouble velocity_3_z;
  MwbDouble healthy_1;
  MwbDouble healthy_2;
  MwbDouble healthy_3;
  MwbDouble reconfigure;
  MwbDouble enable;
  MwbDouble reset;
};



#endif /* TROL_CFUNCTION_SYSBLOCK_PRIVATE_H */

/********************************************************************************
** end of file
********************************************************************************/
