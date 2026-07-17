/********************************************************************************
 * Copyright (C) 2005-2026, Suzhou Tongyuan Software&Control Technology Co.,Ltd.
 * All rights reserved.
 * 版权所有 (C) 2005-2026， 苏州同元软控技术股份有限公司
 * 保留所有权利。
 *
 * 该文件由MWORKS内核代码生成器自动生成。
 *
 * 文件名称: MoSim_P8_FormationControl_CFunction_Sysblock.c
 * 生成时间: 2026-07-17 07:15:29
 *
********************************************************************************/

#include "MoSim_P8_FormationControl_CFunction_Sysblock.h"
#include "mwb_runtime.h"
#include "MoSim_P8_FormationControl_CFunction_Sysblock_private.h"
#include "MoSim_P8_FormationControl_CFunction_Sysblock_extern_include.h"

struct function_sysblockExtU function_sysblockGbIn;
struct function_sysblockExtY cfunction_sysblockGbOut;
struct nction_sysblockDw unction_sysblockGbDw;
static struct cfunction_sysblockTagEmd unction_sysblockStMd;
nction_sysblockEmd*const unction_sysblockGbMd = &unction_sysblockStMd;

void Step(void)
{
  {
    void MosimFormationControlStepScalar(const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const 
    MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, 
    const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, 
    const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, 
    const MwbDouble, const MwbDouble, const MwbDouble, const MwbDouble, MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* 
    , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* 
    , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* , MwbDouble* );
    MosimFormationControlStepScalar(function_sysblockGbIn.mode_id_in, function_sysblockGbIn.dt_in, function_sysblockGbIn.leader_x_in, 
    function_sysblockGbIn.leader_y_in, function_sysblockGbIn.leader_z_in, function_sysblockGbIn.leader_vx_in, function_sysblockGbIn.leader_vy_in, 
function_sysblockGbIn.leader_vz_in, function_sysblockGbIn.leader_yaw_in, function_sysblockGbIn.position_1_x_in, function_sysblockGbIn.position_1_y_in, 
function_sysblockGbIn.position_1_z_in, function_sysblockGbIn.position_2_x_in, function_sysblockGbIn.position_2_y_in, function_sysblockGbIn.position_2_z_in, 
function_sysblockGbIn.position_3_x_in, function_sysblockGbIn.position_3_y_in, function_sysblockGbIn.position_3_z_in, function_sysblockGbIn.velocity_1_x_in, 
function_sysblockGbIn.velocity_1_y_in, function_sysblockGbIn.velocity_1_z_in, function_sysblockGbIn.velocity_2_x_in, function_sysblockGbIn.velocity_2_y_in, 
function_sysblockGbIn.velocity_2_z_in, function_sysblockGbIn.velocity_3_x_in, function_sysblockGbIn.velocity_3_y_in, function_sysblockGbIn.velocity_3_z_in, 
function_sysblockGbIn.healthy_1_in, function_sysblockGbIn.healthy_2_in, function_sysblockGbIn.healthy_3_in, function_sysblockGbIn.reconfigure_in, 
function_sysblockGbIn.enable_in, function_sysblockGbIn.reset_in, &(cfunction_sysblockGbOut.desired_position_1_x_out), &(cfunction_sysblockGbOut.desired_position_1_y_out), 
&(cfunction_sysblockGbOut.desired_position_1_z_out), &(cfunction_sysblockGbOut.desired_position_2_x_out), &(cfunction_sysblockGbOut.desired_position_2_y_out), 
&(cfunction_sysblockGbOut.desired_position_2_z_out), &(cfunction_sysblockGbOut.desired_position_3_x_out), &(cfunction_sysblockGbOut.desired_position_3_y_out), 
&(cfunction_sysblockGbOut.desired_position_3_z_out), &(cfunction_sysblockGbOut.desired_velocity_1_x_out), &(cfunction_sysblockGbOut.desired_velocity_1_y_out), 
&(cfunction_sysblockGbOut.desired_velocity_1_z_out), &(cfunction_sysblockGbOut.desired_velocity_2_x_out), &(cfunction_sysblockGbOut.desired_velocity_2_y_out), 
&(cfunction_sysblockGbOut.desired_velocity_2_z_out), &(cfunction_sysblockGbOut.desired_velocity_3_x_out), &(cfunction_sysblockGbOut.desired_velocity_3_y_out), 
&(cfunction_sysblockGbOut.desired_velocity_3_z_out), &(cfunction_sysblockGbOut.minimum_pair_distance_out), &(cfunction_sysblockGbOut.formation_rmse_out), 
&(cfunction_sysblockGbOut.active_agents_out), &(cfunction_sysblockGbOut.failed_mask_out), &(cfunction_sysblockGbOut.safety_corrections_out), 
&(cfunction_sysblockGbOut.status_code_out));
  }
  ++unction_sysblockGbMd->m_timeTickCount;
}

void Init(void)
{
  unction_sysblockGbMd->m_stepSize = 0.02;
}



/********************************************************************************
** end of file
********************************************************************************/
