/********************************************************************************
 * Copyright (C) 2005-2026, Suzhou Tongyuan Software&Control Technology Co.,Ltd.
 * All rights reserved.
 * 版权所有 (C) 2005-2026， 苏州同元软控技术股份有限公司
 * 保留所有权利。
 *
 * 该文件由MWORKS内核代码生成器自动生成。
 *
 * 文件名称: MoSim_PID_Unified_Graphical_Sysblock_private.h
 * 生成时间: 2026-07-16 14:13:22
 *
********************************************************************************/

#ifndef PHICAL_SYSBLOCK_PRIVATE_H
#define PHICAL_SYSBLOCK_PRIVATE_H

#include "MoSim_PID_Unified_Graphical_Sysblock.h"

struct asysblockExtU
{
  MwbDouble setpoint;
  MwbDouble measurement;
  MwbDouble inner_measurement;
  MwbDouble feedforward;
  MwbDouble schedule;
  MwbDouble fuzzy_error;
  MwbDouble neural_residual;
  MwbDouble cascade_mode;
  MwbDouble enable;
};

struct asysblockExtY
{
  MwbDouble command;
  MwbDouble outer_command;
  MwbDouble unsaturated_command;
  MwbDouble integral_state;
  MwbDouble scheduled_gain;
};

struct sblockB
{
  MwbDouble y;
  MwbDouble y_b;
  MwbDouble y_e;
  MwbDouble y_g;
  MwbDouble y_i;
  MwbDouble y_j;
  MwbDouble y_m;
  MwbDouble y_s;
  MwbDouble y_v;
  MwbDouble y_aa;
  MwbDouble y_da;
  MwbDouble y_ga;
  MwbDouble y_ha;
  MwbDouble y_la;
  MwbDouble y_sa;
  MwbDouble y_va;
  MwbDouble y_xa;
  MwbDouble y_ab;
  MwbDouble y_ib;
  MwbDouble y_jb;
  MwbDouble y_nb;
  MwbDouble y_pb;
  MwbDouble y_tb;
  MwbDouble y_vb;
  MwbDouble y_bc;
  MwbDouble y_cc;
  MwbDouble y_gc;
  MwbDouble y_lc;
  MwbDouble y_pc;
  MwbDouble y_uc;
  MwbDouble y_vc;
  MwbDouble y_dd;
  MwbDouble y_fd;
  MwbDouble y_hd;
  MwbDouble y_jd;
  MwbDouble y_ld;
  MwbDouble y_nd;
  MwbDouble y_pd;
  MwbDouble y_rd;
  MwbDouble y_td;
  MwbDouble y_vd;
  MwbDouble y_xd;
  MwbDouble y_zd;
  MwbDouble y_be;
  MwbDouble y_de;
};

struct ysblockDw
{
  MwbDouble u;
  MwbDouble k;
  MwbDouble u_a;
  MwbDouble k_c;
  MwbDouble upperLimit;
  MwbDouble u_d;
  MwbDouble lowerLimit;
  MwbDouble u_f;
  MwbDouble k_h;
  MwbDouble u1;
  MwbDouble u2;
  MwbDouble u1_k;
  MwbDouble u2_l;
  MwbDouble u1_n;
  MwbDouble u2_o;
  MwbDouble upperLimit_p;
  MwbDouble u_q;
  MwbDouble lowerLimit_r;
  MwbDouble u1_t;
  MwbDouble u2_u;
  MwbDouble u1_w;
  MwbDouble u2_x;
  MwbDouble u_y;
  MwbDouble k_ba;
  MwbDouble u_ca;
  MwbDouble k_ea;
  MwbDouble initCond;
  MwbDouble u1_fa;
  MwbDouble unitDelayBuffer;
  MwbDouble yb;
  MwbDouble u1_ia;
  MwbDouble u2_ja;
  MwbDouble u_ka;
  MwbDouble k_ma;
  MwbDouble initCond_na;
  MwbDouble u1_oa;
  MwbDouble unitDelayBuffer_pa;
  MwbDouble yb_qa;
  MwbDouble u_ra;
  MwbDouble k_ta;
  MwbDouble u_ua;
  MwbDouble k_wa;
  MwbDouble u1_ya;
  MwbDouble u2_za;
  MwbDouble u1_bb;
  MwbDouble u2_cb;
  MwbDouble u1_db;
  MwbDouble u2_eb;
  MwbDouble upperLimit_fb;
  MwbDouble u_gb;
  MwbDouble lowerLimit_hb;
  MwbDouble u1_kb;
  MwbDouble u2_lb;
  MwbDouble u_mb;
  MwbDouble k_ob;
  MwbDouble u1_qb;
  MwbDouble u2_rb;
  MwbDouble u_sb;
  MwbDouble k_ub;
  MwbDouble u1_wb;
  MwbDouble u2_xb;
  MwbDouble upperLimit_yb;
  MwbDouble u_zb;
  MwbDouble lowerLimit_ac;
  MwbDouble u1_dc;
  MwbDouble u2_ec;
  MwbDouble u_fc;
  MwbDouble k_hc;
  MwbDouble upperLimit_ic;
  MwbDouble u_jc;
  MwbDouble lowerLimit_kc;
  MwbDouble u1_mc;
  MwbDouble u2_nc;
  MwbDouble u_oc;
  MwbDouble k_qc;
  MwbDouble upperLimit_rc;
  MwbDouble u_sc;
  MwbDouble lowerLimit_tc;
  MwbDouble u1_wc;
  MwbDouble u2_xc;
  MwbDouble u3;
  MwbDouble threshold;
  MwbDouble u1_yc;
  MwbDouble u2_zc;
  MwbDouble u3_ad;
  MwbDouble threshold_bd;
  MwbDouble k_cd;
  MwbDouble k_ed;
  MwbDouble k_gd;
  MwbDouble k_id;
  MwbDouble k_kd;
  MwbDouble k_md;
  MwbDouble k_od;
  MwbDouble k_qd;
  MwbDouble k_sd;
  MwbDouble k_ud;
  MwbDouble k_wd;
  MwbDouble k_yd;
  MwbDouble k_ae;
  MwbDouble k_ce;
};



#endif /* PHICAL_SYSBLOCK_PRIVATE_H */

/********************************************************************************
** end of file
********************************************************************************/
