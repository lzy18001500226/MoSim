/********************************************************************************
 * Copyright (C) 2005-2026, Suzhou Tongyuan Software&Control Technology Co.,Ltd.
 * All rights reserved.
 * 版权所有 (C) 2005-2026， 苏州同元软控技术股份有限公司
 * 保留所有权利。
 *
 * 该文件由MWORKS内核代码生成器自动生成。
 *
 * 文件名称: PX4CTRL_Original_OuterLoop_Graphical_Sysblock_private.h
 * 生成时间: 2026-07-30 15:17:24
 *
********************************************************************************/

#ifndef RLOOP_GRAPHICAL_SYSBLOCK_PRIVATE_H
#define RLOOP_GRAPHICAL_SYSBLOCK_PRIVATE_H

#include "PX4CTRL_Original_OuterLoop_Graphical_Sysblock.h"

struct graphical_sysblockExtU
{
  MwbDouble ref_px;
  MwbDouble px;
  MwbDouble ref_vx;
  MwbDouble vx;
  MwbDouble ref_ax;
  MwbDouble ref_py;
  MwbDouble py;
  MwbDouble ref_vy;
  MwbDouble vy;
  MwbDouble ref_ay;
  MwbDouble ref_pz;
  MwbDouble pz;
  MwbDouble ref_vz;
  MwbDouble vz;
  MwbDouble ref_az;
  MwbDouble yaw_mea;
  MwbDouble ref_yaw;
};

struct graphical_sysblockExtY
{
  MwbDouble desired_acc_x;
  MwbDouble desired_acc_y;
  MwbDouble desired_acc_z;
  MwbDouble roll_cmd;
  MwbDouble pitch_cmd;
  MwbDouble yaw_cmd;
  MwbDouble collective_thrust_n;
  MwbDouble normalized_thrust;
};

struct phical_sysblockB
{
  MwbDouble y1;
  MwbDouble y1_b;
  MwbDouble y;
  MwbDouble y_e;
  MwbDouble y_g;
  MwbDouble y_k;
  MwbDouble y_m;
  MwbDouble y_q;
  MwbDouble y_s;
  MwbDouble y_w;
  MwbDouble y_y;
  MwbDouble y_da;
  MwbDouble y_fa;
  MwbDouble y_ka;
  MwbDouble y_na;
  MwbDouble y_qa;
  MwbDouble y_ta;
  MwbDouble y_cb;
  MwbDouble y_gb;
  MwbDouble y_ib;
  MwbDouble y_nb;
  MwbDouble y_qb;
  MwbDouble y_vb;
  MwbDouble y_yb;
  MwbDouble y_ec;
  MwbDouble y_gc;
  MwbDouble y_ic;
  MwbDouble y_jc;
  MwbDouble y_mc;
  MwbDouble y_pc;
};

struct aphical_sysblockDw
{
  MwbDouble u1;
  MwbDouble u1_a;
  MwbDouble u;
  MwbDouble k;
  MwbDouble u1_c;
  MwbDouble u2;
  MwbDouble u_d;
  MwbDouble k_f;
  MwbDouble u1_h;
  MwbDouble u2_i;
  MwbDouble u_j;
  MwbDouble k_l;
  MwbDouble u1_n;
  MwbDouble u2_o;
  MwbDouble u_p;
  MwbDouble k_r;
  MwbDouble u1_t;
  MwbDouble u2_u;
  MwbDouble u_v;
  MwbDouble k_x;
  MwbDouble u1_aa;
  MwbDouble u2_ba;
  MwbDouble u_ca;
  MwbDouble k_ea;
  MwbDouble u1_ga;
  MwbDouble u2_ha;
  MwbDouble u1_ia;
  MwbDouble u2_ja;
  MwbDouble u1_la;
  MwbDouble u2_ma;
  MwbDouble u1_oa;
  MwbDouble u2_pa;
  MwbDouble u1_ra;
  MwbDouble u2_sa;
  MwbDouble u1_ua;
  MwbDouble u2_va;
  MwbDouble u1_wa;
  MwbDouble u2_xa;
  MwbDouble u1_ya;
  MwbDouble u2_za;
  MwbDouble u1_ab;
  MwbDouble u2_bb;
  MwbDouble u1_db;
  MwbDouble u2_eb;
  MwbDouble u_fb;
  MwbDouble k_hb;
  MwbDouble u1_jb;
  MwbDouble u2_kb;
  MwbDouble u1_lb;
  MwbDouble u2_mb;
  MwbDouble u1_ob;
  MwbDouble u2_pb;
  MwbDouble u1_rb;
  MwbDouble u2_sb;
  MwbDouble u1_tb;
  MwbDouble u2_ub;
  MwbDouble u1_wb;
  MwbDouble u2_xb;
  MwbDouble u1_zb;
  MwbDouble u2_ac;
  MwbDouble u1_bc;
  MwbDouble u2_cc;
  MwbDouble k_dc;
  MwbDouble k_fc;
  MwbDouble k_hc;
  MwbDouble u1_kc;
  MwbDouble u2_lc;
  MwbDouble u1_nc;
  MwbDouble u2_oc;
  MwbDouble u1_qc;
  MwbDouble u2_rc;
  MwbInt8 warn_flag0;
  MwbInt8 warn_flag1;
  MwbInt8 warn_flag2;
  MwbInt8 warn_flag3;
  MwbInt8 warn_flag4;
};



#endif /* RLOOP_GRAPHICAL_SYSBLOCK_PRIVATE_H */

/********************************************************************************
** end of file
********************************************************************************/
