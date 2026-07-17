/********************************************************************************
 * Copyright (C) 2005-2026, Suzhou Tongyuan Software&Control Technology Co.,Ltd.
 * All rights reserved.
 * 版权所有 (C) 2005-2026， 苏州同元软控技术股份有限公司
 * 保留所有权利。
 *
 * 该文件由MWORKS内核代码生成器自动生成。
 *
 * 文件名称: MoSim_P7_FaultTolerantControl_CFunction_Sysblock.h
 * 生成时间: 2026-07-17 04:13:56
 *
********************************************************************************/

#ifndef aCFUNCTION_SYSBLOCK_H
#define aCFUNCTION_SYSBLOCK_H

#ifndef TOLERANTCONTROL_CFUNCTION_SYSBLOCK_COMMON_INCLUDES_
#define TOLERANTCONTROL_CFUNCTION_SYSBLOCK_COMMON_INCLUDES_
#include "mwb_types.h"
#include "math.h"
#endif /* TOLERANTCONTROL_CFUNCTION_SYSBLOCK_COMMON_INCLUDES_ */

typedef struct rol_cfunction_sysblockTagEmd acfunction_sysblockEmd;

struct rol_cfunction_sysblockTagEmd{
  MwbDouble m_curTime;
  MwbDouble m_startTime;
  MwbDouble m_stepSize;
  MwbInt32 m_timeTickCount;
};

/* External inputs (root inport signals) */
extern struct ol_cfunction_sysblockExtU ol_cfunction_sysblockGbIn;

/* External outputs (root outport signals) */
extern struct ol_cfunction_sysblockExtY rol_cfunction_sysblockGbOut;

/* Block states */
extern struct acfunction_sysblockDw l_cfunction_sysblockGbDw;

extern acfunction_sysblockEmd*const l_cfunction_sysblockGbMd;

void Step(void);
void Init(void);


#endif /* aCFUNCTION_SYSBLOCK_H */

/********************************************************************************
** end of file
********************************************************************************/
