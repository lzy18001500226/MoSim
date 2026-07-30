/********************************************************************************
 * Copyright (C) 2005-2026, Suzhou Tongyuan Software&Control Technology Co.,Ltd.
 * All rights reserved.
 * 版权所有 (C) 2005-2026， 苏州同元软控技术股份有限公司
 * 保留所有权利。
 *
 * 该文件由MWORKS内核代码生成器自动生成。
 *
 * 文件名称: PX4CTRL_Original_OuterLoop_Graphical_Sysblock.c
 * 生成时间: 2026-07-30 15:17:24
 *
********************************************************************************/

#include "PX4CTRL_Original_OuterLoop_Graphical_Sysblock.h"
#include "mwb_runtime.h"
#include "PX4CTRL_Original_OuterLoop_Graphical_Sysblock_private.h"
#include "PX4CTRL_Original_OuterLoop_Graphical_Sysblock_extern_include.h"

struct graphical_sysblockExtU graphical_sysblockGbIn;
struct graphical_sysblockExtY agraphical_sysblockGbOut;
struct phical_sysblockB aphical_sysblockGbB;
struct aphical_sysblockDw raphical_sysblockGbDw;
static struct agraphical_sysblockTagEmd raphical_sysblockStMd;
aphical_sysblockEmd*const raphical_sysblockGbMd = &raphical_sysblockStMd;

void Step(void)
{
  aphical_sysblockGbB.y_ec = raphical_sysblockGbDw.k_dc;
  aphical_sysblockGbB.y_gc = raphical_sysblockGbDw.k_fc;
  aphical_sysblockGbB.y_ic = raphical_sysblockGbDw.k_hc;
  aphical_sysblockGbB.y_jc = aphical_sysblockGbB.y_ec / aphical_sysblockGbB.y_ic;
  aphical_sysblockGbB.y_mc = aphical_sysblockGbB.y_gc * aphical_sysblockGbB.y_ec;
  aphical_sysblockGbB.y_pc = aphical_sysblockGbB.y_mc / aphical_sysblockGbB.y_ic;
  aphical_sysblockGbB.y1 = sin(graphical_sysblockGbIn.yaw_mea);
  aphical_sysblockGbB.y1_b = cos(graphical_sysblockGbIn.yaw_mea);
  agraphical_sysblockGbOut.yaw_cmd = raphical_sysblockGbDw.k * graphical_sysblockGbIn.ref_yaw;
  aphical_sysblockGbB.y = graphical_sysblockGbIn.ref_vx - graphical_sysblockGbIn.vx;
  aphical_sysblockGbB.y_e = raphical_sysblockGbDw.k_f * aphical_sysblockGbB.y;
  aphical_sysblockGbB.y_g = graphical_sysblockGbIn.ref_py - graphical_sysblockGbIn.py;
  aphical_sysblockGbB.y_k = raphical_sysblockGbDw.k_l * aphical_sysblockGbB.y_g;
  aphical_sysblockGbB.y_m = graphical_sysblockGbIn.ref_vy - graphical_sysblockGbIn.vy;
  aphical_sysblockGbB.y_q = raphical_sysblockGbDw.k_r * aphical_sysblockGbB.y_m;
  aphical_sysblockGbB.y_s = graphical_sysblockGbIn.ref_pz - graphical_sysblockGbIn.pz;
  aphical_sysblockGbB.y_w = raphical_sysblockGbDw.k_x * aphical_sysblockGbB.y_s;
  aphical_sysblockGbB.y_y = graphical_sysblockGbIn.ref_vz - graphical_sysblockGbIn.vz;
  aphical_sysblockGbB.y_da = raphical_sysblockGbDw.k_ea * aphical_sysblockGbB.y_y;
  aphical_sysblockGbB.y_fa = aphical_sysblockGbB.y_k + aphical_sysblockGbB.y_q;
  agraphical_sysblockGbOut.desired_acc_y = aphical_sysblockGbB.y_fa + graphical_sysblockGbIn.ref_ay;
  aphical_sysblockGbB.y_ka = agraphical_sysblockGbOut.desired_acc_y * aphical_sysblockGbB.y1;
  aphical_sysblockGbB.y_na = agraphical_sysblockGbOut.desired_acc_y * aphical_sysblockGbB.y1_b;
  aphical_sysblockGbB.y_qa = aphical_sysblockGbB.y_w + aphical_sysblockGbB.y_da;
  aphical_sysblockGbB.y_ta = aphical_sysblockGbB.y_qa + graphical_sysblockGbIn.ref_az;
  agraphical_sysblockGbOut.desired_acc_z = aphical_sysblockGbB.y_ta + aphical_sysblockGbB.y_ec;
  agraphical_sysblockGbOut.normalized_thrust = agraphical_sysblockGbOut.desired_acc_z / aphical_sysblockGbB.y_jc;
  agraphical_sysblockGbOut.collective_thrust_n = agraphical_sysblockGbOut.normalized_thrust * aphical_sysblockGbB.y_pc;
  aphical_sysblockGbB.y_cb = graphical_sysblockGbIn.ref_px - graphical_sysblockGbIn.px;
  aphical_sysblockGbB.y_gb = raphical_sysblockGbDw.k_hb * aphical_sysblockGbB.y_cb;
  aphical_sysblockGbB.y_ib = aphical_sysblockGbB.y_gb + aphical_sysblockGbB.y_e;
  agraphical_sysblockGbOut.desired_acc_x = aphical_sysblockGbB.y_ib + graphical_sysblockGbIn.ref_ax;
  aphical_sysblockGbB.y_nb = agraphical_sysblockGbOut.desired_acc_x * aphical_sysblockGbB.y1_b;
  aphical_sysblockGbB.y_qb = aphical_sysblockGbB.y_nb + aphical_sysblockGbB.y_ka;
  agraphical_sysblockGbOut.pitch_cmd = aphical_sysblockGbB.y_qb / aphical_sysblockGbB.y_ec;
  aphical_sysblockGbB.y_vb = agraphical_sysblockGbOut.desired_acc_x * aphical_sysblockGbB.y1;
  aphical_sysblockGbB.y_yb = aphical_sysblockGbB.y_vb - aphical_sysblockGbB.y_na;
  agraphical_sysblockGbOut.roll_cmd = aphical_sysblockGbB.y_yb / aphical_sysblockGbB.y_ec;
  ++raphical_sysblockGbMd->m_timeTickCount;
}

void Init(void)
{
  raphical_sysblockGbMd->m_stepSize = 0.01;
  raphical_sysblockGbDw.k_dc = 9.80665;
  raphical_sysblockGbDw.k_fc = 1.0;
  raphical_sysblockGbDw.k_hc = 0.37;
  raphical_sysblockGbDw.k = 1.0;
  raphical_sysblockGbDw.k_f = 1.5;
  raphical_sysblockGbDw.k_l = 1.5;
  raphical_sysblockGbDw.k_r = 1.5;
  raphical_sysblockGbDw.k_x = 1.5;
  raphical_sysblockGbDw.k_ea = 1.5;
  raphical_sysblockGbDw.k_hb = 1.5;
}



/********************************************************************************
** end of file
********************************************************************************/
