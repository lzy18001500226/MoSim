/********************************************************************************
 * Copyright (C) 2005-2026, Suzhou Tongyuan Software&Control Technology Co.,Ltd.
 * All rights reserved.
 * 版权所有 (C) 2005-2026， 苏州同元软控技术股份有限公司
 * 保留所有权利。
 *
 * 该文件由MWORKS内核代码生成器自动生成。
 *
 * 文件名称: MoSim_PID_AttitudeThrust_CFunction_Sysblock.h
 * 生成时间: 2026-07-16 15:23:16
 *
********************************************************************************/

#ifndef CTION_SYSBLOCK_H
#define CTION_SYSBLOCK_H

#ifndef TUDETHRUST_CFUNCTION_SYSBLOCK_COMMON_INCLUDES_
#define TUDETHRUST_CFUNCTION_SYSBLOCK_COMMON_INCLUDES_
#include "mwb_types.h"
#include "math.h"
#endif /* TUDETHRUST_CFUNCTION_SYSBLOCK_COMMON_INCLUDES_ */

typedef struct function_sysblockTagEmd ction_sysblockEmd;

struct function_sysblockTagEmd{
  MwbDouble m_curTime;
  MwbDouble m_startTime;
  MwbDouble m_stepSize;
  MwbInt32 m_timeTickCount;
};

/* External inputs (root inport signals) */
extern struct unction_sysblockExtU unction_sysblockGbIn;

/* External outputs (root outport signals) */
extern struct unction_sysblockExtY function_sysblockGbOut;

/* Block states */
extern struct ction_sysblockDw nction_sysblockGbDw;

extern ction_sysblockEmd*const nction_sysblockGbMd;

void Step(void);
void Init(void);


#endif /* CTION_SYSBLOCK_H */

/********************************************************************************
** end of file
********************************************************************************/
