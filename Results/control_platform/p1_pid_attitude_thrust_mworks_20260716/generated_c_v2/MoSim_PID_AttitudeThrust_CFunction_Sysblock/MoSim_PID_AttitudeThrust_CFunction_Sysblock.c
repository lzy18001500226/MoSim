/********************************************************************************
 * Copyright (C) 2005-2026, Suzhou Tongyuan Software&Control Technology Co.,Ltd.
 * All rights reserved.
 * 版权所有 (C) 2005-2026， 苏州同元软控技术股份有限公司
 * 保留所有权利。
 *
 * 该文件由MWORKS内核代码生成器自动生成。
 *
 * 文件名称: MoSim_PID_AttitudeThrust_CFunction_Sysblock.c
 * 生成时间: 2026-07-16 15:58:49
 *
********************************************************************************/

#include "MoSim_PID_AttitudeThrust_CFunction_Sysblock.h"
#include "mwb_runtime.h"
#include "MoSim_PID_AttitudeThrust_CFunction_Sysblock_private.h"
#include "MoSim_PID_AttitudeThrust_CFunction_Sysblock_extern_include.h"

struct unction_sysblockExtU unction_sysblockGbIn;
struct unction_sysblockExtY function_sysblockGbOut;
struct ction_sysblockDw nction_sysblockGbDw;
static struct function_sysblockTagEmd nction_sysblockStMd;
ction_sysblockEmd*const nction_sysblockGbMd = &nction_sysblockStMd;

void Step(void)
{
  {
    void MosimPidAttitudeThrustStepScalar(const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const
    MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble,
    const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble,
    const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble,
    const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble,
    const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble*
    , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble*
    , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* );
    MosimPidAttitudeThrustStepScalar(unction_sysblockGbIn.algorithm_id_in, unction_sysblockGbIn.dt_in, unction_sysblockGbIn.position_x_in,
    unction_sysblockGbIn.position_y_in, unction_sysblockGbIn.position_z_in, unction_sysblockGbIn.velocity_x_in, unction_sysblockGbIn.velocity_y_in,
unction_sysblockGbIn.velocity_z_in, unction_sysblockGbIn.attitude_w_in, unction_sysblockGbIn.attitude_x_in, unction_sysblockGbIn.attitude_y_in,
unction_sysblockGbIn.attitude_z_in, unction_sysblockGbIn.angular_velocity_x_in, unction_sysblockGbIn.angular_velocity_y_in, unction_sysblockGbIn.angular_velocity_z_in,
unction_sysblockGbIn.reference_position_x_in, unction_sysblockGbIn.reference_position_y_in, unction_sysblockGbIn.reference_position_z_in,
unction_sysblockGbIn.reference_velocity_x_in, unction_sysblockGbIn.reference_velocity_y_in, unction_sysblockGbIn.reference_velocity_z_in,
unction_sysblockGbIn.reference_acceleration_x_in, unction_sysblockGbIn.reference_acceleration_y_in, unction_sysblockGbIn.reference_acceleration_z_in,
unction_sysblockGbIn.reference_yaw_in, unction_sysblockGbIn.mass_kg_in, unction_sysblockGbIn.gravity_mps2_in, unction_sysblockGbIn.max_tilt_rad_in,
unction_sysblockGbIn.min_collective_thrust_n_in, unction_sysblockGbIn.max_collective_thrust_n_in, unction_sysblockGbIn.schedule_x_in,
unction_sysblockGbIn.schedule_y_in, unction_sysblockGbIn.schedule_z_in, unction_sysblockGbIn.fuzzy_error_x_in, unction_sysblockGbIn.fuzzy_error_y_in,
unction_sysblockGbIn.fuzzy_error_z_in, unction_sysblockGbIn.neural_residual_x_in, unction_sysblockGbIn.neural_residual_y_in, unction_sysblockGbIn.neural_residual_z_in,
unction_sysblockGbIn.enable_in, unction_sysblockGbIn.reset_in, &(function_sysblockGbOut.desired_attitude_w_out), &(function_sysblockGbOut.desired_attitude_x_out),
&(function_sysblockGbOut.desired_attitude_y_out), &(function_sysblockGbOut.desired_attitude_z_out), &(function_sysblockGbOut.desired_collective_thrust_n_out),
&(function_sysblockGbOut.desired_acceleration_x_out), &(function_sysblockGbOut.desired_acceleration_y_out), &(function_sysblockGbOut.desired_acceleration_z_out),
&(function_sysblockGbOut.position_error_x_out), &(function_sysblockGbOut.position_error_y_out), &(function_sysblockGbOut.position_error_z_out),
&(function_sysblockGbOut.velocity_error_x_out), &(function_sysblockGbOut.velocity_error_y_out), &(function_sysblockGbOut.velocity_error_z_out),
&(function_sysblockGbOut.scheduled_gain_x_out), &(function_sysblockGbOut.scheduled_gain_y_out), &(function_sysblockGbOut.scheduled_gain_z_out),
&(function_sysblockGbOut.saturated_out), &(function_sysblockGbOut.status_code_out), &(function_sysblockGbOut.algorithm_id_out_out));

  }
  ++nction_sysblockGbMd->m_timeTickCount;
}

void Init(void)
{
  nction_sysblockGbMd->m_stepSize = 0.01;
}



/********************************************************************************
** end of file
********************************************************************************/
