/********************************************************************************
 * Copyright (C) 2005-2026, Suzhou Tongyuan Software&Control Technology Co.,Ltd.
 * All rights reserved.
 * 版权所有 (C) 2005-2026， 苏州同元软控技术股份有限公司
 * 保留所有权利。
 *
 * 该文件由MWORKS内核代码生成器自动生成。
 *
 * 文件名称: MoSim_Classic_CFunction_Sysblock.c
 * 生成时间: 2026-07-17 20:28:29
 *
********************************************************************************/

#include "MoSim_Classic_CFunction_Sysblock.h"
#include "mwb_runtime.h"
#include "MoSim_Classic_CFunction_Sysblock_private.h"
#include "MoSim_Classic_CFunction_Sysblock_extern_include.h"

struct blockExtU blockGbIn;
struct blockExtY sblockGbOut;
struct ockDw lockGbDw;
static struct sblockTagEmd lockStMd;
ockEmd*const lockGbMd = &lockStMd;

void Step(void)
{
  {
    void MosimClassicStepScalar(const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble,
    const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble,
    const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, MwbDouble* , MwbDouble* , MwbDouble*
    , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble*
    , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble*
    , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble*
    , MwbDouble* , MwbDouble* );
    MosimClassicStepScalar(blockGbIn.controller_id_in, blockGbIn.dt_in, blockGbIn.position_x_in, blockGbIn.position_y_in, blockGbIn.position_z_in,
    blockGbIn.velocity_x_in, blockGbIn.velocity_y_in, blockGbIn.velocity_z_in, blockGbIn.reference_position_x_in, blockGbIn.reference_position_y_in,
blockGbIn.reference_position_z_in, blockGbIn.reference_velocity_x_in, blockGbIn.reference_velocity_y_in, blockGbIn.reference_velocity_z_in,
blockGbIn.reference_acceleration_x_in, blockGbIn.reference_acceleration_y_in, blockGbIn.reference_acceleration_z_in, blockGbIn.reference_yaw_in,
blockGbIn.enable_in, blockGbIn.reset_in, &(sblockGbOut.desired_acceleration_x_out), &(sblockGbOut.desired_acceleration_y_out), &(sblockGbOut.desired_acceleration_z_out),
&(sblockGbOut.desired_attitude_w_out), &(sblockGbOut.desired_attitude_x_out), &(sblockGbOut.desired_attitude_y_out), &(sblockGbOut.desired_attitude_z_out),
&(sblockGbOut.observer_position_x_out), &(sblockGbOut.observer_position_y_out), &(sblockGbOut.observer_position_z_out), &(sblockGbOut.observer_velocity_x_out),
&(sblockGbOut.observer_velocity_y_out), &(sblockGbOut.observer_velocity_z_out), &(sblockGbOut.reference_model_position_x_out), &(sblockGbOut.reference_model_position_y_out),
&(sblockGbOut.reference_model_position_z_out), &(sblockGbOut.reference_model_velocity_x_out), &(sblockGbOut.reference_model_velocity_y_out),
&(sblockGbOut.reference_model_velocity_z_out), &(sblockGbOut.adaptive_position_delta_x_out), &(sblockGbOut.adaptive_position_delta_y_out),
&(sblockGbOut.adaptive_position_delta_z_out), &(sblockGbOut.adaptive_velocity_delta_x_out), &(sblockGbOut.adaptive_velocity_delta_y_out),
&(sblockGbOut.adaptive_velocity_delta_z_out), &(sblockGbOut.fractional_integral_x_out), &(sblockGbOut.fractional_integral_y_out),
&(sblockGbOut.fractional_integral_z_out), &(sblockGbOut.fractional_derivative_x_out), &(sblockGbOut.fractional_derivative_y_out),
&(sblockGbOut.fractional_derivative_z_out), &(sblockGbOut.normalized_thrust_out), &(sblockGbOut.collective_thrust_n_out), &(sblockGbOut.saturated_out),
&(sblockGbOut.status_code_out));
  }
  ++lockGbMd->m_timeTickCount;
}

void Init(void)
{
  lockGbMd->m_stepSize = 0.01;
}



/********************************************************************************
** end of file
********************************************************************************/
