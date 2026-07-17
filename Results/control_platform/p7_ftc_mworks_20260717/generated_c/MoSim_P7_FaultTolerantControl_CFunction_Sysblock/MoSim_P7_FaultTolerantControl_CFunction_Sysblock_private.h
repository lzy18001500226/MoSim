/********************************************************************************
 * Copyright (C) 2005-2026, Suzhou Tongyuan Software&Control Technology Co.,Ltd.
 * All rights reserved.
 * 版权所有 (C) 2005-2026， 苏州同元软控技术股份有限公司
 * 保留所有权利。
 *
 * 该文件由MWORKS内核代码生成器自动生成。
 *
 * 文件名称: MoSim_P7_FaultTolerantControl_CFunction_Sysblock_private.h
 * 生成时间: 2026-07-17 04:13:56
 *
********************************************************************************/

#ifndef TCONTROL_CFUNCTION_SYSBLOCK_PRIVATE_H
#define TCONTROL_CFUNCTION_SYSBLOCK_PRIVATE_H

#include "MoSim_P7_FaultTolerantControl_CFunction_Sysblock.h"

struct ol_cfunction_sysblockExtU
{
  MwbDouble mode_id_in;
  MwbDouble dt_in;
  MwbDouble desired_thrust_in;
  MwbDouble desired_roll_in;
  MwbDouble desired_pitch_in;
  MwbDouble desired_yaw_in;
  MwbDouble response_1_in;
  MwbDouble response_2_in;
  MwbDouble response_3_in;
  MwbDouble response_4_in;
  MwbDouble airborne_in;
  MwbDouble altitude_in;
  MwbDouble enable_in;
  MwbDouble reset_in;
};

struct ol_cfunction_sysblockExtY
{
  MwbDouble motor_command_1_out;
  MwbDouble motor_command_2_out;
  MwbDouble motor_command_3_out;
  MwbDouble motor_command_4_out;
  MwbDouble eta_hat_1_out;
  MwbDouble eta_hat_2_out;
  MwbDouble eta_hat_3_out;
  MwbDouble eta_hat_4_out;
  MwbDouble achieved_thrust_out;
  MwbDouble achieved_roll_out;
  MwbDouble achieved_pitch_out;
  MwbDouble achieved_yaw_out;
  MwbDouble residual_norm_out;
  MwbDouble isolated_mask_out;
  MwbDouble fault_count_out;
  MwbDouble action_out;
  MwbDouble allocation_saturated_out;
  MwbDouble status_code_out;
};

struct acfunction_sysblockDw
{
  MwbDouble mode_id;
  MwbDouble dt;
  MwbDouble desired_thrust;
  MwbDouble desired_roll;
  MwbDouble desired_pitch;
  MwbDouble desired_yaw;
  MwbDouble response_1;
  MwbDouble response_2;
  MwbDouble response_3;
  MwbDouble response_4;
  MwbDouble airborne;
  MwbDouble altitude;
  MwbDouble enable;
  MwbDouble reset;
};



#endif /* TCONTROL_CFUNCTION_SYSBLOCK_PRIVATE_H */

/********************************************************************************
** end of file
********************************************************************************/
