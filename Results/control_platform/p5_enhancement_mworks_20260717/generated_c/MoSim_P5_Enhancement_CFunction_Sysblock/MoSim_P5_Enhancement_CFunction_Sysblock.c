/********************************************************************************
 * Copyright (C) 2005-2026, Suzhou Tongyuan Software&Control Technology Co.,Ltd.
 * All rights reserved.
 * 版权所有 (C) 2005-2026， 苏州同元软控技术股份有限公司
 * 保留所有权利。
 *
 * 该文件由MWORKS内核代码生成器自动生成。
 *
 * 文件名称: MoSim_P5_Enhancement_CFunction_Sysblock.c
 * 生成时间: 2026-07-17 09:21:59
 *
********************************************************************************/

#include "MoSim_P5_Enhancement_CFunction_Sysblock.h"
#include "mwb_runtime.h"
#include "MoSim_P5_Enhancement_CFunction_Sysblock_private.h"
#include "MoSim_P5_Enhancement_CFunction_Sysblock_extern_include.h"

struct ion_sysblockExtU ion_sysblockGbIn;
struct ion_sysblockExtY tion_sysblockGbOut;
struct n_sysblockDw on_sysblockGbDw;
static struct tion_sysblockTagEmd on_sysblockStMd;
n_sysblockEmd*const on_sysblockGbMd = &on_sysblockStMd;

void Step(void)
{
  {
    void MosimEnhancementStepScalar(const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, 
    const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, 
    const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, 
    const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, 
    const MwbDouble, MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* 
    , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* 
    , MwbDouble* , MwbDouble* );
    MosimEnhancementStepScalar(ion_sysblockGbIn.controller_id_in, ion_sysblockGbIn.dt_in, ion_sysblockGbIn.position_x_in, ion_sysblockGbIn.position_y_in, 
    ion_sysblockGbIn.position_z_in, ion_sysblockGbIn.velocity_x_in, ion_sysblockGbIn.velocity_y_in, ion_sysblockGbIn.velocity_z_in, ion_sysblockGbIn.measured_acceleration_x_in, 
ion_sysblockGbIn.measured_acceleration_y_in, ion_sysblockGbIn.measured_acceleration_z_in, ion_sysblockGbIn.reference_position_x_in, 
ion_sysblockGbIn.reference_position_y_in, ion_sysblockGbIn.reference_position_z_in, ion_sysblockGbIn.reference_velocity_x_in, ion_sysblockGbIn.reference_velocity_y_in, 
ion_sysblockGbIn.reference_velocity_z_in, ion_sysblockGbIn.reference_acceleration_x_in, ion_sysblockGbIn.reference_acceleration_y_in, 
ion_sysblockGbIn.reference_acceleration_z_in, ion_sysblockGbIn.reference_yaw_in, ion_sysblockGbIn.trajectory_phase_bin_in, ion_sysblockGbIn.repeat_complete_in, 
ion_sysblockGbIn.mass_kg_in, ion_sysblockGbIn.gravity_mps2_in, ion_sysblockGbIn.hover_percentage_in, ion_sysblockGbIn.max_tilt_rad_in, 
ion_sysblockGbIn.min_collective_thrust_n_in, ion_sysblockGbIn.max_collective_thrust_n_in, ion_sysblockGbIn.enable_in, ion_sysblockGbIn.reset_in, 
&(tion_sysblockGbOut.desired_attitude_w_out), &(tion_sysblockGbOut.desired_attitude_x_out), &(tion_sysblockGbOut.desired_attitude_y_out), 
&(tion_sysblockGbOut.desired_attitude_z_out), &(tion_sysblockGbOut.normalized_thrust_out), &(tion_sysblockGbOut.collective_thrust_n_out), 
&(tion_sysblockGbOut.desired_acceleration_x_out), &(tion_sysblockGbOut.desired_acceleration_y_out), &(tion_sysblockGbOut.desired_acceleration_z_out), 
&(tion_sysblockGbOut.nominal_acceleration_x_out), &(tion_sysblockGbOut.nominal_acceleration_y_out), &(tion_sysblockGbOut.nominal_acceleration_z_out), 
&(tion_sysblockGbOut.compensation_x_out), &(tion_sysblockGbOut.compensation_y_out), &(tion_sysblockGbOut.compensation_z_out), &(tion_sysblockGbOut.observer_state_x_out), 
&(tion_sysblockGbOut.observer_state_y_out), &(tion_sysblockGbOut.observer_state_z_out), &(tion_sysblockGbOut.effective_gain_scale_out), 
&(tion_sysblockGbOut.saturated_out), &(tion_sysblockGbOut.status_code_out));
  }
  ++on_sysblockGbMd->m_timeTickCount;
}

void Init(void)
{
  on_sysblockGbMd->m_stepSize = 0.01;
}



/********************************************************************************
** end of file
********************************************************************************/
