/********************************************************************************
 * Copyright (C) 2005-2026, Suzhou Tongyuan Software&Control Technology Co.,Ltd.
 * All rights reserved.
 * 版权所有 (C) 2005-2026， 苏州同元软控技术股份有限公司
 * 保留所有权利。
 *
 * 该文件由MWORKS内核代码生成器自动生成。
 *
 * 文件名称: MoSim_P4_Mpc_CFunction_Sysblock.c
 * 生成时间: 2026-07-16 23:05:45
 *
********************************************************************************/

#include "MoSim_P4_Mpc_CFunction_Sysblock.h"
#include "mwb_runtime.h"
#include "MoSim_P4_Mpc_CFunction_Sysblock_private.h"
#include "MoSim_P4_Mpc_CFunction_Sysblock_extern_include.h"

struct lockExtU lockGbIn;
struct lockExtY blockGbOut;
struct ckDw ockGbDw;
static struct blockTagEmd ockStMd;
ckEmd*const ockGbMd = &ockStMd;

void Step(void)
{
  {
    void MosimMpcStepScalar(const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, 
    const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, 
    const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, 
    const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* 
    , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* 
    , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* );
    MosimMpcStepScalar(lockGbIn.controller_id_in, lockGbIn.dt_in, lockGbIn.position_x_in, lockGbIn.position_y_in, lockGbIn.position_z_in, 
    lockGbIn.velocity_x_in, lockGbIn.velocity_y_in, lockGbIn.velocity_z_in, lockGbIn.reference_position_x_in, lockGbIn.reference_position_y_in, 
lockGbIn.reference_position_z_in, lockGbIn.reference_velocity_x_in, lockGbIn.reference_velocity_y_in, lockGbIn.reference_velocity_z_in, 
lockGbIn.reference_acceleration_x_in, lockGbIn.reference_acceleration_y_in, lockGbIn.reference_acceleration_z_in, lockGbIn.reference_yaw_in, 
lockGbIn.mass_kg_in, lockGbIn.gravity_mps2_in, lockGbIn.hover_percentage_in, lockGbIn.max_tilt_rad_in, lockGbIn.min_collective_thrust_n_in, 
lockGbIn.max_collective_thrust_n_in, lockGbIn.enable_in, lockGbIn.reset_in, &(blockGbOut.desired_attitude_w_out), &(blockGbOut.desired_attitude_x_out), 
&(blockGbOut.desired_attitude_y_out), &(blockGbOut.desired_attitude_z_out), &(blockGbOut.normalized_thrust_out), &(blockGbOut.collective_thrust_n_out), 
&(blockGbOut.desired_acceleration_x_out), &(blockGbOut.desired_acceleration_y_out), &(blockGbOut.desired_acceleration_z_out), &(blockGbOut.unconstrained_acceleration_x_out), 
&(blockGbOut.unconstrained_acceleration_y_out), &(blockGbOut.unconstrained_acceleration_z_out), &(blockGbOut.auxiliary_x_out), &(blockGbOut.auxiliary_y_out), 
&(blockGbOut.auxiliary_z_out), &(blockGbOut.solver_cost_out), &(blockGbOut.solver_iterations_out), &(blockGbOut.saturated_out), &(blockGbOut.status_code_out));

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
