/********************************************************************************
 * Copyright (C) 2005-2026, Suzhou Tongyuan Software&Control Technology Co.,Ltd.
 * All rights reserved.
 * 版权所有 (C) 2005-2026， 苏州同元软控技术股份有限公司
 * 保留所有权利。
 *
 * 该文件由MWORKS内核代码生成器自动生成。
 *
 * 文件名称: PX4CTRL_Original_OuterLoop_Graphical_Sysblock.h
 * 生成时间: 2026-07-30 15:17:24
 *
********************************************************************************/

#ifndef APHICAL_SYSBLOCK_H
#define APHICAL_SYSBLOCK_H

#ifndef AL_OUTERLOOP_GRAPHICAL_SYSBLOCK_COMMON_INCLUDES_
#define AL_OUTERLOOP_GRAPHICAL_SYSBLOCK_COMMON_INCLUDES_
#include "mwb_types.h"
#include "math.h"
#endif /* AL_OUTERLOOP_GRAPHICAL_SYSBLOCK_COMMON_INCLUDES_ */

typedef struct agraphical_sysblockTagEmd aphical_sysblockEmd;

struct agraphical_sysblockTagEmd{
  MwbDouble m_curTime;
  MwbDouble m_startTime;
  MwbDouble m_stepSize;
  MwbInt32 m_timeTickCount;
};

/* External inputs (root inport signals) */
extern struct graphical_sysblockExtU graphical_sysblockGbIn;

/* External outputs (root outport signals) */
extern struct graphical_sysblockExtY agraphical_sysblockGbOut;

/* Block signals */
extern struct phical_sysblockB aphical_sysblockGbB;

/* Block states */
extern struct aphical_sysblockDw raphical_sysblockGbDw;

extern aphical_sysblockEmd*const raphical_sysblockGbMd;

void Step(void);
void Init(void);


#endif /* APHICAL_SYSBLOCK_H */

/********************************************************************************
** end of file
********************************************************************************/
