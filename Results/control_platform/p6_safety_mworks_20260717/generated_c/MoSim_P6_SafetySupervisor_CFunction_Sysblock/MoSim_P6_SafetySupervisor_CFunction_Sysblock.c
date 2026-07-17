/********************************************************************************
 * Copyright (C) 2005-2026, Suzhou Tongyuan Software&Control Technology Co.,Ltd.
 * All rights reserved.
 * 版权所有 (C) 2005-2026， 苏州同元软控技术股份有限公司
 * 保留所有权利。
 *
 * 该文件由MWORKS内核代码生成器自动生成。
 *
 * 文件名称: MoSim_P6_SafetySupervisor_CFunction_Sysblock.c
 * 生成时间: 2026-07-17 03:12:19
 *
********************************************************************************/

#include "MoSim_P6_SafetySupervisor_CFunction_Sysblock.h"
#include "mwb_runtime.h"
#include "MoSim_P6_SafetySupervisor_CFunction_Sysblock_private.h"
#include "MoSim_P6_SafetySupervisor_CFunction_Sysblock_extern_include.h"

struct function_sysblockExtU function_sysblockGbIn;
struct function_sysblockExtY cfunction_sysblockGbOut;
struct nction_sysblockDw unction_sysblockGbDw;
static struct cfunction_sysblockTagEmd unction_sysblockStMd;
nction_sysblockEmd*const unction_sysblockGbMd = &unction_sysblockStMd;

void Step(void)
{
  {
    void MosimSafetySupervisorStepScalar(const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const 
    MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, 
    const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, 
    const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, MwbDouble* 
    , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* 
    , MwbDouble* );
    MosimSafetySupervisorStepScalar(function_sysblockGbIn.mode_id_in, function_sysblockGbIn.dt_in, function_sysblockGbIn.position_x_in, 
    function_sysblockGbIn.position_y_in, function_sysblockGbIn.position_z_in, function_sysblockGbIn.velocity_x_in, function_sysblockGbIn.velocity_y_in, 
function_sysblockGbIn.velocity_z_in, function_sysblockGbIn.candidate_acceleration_x_in, function_sysblockGbIn.candidate_acceleration_y_in, 
function_sysblockGbIn.candidate_acceleration_z_in, function_sysblockGbIn.candidate_thrust_in, function_sysblockGbIn.candidate_tilt_rad_in, 
function_sysblockGbIn.reference_position_x_in, function_sysblockGbIn.reference_position_y_in, function_sysblockGbIn.reference_position_z_in, 
function_sysblockGbIn.home_position_x_in, function_sysblockGbIn.home_position_y_in, function_sysblockGbIn.home_position_z_in, function_sysblockGbIn.obstacle_distance_in, 
function_sysblockGbIn.command_age_s_in, function_sysblockGbIn.state_valid_in, function_sysblockGbIn.offboard_valid_in, function_sysblockGbIn.emergency_request_in, 
function_sysblockGbIn.return_request_in, function_sysblockGbIn.land_request_in, function_sysblockGbIn.enable_in, function_sysblockGbIn.reset_in, 
&(cfunction_sysblockGbOut.safe_acceleration_x_out), &(cfunction_sysblockGbOut.safe_acceleration_y_out), &(cfunction_sysblockGbOut.safe_acceleration_z_out), 
&(cfunction_sysblockGbOut.safe_thrust_out), &(cfunction_sysblockGbOut.safe_reference_x_out), &(cfunction_sysblockGbOut.safe_reference_y_out), 
&(cfunction_sysblockGbOut.safe_reference_z_out), &(cfunction_sysblockGbOut.action_out), &(cfunction_sysblockGbOut.state_out), &(cfunction_sysblockGbOut.active_constraints_out), 
&(cfunction_sysblockGbOut.modified_out), &(cfunction_sysblockGbOut.status_code_out));
  }
  ++unction_sysblockGbMd->m_timeTickCount;
}

void Init(void)
{
  unction_sysblockGbMd->m_stepSize = 0.01;
}



/********************************************************************************
** end of file
********************************************************************************/
