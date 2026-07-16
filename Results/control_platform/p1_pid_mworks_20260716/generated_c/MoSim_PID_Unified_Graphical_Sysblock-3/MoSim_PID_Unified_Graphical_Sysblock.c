/********************************************************************************
 * Copyright (C) 2005-2026, Suzhou Tongyuan Software&Control Technology Co.,Ltd.
 * All rights reserved.
 * 版权所有 (C) 2005-2026， 苏州同元软控技术股份有限公司
 * 保留所有权利。
 *
 * 该文件由MWORKS内核代码生成器自动生成。
 *
 * 文件名称: MoSim_PID_Unified_Graphical_Sysblock.c
 * 生成时间: 2026-07-16 14:13:22
 *
********************************************************************************/

#include "MoSim_PID_Unified_Graphical_Sysblock.h"
#include "mwb_runtime.h"
#include "MoSim_PID_Unified_Graphical_Sysblock_private.h"
#include "MoSim_PID_Unified_Graphical_Sysblock_extern_include.h"

struct asysblockExtU asysblockGbIn;
struct asysblockExtY l_sysblockGbOut;
struct sblockB ysblockGbB;
struct ysblockDw sysblockGbDw;
static struct l_sysblockTagEmd sysblockStMd;
ysblockEmd*const sysblockGbMd = &sysblockStMd;

void Step(void)
{
  ysblockGbB.y_dd = sysblockGbDw.k_cd;
  ysblockGbB.y_fd = sysblockGbDw.k_ed;
  ysblockGbB.y_hd = sysblockGbDw.k_gd;
  ysblockGbB.y_jd = sysblockGbDw.k_id;
  ysblockGbB.y_ld = sysblockGbDw.k_kd;
  ysblockGbB.y_nd = sysblockGbDw.k_md;
  ysblockGbB.y_pd = sysblockGbDw.k_od;
  ysblockGbB.y_rd = sysblockGbDw.k_qd;
  ysblockGbB.y_td = sysblockGbDw.k_sd;
  ysblockGbB.y_vd = sysblockGbDw.k_ud;
  ysblockGbB.y_xd = sysblockGbDw.k_wd;
  ysblockGbB.y_zd = sysblockGbDw.k_yd;
  ysblockGbB.y_be = sysblockGbDw.k_ae;
  ysblockGbB.y_de = sysblockGbDw.k_ce;
  ysblockGbB.y = sysblockGbDw.k * asysblockGbIn.schedule;
  ysblockGbB.y_b = sysblockGbDw.k_c * asysblockGbIn.fuzzy_error;
  if (asysblockGbIn.neural_residual > ysblockGbB.y_fd)
  {
    ysblockGbB.y_e = ysblockGbB.y_fd;
  }
  else if (asysblockGbIn.neural_residual < ysblockGbB.y_hd)
  {
    ysblockGbB.y_e = ysblockGbB.y_hd;
  }
  else
  {
    ysblockGbB.y_e = asysblockGbIn.neural_residual;
  }
  ysblockGbB.y_g = sysblockGbDw.k_h * ysblockGbB.y_e;
  ysblockGbB.y_i = ysblockGbB.y_dd + ysblockGbB.y;
  ysblockGbB.y_j = ysblockGbB.y_i + ysblockGbB.y_b;
  ysblockGbB.y_m = ysblockGbB.y_j + ysblockGbB.y_g;
  if (ysblockGbB.y_m > ysblockGbB.y_jd)
  {
    l_sysblockGbOut.scheduled_gain = ysblockGbB.y_jd;
  }
  else if (ysblockGbB.y_m < ysblockGbB.y_ld)
  {
    l_sysblockGbOut.scheduled_gain = ysblockGbB.y_ld;
  }
  else
  {
    l_sysblockGbOut.scheduled_gain = ysblockGbB.y_m;
  }
  ysblockGbB.y_s = asysblockGbIn.setpoint - asysblockGbIn.measurement;
  ysblockGbB.y_v = ysblockGbB.y_s * l_sysblockGbOut.scheduled_gain;
  ysblockGbB.y_aa = sysblockGbDw.k_ba * ysblockGbB.y_v;
  ysblockGbB.y_da = sysblockGbDw.k_ea * ysblockGbB.y_v;
  ysblockGbB.y_ga = sysblockGbDw.yb;
  sysblockGbDw.yb = ysblockGbB.y_s;
  ysblockGbB.y_ha = ysblockGbB.y_s - ysblockGbB.y_ga;
  ysblockGbB.y_la = sysblockGbDw.k_ma * ysblockGbB.y_ha;
  l_sysblockGbOut.integral_state = sysblockGbDw.yb_qa;
  ysblockGbB.y_sa = sysblockGbDw.k_ta * l_sysblockGbOut.integral_state;
  ysblockGbB.y_va = sysblockGbDw.k_wa * asysblockGbIn.feedforward;
  ysblockGbB.y_xa = ysblockGbB.y_aa + ysblockGbB.y_sa;
  ysblockGbB.y_ab = ysblockGbB.y_xa + ysblockGbB.y_la;
  l_sysblockGbOut.unsaturated_command = ysblockGbB.y_ab + ysblockGbB.y_va;
  if (l_sysblockGbOut.unsaturated_command > ysblockGbB.y_rd)
  {
    ysblockGbB.y_ib = ysblockGbB.y_rd;
  }
  else if (l_sysblockGbOut.unsaturated_command < ysblockGbB.y_td)
  {
    ysblockGbB.y_ib = ysblockGbB.y_td;
  }
  else
  {
    ysblockGbB.y_ib = l_sysblockGbOut.unsaturated_command;
  }
  ysblockGbB.y_jb = ysblockGbB.y_ib - l_sysblockGbOut.unsaturated_command;
  ysblockGbB.y_nb = sysblockGbDw.k_ob * ysblockGbB.y_jb;
  ysblockGbB.y_pb = ysblockGbB.y_da + ysblockGbB.y_nb;
  ysblockGbB.y_tb = sysblockGbDw.k_ub * ysblockGbB.y_pb;
  ysblockGbB.y_vb = ysblockGbB.y_tb + l_sysblockGbOut.integral_state;
  if (ysblockGbB.y_vb > ysblockGbB.y_nd)
  {
    ysblockGbB.y_bc = ysblockGbB.y_nd;
  }
  else if (ysblockGbB.y_vb < ysblockGbB.y_pd)
  {
    ysblockGbB.y_bc = ysblockGbB.y_pd;
  }
  else
  {
    ysblockGbB.y_bc = ysblockGbB.y_vb;
  }
  ysblockGbB.y_cc = asysblockGbIn.setpoint - asysblockGbIn.measurement;
  ysblockGbB.y_gc = sysblockGbDw.k_hc * ysblockGbB.y_cc;
  if (ysblockGbB.y_gc > ysblockGbB.y_vd)
  {
    l_sysblockGbOut.outer_command = ysblockGbB.y_vd;
  }
  else if (ysblockGbB.y_gc < ysblockGbB.y_xd)
  {
    l_sysblockGbOut.outer_command = ysblockGbB.y_xd;
  }
  else
  {
    l_sysblockGbOut.outer_command = ysblockGbB.y_gc;
  }
  ysblockGbB.y_lc = l_sysblockGbOut.outer_command - asysblockGbIn.inner_measurement;
  ysblockGbB.y_pc = sysblockGbDw.k_qc * ysblockGbB.y_lc;
  if (ysblockGbB.y_pc > ysblockGbB.y_zd)
  {
    ysblockGbB.y_uc = ysblockGbB.y_zd;
  }
  else if (ysblockGbB.y_pc < ysblockGbB.y_be)
  {
    ysblockGbB.y_uc = ysblockGbB.y_be;
  }
  else
  {
    ysblockGbB.y_uc = ysblockGbB.y_pc;
  }
  if (asysblockGbIn.cascade_mode >= sysblockGbDw.threshold)
  {
    ysblockGbB.y_vc = ysblockGbB.y_uc;
  }
  else
  {
    ysblockGbB.y_vc = ysblockGbB.y_ib;
  }
  if (asysblockGbIn.enable >= sysblockGbDw.threshold_bd)
  {
    l_sysblockGbOut.command = ysblockGbB.y_vc;
  }
  else
  {
    l_sysblockGbOut.command = ysblockGbB.y_de;
  }
  sysblockGbDw.yb_qa = ysblockGbB.y_bc;
  ++sysblockGbMd->m_timeTickCount;
}

