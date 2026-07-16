/********************************************************************************
 * Copyright (C) 2005-2026, Suzhou Tongyuan Software&Control Technology Co.,Ltd.
 * All rights reserved.
 * 版权所有 (C) 2005-2026， 苏州同元软控技术股份有限公司
 * 保留所有权利。
 *
 * 该文件由MWORKS内核代码生成器自动生成。
 *
 * 文件名称: MoSim_PID_Unified_Graphical_Sysblock.h
 * 生成时间: 2026-07-16 14:13:22
 *
********************************************************************************/

#ifndef YSBLOCK_H
#define YSBLOCK_H

#ifndef IED_GRAPHICAL_SYSBLOCK_COMMON_INCLUDES_
#define IED_GRAPHICAL_SYSBLOCK_COMMON_INCLUDES_
#include "mwb_types.h"
#include "math.h"
#endif /* IED_GRAPHICAL_SYSBLOCK_COMMON_INCLUDES_ */

typedef struct l_sysblockTagEmd ysblockEmd;

struct l_sysblockTagEmd{
  MwbDouble m_curTime;
  MwbDouble m_startTime;
  MwbDouble m_stepSize;
  MwbInt32 m_timeTickCount;
};

/* External inputs (root inport signals) */
extern struct asysblockExtU asysblockGbIn;

/* External outputs (root outport signals) */
extern struct asysblockExtY l_sysblockGbOut;

/* Block signals */
extern struct sblockB ysblockGbB;

/* Block states */
extern struct ysblockDw sysblockGbDw;

extern ysblockEmd*const sysblockGbMd;

void Step(void);
void Init(void);


#endif /* YSBLOCK_H */

/********************************************************************************
** end of file
********************************************************************************/
