/********************************************************************************
 * Copyright (C) 2005-2026, Suzhou Tongyuan Software&Control Technology Co.,Ltd.
 * All rights reserved.
 * 版权所有 (C) 2005-2026， 苏州同元软控技术股份有限公司
 * 保留所有权利。
 *
 * 该文件由MWORKS内核代码生成器自动生成。
 *
 * 文件名称: MoSim_P7_FaultTolerantControl_CFunction_Sysblock.c
 * 生成时间: 2026-07-17 04:13:56
 *
********************************************************************************/

#include "MoSim_P7_FaultTolerantControl_CFunction_Sysblock.h"
#include "mwb_runtime.h"
#include "MoSim_P7_FaultTolerantControl_CFunction_Sysblock_private.h"
#include "MoSim_P7_FaultTolerantControl_CFunction_Sysblock_extern_include.h"

struct ol_cfunction_sysblockExtU ol_cfunction_sysblockGbIn;
struct ol_cfunction_sysblockExtY rol_cfunction_sysblockGbOut;
struct acfunction_sysblockDw l_cfunction_sysblockGbDw;
static struct rol_cfunction_sysblockTagEmd l_cfunction_sysblockStMd;
acfunction_sysblockEmd*const l_cfunction_sysblockGbMd = &l_cfunction_sysblockStMd;

void Step(void)
{
  {
    void MosimFaultTolerantControlStepScalar(const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, 
    const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, 
    const MwbDouble, MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* 
    , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* );
    MosimFaultTolerantControlStepScalar(ol_cfunction_sysblockGbIn.mode_id_in, ol_cfunction_sysblockGbIn.dt_in, ol_cfunction_sysblockGbIn.desired_thrust_in, 
    ol_cfunction_sysblockGbIn.desired_roll_in, ol_cfunction_sysblockGbIn.desired_pitch_in, ol_cfunction_sysblockGbIn.desired_yaw_in, ol_cfunction_sysblockGbIn.response_1_in, 
ol_cfunction_sysblockGbIn.response_2_in, ol_cfunction_sysblockGbIn.response_3_in, ol_cfunction_sysblockGbIn.response_4_in, ol_cfunction_sysblockGbIn.airborne_in, 
ol_cfunction_sysblockGbIn.altitude_in, ol_cfunction_sysblockGbIn.enable_in, ol_cfunction_sysblockGbIn.reset_in, &(rol_cfunction_sysblockGbOut.motor_command_1_out), 
&(rol_cfunction_sysblockGbOut.motor_command_2_out), &(rol_cfunction_sysblockGbOut.motor_command_3_out), &(rol_cfunction_sysblockGbOut.motor_command_4_out), 
&(rol_cfunction_sysblockGbOut.eta_hat_1_out), &(rol_cfunction_sysblockGbOut.eta_hat_2_out), &(rol_cfunction_sysblockGbOut.eta_hat_3_out), 
&(rol_cfunction_sysblockGbOut.eta_hat_4_out), &(rol_cfunction_sysblockGbOut.achieved_thrust_out), &(rol_cfunction_sysblockGbOut.achieved_roll_out), 
&(rol_cfunction_sysblockGbOut.achieved_pitch_out), &(rol_cfunction_sysblockGbOut.achieved_yaw_out), &(rol_cfunction_sysblockGbOut.residual_norm_out), 
&(rol_cfunction_sysblockGbOut.isolated_mask_out), &(rol_cfunction_sysblockGbOut.fault_count_out), &(rol_cfunction_sysblockGbOut.action_out), 
&(rol_cfunction_sysblockGbOut.allocation_saturated_out), &(rol_cfunction_sysblockGbOut.status_code_out));
  }
  ++l_cfunction_sysblockGbMd->m_timeTickCount;
}

void Init(void)
{
  l_cfunction_sysblockGbMd->m_stepSize = 0.01;
}



/********************************************************************************
** end of file
********************************************************************************/
