/********************************************************************************
 * Copyright (C) 2005-2026, Suzhou Tongyuan Software&Control Technology Co.,Ltd.
 * All rights reserved.
 * 版权所有 (C) 2005-2026， 苏州同元软控技术股份有限公司
 * 保留所有权利。
 *
 * 该文件由MWORKS内核代码生成器自动生成。
 *
 * 文件名称: PX4CTRL_Core_CFunction_Sysblock.h
 * 生成时间: 2026-06-29 09:26:55
 *
********************************************************************************/

#ifndef CK_H
#define CK_H

#ifndef FUNCTION_SYSBLOCK_COMMON_INCLUDES_
#define FUNCTION_SYSBLOCK_COMMON_INCLUDES_
#include "mwb_types.h"
#include "math.h"
#endif /* FUNCTION_SYSBLOCK_COMMON_INCLUDES_ */

typedef struct blockTagEmd ckEmd;

struct blockTagEmd{
  MwbDouble m_curTime;
  MwbDouble m_startTime;
  MwbDouble m_stepSize;
  MwbInt32 m_timeTickCount;
};

/* External inputs (root inport signals) */
extern struct lockExtU lockGbIn;

/* External outputs (root outport signals) */
extern struct lockExtY blockGbOut;

/* Block states */
extern struct ckDw ockGbDw;

extern ckEmd*const ockGbMd;

void Step(void);
void Init(void);


#endif /* CK_H */

/********************************************************************************
** end of file
********************************************************************************/
