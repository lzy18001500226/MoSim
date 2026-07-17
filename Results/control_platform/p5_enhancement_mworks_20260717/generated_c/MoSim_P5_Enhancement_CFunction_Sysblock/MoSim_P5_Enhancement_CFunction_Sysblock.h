/********************************************************************************
 * Copyright (C) 2005-2026, Suzhou Tongyuan Software&Control Technology Co.,Ltd.
 * All rights reserved.
 * 版权所有 (C) 2005-2026， 苏州同元软控技术股份有限公司
 * 保留所有权利。
 *
 * 该文件由MWORKS内核代码生成器自动生成。
 *
 * 文件名称: MoSim_P5_Enhancement_CFunction_Sysblock.h
 * 生成时间: 2026-07-17 09:21:59
 *
********************************************************************************/

#ifndef N_SYSBLOCK_H
#define N_SYSBLOCK_H

#ifndef CEMENT_CFUNCTION_SYSBLOCK_COMMON_INCLUDES_
#define CEMENT_CFUNCTION_SYSBLOCK_COMMON_INCLUDES_
#include "mwb_types.h"
#include "math.h"
#endif /* CEMENT_CFUNCTION_SYSBLOCK_COMMON_INCLUDES_ */

typedef struct tion_sysblockTagEmd n_sysblockEmd;

struct tion_sysblockTagEmd{
  MwbDouble m_curTime;
  MwbDouble m_startTime;
  MwbDouble m_stepSize;
  MwbInt32 m_timeTickCount;
};

/* External inputs (root inport signals) */
extern struct ion_sysblockExtU ion_sysblockGbIn;

/* External outputs (root outport signals) */
extern struct ion_sysblockExtY tion_sysblockGbOut;

/* Block states */
extern struct n_sysblockDw on_sysblockGbDw;

extern n_sysblockEmd*const on_sysblockGbMd;

void Step(void);
void Init(void);


#endif /* N_SYSBLOCK_H */

/********************************************************************************
** end of file
********************************************************************************/
