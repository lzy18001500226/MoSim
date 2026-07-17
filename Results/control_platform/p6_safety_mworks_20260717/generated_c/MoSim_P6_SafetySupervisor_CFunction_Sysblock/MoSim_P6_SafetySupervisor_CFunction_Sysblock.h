/********************************************************************************
 * Copyright (C) 2005-2026, Suzhou Tongyuan Software&Control Technology Co.,Ltd.
 * All rights reserved.
 * 版权所有 (C) 2005-2026， 苏州同元软控技术股份有限公司
 * 保留所有权利。
 *
 * 该文件由MWORKS内核代码生成器自动生成。
 *
 * 文件名称: MoSim_P6_SafetySupervisor_CFunction_Sysblock.h
 * 生成时间: 2026-07-17 03:12:19
 *
********************************************************************************/

#ifndef NCTION_SYSBLOCK_H
#define NCTION_SYSBLOCK_H

#ifndef YSUPERVISOR_CFUNCTION_SYSBLOCK_COMMON_INCLUDES_
#define YSUPERVISOR_CFUNCTION_SYSBLOCK_COMMON_INCLUDES_
#include "mwb_types.h"
#include "math.h"
#endif /* YSUPERVISOR_CFUNCTION_SYSBLOCK_COMMON_INCLUDES_ */

typedef struct cfunction_sysblockTagEmd nction_sysblockEmd;

struct cfunction_sysblockTagEmd{
  MwbDouble m_curTime;
  MwbDouble m_startTime;
  MwbDouble m_stepSize;
  MwbInt32 m_timeTickCount;
};

/* External inputs (root inport signals) */
extern struct function_sysblockExtU function_sysblockGbIn;

/* External outputs (root outport signals) */
extern struct function_sysblockExtY cfunction_sysblockGbOut;

/* Block states */
extern struct nction_sysblockDw unction_sysblockGbDw;

extern nction_sysblockEmd*const unction_sysblockGbMd;

void Step(void);
void Init(void);


#endif /* NCTION_SYSBLOCK_H */

/********************************************************************************
** end of file
********************************************************************************/