void Init(void)
{
  sysblockGbMd->m_stepSize = 0.02;
  sysblockGbDw.k_cd = 1.0;
  sysblockGbDw.k_ed = 0.25;
  sysblockGbDw.k_gd = (-0.25);
  sysblockGbDw.k_id = 4.0;
  sysblockGbDw.k_kd = 0.25;
  sysblockGbDw.k_md = 0.5;
  sysblockGbDw.k_od = (-0.5);
  sysblockGbDw.k_qd = 1.0;
  sysblockGbDw.k_sd = (-1.0);
  sysblockGbDw.k_ud = 1.0;
  sysblockGbDw.k_wd = (-1.0);
  sysblockGbDw.k_yd = 1.0;
  sysblockGbDw.k_ae = (-1.0);
  sysblockGbDw.k_ce = 0.0;
  sysblockGbDw.k = 0.4;
  sysblockGbDw.k_c = 0.3;
  sysblockGbDw.k_h = 0.2;
  sysblockGbDw.k_ba = 1.2;
  sysblockGbDw.k_ea = 1.0;
  sysblockGbDw.initCond = 0.0;
  sysblockGbDw.k_ma = 5.0;
  sysblockGbDw.initCond_na = 0.0;
  sysblockGbDw.k_ta = 0.8;
  sysblockGbDw.k_wa = 0.5;
  sysblockGbDw.k_ob = 0.4;
  sysblockGbDw.k_ub = 0.02;
  sysblockGbDw.k_hc = 1.2;
  sysblockGbDw.k_qc = 1.5;
  sysblockGbDw.threshold = 0.5;
  sysblockGbDw.threshold_bd = 0.5;
  sysblockGbDw.yb = sysblockGbDw.initCond;
  sysblockGbDw.yb_qa = sysblockGbDw.initCond_na;
}



/********************************************************************************
** end of file
********************************************************************************/
