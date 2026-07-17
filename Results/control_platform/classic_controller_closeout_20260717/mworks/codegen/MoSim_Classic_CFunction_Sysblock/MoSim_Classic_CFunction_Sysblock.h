/********************************************************************************
 * Copyright (C) 2005-2026, Suzhou Tongyuan Software&Control Technology Co.,Ltd.
 * All rights reserved.
 * 版权所有 (C) 2005-2026， 苏州同元软控技术股份有限公司
 * 保留所有权利。
 *
 * 该文件由MWORKS内核代码生成器自动生成。
 *
 * 文件名称: MoSim_Classic_CFunction_Sysblock.h
 * 生成时间: 2026-07-17 20:28:29
 *
********************************************************************************/

#ifndef OCK_H
#define OCK_H

#ifndef CFUNCTION_SYSBLOCK_COMMON_INCLUDES_
#define CFUNCTION_SYSBLOCK_COMMON_INCLUDES_
#include "mwb_types.h"
#include "math.h"
#endif /* CFUNCTION_SYSBLOCK_COMMON_INCLUDES_ */

typedef struct sblockTagEmd ockEmd;

struct sblockTagEmd{
  MwbDouble m_curTime;
  MwbDouble m_startTime;
  MwbDouble m_stepSize;
  MwbInt32 m_timeTickCount;
};

/* External inputs (root inport signals) */
extern struct blockExtU blockGbIn;

/* External outputs (root outport signals) */
extern struct blockExtY sblockGbOut;

/* Block states */
extern struct ockDw lockGbDw;

extern ockEmd*const lockGbMd;

void Step(void);
void Init(void);


#endif /* OCK_H */

/********************************************************************************
** end of file
********************************************************************************/
