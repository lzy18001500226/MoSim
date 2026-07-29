/********************************************************************************
 * Copyright (C) 2005-2026, Suzhou Tongyuan Software&Control Technology Co.,Ltd.
 * All rights reserved.
 * 版权所有 (C) 2005-2026， 苏州同元软控技术股份有限公司
 * 保留所有权利。
 *
 * 该文件由MWORKS内核代码生成器自动生成。
 *
 * 文件名称: PX4CTRL_Core_CFunction_Sysblock.c
 * 生成时间: 2026-06-29 09:26:55
 *
********************************************************************************/

#include "PX4CTRL_Core_CFunction_Sysblock.h"
#include "mwb_runtime.h"
#include "PX4CTRL_Core_CFunction_Sysblock_private.h"
#include "PX4CTRL_Core_CFunction_Sysblock_extern_include.h"

struct lockExtU lockGbIn;
struct lockExtY blockGbOut;
struct ckDw ockGbDw;
static struct blockTagEmd ockStMd;
ckEmd*const ockGbMd = &ockStMd;

void Step(void)
{
  {
    void MosimPx4ctrlCoreCStepScalar(const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, 
    const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, 
    const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, 
    const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, 
    const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, 
    const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* 
    , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* 
    , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* );
    MosimPx4ctrlCoreCStepScalar(lockGbIn.dt_in, lockGbIn.position_x_in, lockGbIn.position_y_in, lockGbIn.position_z_in, lockGbIn.velocity_x_in, 
    lockGbIn.velocity_y_in, lockGbIn.velocity_z_in, lockGbIn.attitude_w_in, lockGbIn.attitude_x_in, lockGbIn.attitude_y_in, lockGbIn.attitude_z_in, 
lockGbIn.angular_velocity_x_in, lockGbIn.angular_velocity_y_in, lockGbIn.angular_velocity_z_in, lockGbIn.reference_position_x_in, 
lockGbIn.reference_position_y_in, lockGbIn.reference_position_z_in, lockGbIn.reference_velocity_x_in, lockGbIn.reference_velocity_y_in, 
lockGbIn.reference_velocity_z_in, lockGbIn.reference_acceleration_x_in, lockGbIn.reference_acceleration_y_in, lockGbIn.reference_acceleration_z_in, 
lockGbIn.reference_yaw_in, lockGbIn.reference_yaw_rate_in, lockGbIn.imu_attitude_w_in, lockGbIn.imu_attitude_x_in, lockGbIn.imu_attitude_y_in, 
lockGbIn.imu_attitude_z_in, lockGbIn.imu_angular_velocity_x_in, lockGbIn.imu_angular_velocity_y_in, lockGbIn.imu_angular_velocity_z_in, 
lockGbIn.enable_in, lockGbIn.reset_in, lockGbIn.kp_x_in, lockGbIn.kp_y_in, lockGbIn.kp_z_in, lockGbIn.kv_x_in, lockGbIn.kv_y_in, lockGbIn.kv_z_in, 
lockGbIn.mass_in, lockGbIn.gravity_in, lockGbIn.hover_percentage_in, &(blockGbOut.desired_attitude_w_out), &(blockGbOut.desired_attitude_x_out), 
&(blockGbOut.desired_attitude_y_out), &(blockGbOut.desired_attitude_z_out), &(blockGbOut.normalized_thrust_out), &(blockGbOut.collective_thrust_N_out), 
&(blockGbOut.position_error_x_out), &(blockGbOut.position_error_y_out), &(blockGbOut.position_error_z_out), &(blockGbOut.velocity_error_x_out), 
&(blockGbOut.velocity_error_y_out), &(blockGbOut.velocity_error_z_out), &(blockGbOut.desired_acceleration_x_out), &(blockGbOut.desired_acceleration_y_out), 
&(blockGbOut.desired_acceleration_z_out), &(blockGbOut.desired_force_N_x_out), &(blockGbOut.desired_force_N_y_out), &(blockGbOut.desired_force_N_z_out), 
&(blockGbOut.status_code_out));
  }
  ++ockGbMd->m_timeTickCount;
}

void Init(void)
{
  ockGbMd->m_stepSize = 0.01;
}



/********************************************************************************
** end of file
********************************************************************************/
