/********************************************************************************
 * Copyright (C) 2005-2026, Suzhou Tongyuan Software&Control Technology Co.,Ltd.
 * All rights reserved.
 * 版权所有 (C) 2005-2026， 苏州同元软控技术股份有限公司
 * 保留所有权利。
 *
 * 该文件由MWORKS内核代码生成器自动生成。
 *
 * 文件名称: MoSim_P2_LinearRobust_CFunction_Sysblock.c
 * 生成时间: 2026-07-17 09:21:58
 *
********************************************************************************/

#include "MoSim_P2_LinearRobust_CFunction_Sysblock.h"
#include "mwb_runtime.h"
#include "MoSim_P2_LinearRobust_CFunction_Sysblock_private.h"
#include "MoSim_P2_LinearRobust_CFunction_Sysblock_extern_include.h"

struct tion_sysblockExtU tion_sysblockGbIn;
struct tion_sysblockExtY ction_sysblockGbOut;
struct on_sysblockDw ion_sysblockGbDw;
static struct ction_sysblockTagEmd ion_sysblockStMd;
on_sysblockEmd*const ion_sysblockGbMd = &ion_sysblockStMd;

void Step(void)
{
  {
    void MosimLinearRobustStepScalar(const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, 
    const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, 
    const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, 
    const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* 
    , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* 
    , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* );
    MosimLinearRobustStepScalar(tion_sysblockGbIn.controller_id_in, tion_sysblockGbIn.dt_in, tion_sysblockGbIn.position_x_in, tion_sysblockGbIn.position_y_in, 
    tion_sysblockGbIn.position_z_in, tion_sysblockGbIn.velocity_x_in, tion_sysblockGbIn.velocity_y_in, tion_sysblockGbIn.velocity_z_in, 
tion_sysblockGbIn.reference_position_x_in, tion_sysblockGbIn.reference_position_y_in, tion_sysblockGbIn.reference_position_z_in, tion_sysblockGbIn.reference_velocity_x_in, 
tion_sysblockGbIn.reference_velocity_y_in, tion_sysblockGbIn.reference_velocity_z_in, tion_sysblockGbIn.reference_acceleration_x_in, 
tion_sysblockGbIn.reference_acceleration_y_in, tion_sysblockGbIn.reference_acceleration_z_in, tion_sysblockGbIn.reference_yaw_in, 
tion_sysblockGbIn.mass_kg_in, tion_sysblockGbIn.gravity_mps2_in, tion_sysblockGbIn.hover_percentage_in, tion_sysblockGbIn.max_tilt_rad_in, 
tion_sysblockGbIn.min_collective_thrust_n_in, tion_sysblockGbIn.max_collective_thrust_n_in, tion_sysblockGbIn.enable_in, tion_sysblockGbIn.reset_in, 
&(ction_sysblockGbOut.desired_attitude_w_out), &(ction_sysblockGbOut.desired_attitude_x_out), &(ction_sysblockGbOut.desired_attitude_y_out), 
&(ction_sysblockGbOut.desired_attitude_z_out), &(ction_sysblockGbOut.normalized_thrust_out), &(ction_sysblockGbOut.collective_thrust_n_out), 
&(ction_sysblockGbOut.desired_acceleration_x_out), &(ction_sysblockGbOut.desired_acceleration_y_out), &(ction_sysblockGbOut.desired_acceleration_z_out), 
&(ction_sysblockGbOut.estimated_position_x_out), &(ction_sysblockGbOut.estimated_position_y_out), &(ction_sysblockGbOut.estimated_position_z_out), 
&(ction_sysblockGbOut.estimated_velocity_x_out), &(ction_sysblockGbOut.estimated_velocity_y_out), &(ction_sysblockGbOut.estimated_velocity_z_out), 
&(ction_sysblockGbOut.adaptive_disturbance_x_out), &(ction_sysblockGbOut.adaptive_disturbance_y_out), &(ction_sysblockGbOut.adaptive_disturbance_z_out), 
&(ction_sysblockGbOut.storage_function_out), &(ction_sysblockGbOut.saturated_out), &(ction_sysblockGbOut.status_code_out));
  }
  ++ion_sysblockGbMd->m_timeTickCount;
}

void Init(void)
{
  ion_sysblockGbMd->m_stepSize = 0.01;
}



/********************************************************************************
** end of file
********************************************************************************/
