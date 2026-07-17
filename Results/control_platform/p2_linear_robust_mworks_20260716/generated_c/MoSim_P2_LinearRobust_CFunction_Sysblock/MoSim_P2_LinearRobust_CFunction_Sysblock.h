/********************************************************************************
 * Copyright (C) 2005-2026, Suzhou Tongyuan Software&Control Technology Co.,Ltd.
 * All rights reserved.
 * 版权所有 (C) 2005-2026， 苏州同元软控技术股份有限公司
 * 保留所有权利。
 *
 * 该文件由MWORKS内核代码生成器自动生成。
 *
 * 文件名称: MoSim_P2_LinearRobust_CFunction_Sysblock.h
 * 生成时间: 2026-07-17 09:21:58
 *
********************************************************************************/

#ifndef ON_SYSBLOCK_H
#define ON_SYSBLOCK_H

#ifndef RROBUST_CFUNCTION_SYSBLOCK_COMMON_INCLUDES_
#define RROBUST_CFUNCTION_SYSBLOCK_COMMON_INCLUDES_
#include "mwb_types.h"
#include "math.h"
#endif /* RROBUST_CFUNCTION_SYSBLOCK_COMMON_INCLUDES_ */

typedef struct ction_sysblockTagEmd on_sysblockEmd;

struct ction_sysblockTagEmd{
  MwbDouble m_curTime;
  MwbDouble m_startTime;
  MwbDouble m_stepSize;
  MwbInt32 m_timeTickCount;
};

/* External inputs (root inport signals) */
extern struct tion_sysblockExtU tion_sysblockGbIn;

/* External outputs (root outport signals) */
extern struct tion_sysblockExtY ction_sysblockGbOut;

/* Block states */
extern struct on_sysblockDw ion_sysblockGbDw;

extern on_sysblockEmd*const ion_sysblockGbMd;

void Step(void);
void Init(void);


#endif /* ON_SYSBLOCK_H */

/********************************************************************************
** end of file
********************************************************************************/
