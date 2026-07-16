/********************************************************************************
 * Copyright (C) 2005-2026, Suzhou Tongyuan Software&Control Technology Co.,Ltd.
 * All rights reserved.
 * 版权所有 (C) 2005-2026， 苏州同元软控技术股份有限公司
 * 保留所有权利。
 *
 * 该文件由MWORKS内核代码生成器自动生成。
 *
 * 文件名称: mwb_types.h
 * 生成时间: 2026-07-16 15:58:49
 *
********************************************************************************/

#ifndef MWB_TYPES_H
#define MWB_TYPES_H

#include <stddef.h>

#define MWB_SUPPORT_LONGLONG


/* Logical type definitions */
#if (!defined(__cplusplus))
#ifndef true
#define true (1U)
#endif

#ifndef false
#define false (0U)
#endif
#endif

#define MwbNull 0
#define maxInt8T ((char)(127))
#define minInt8T ((char)(-127-1))
#define maxUInt8T ((unsigned char)(255U))
#define maxInt16T ((short)(32767))
#define minInt16T ((short)(-32767-1))
#define maxUInt16T ((unsigned short)(65535U))
#define maxInt32T ((int)(2147483647))
#define minInt32T ((int)(-2147483647-1))
#define maxUInt32T ((unsigned int)(0xFFFFFFFFU))
#define maxUInt64T ((unsigned long long)(0xFFFFFFFFFFFFFFFFULL))

typedef char MwbChar;
typedef char* MwbString;
typedef int MwbInt;
typedef unsigned int MwbUInt;
typedef float MwbFloat;
typedef double MwbDouble;
typedef unsigned char MwbBool;
typedef size_t MwbSize;
typedef char MwbInt8;
typedef unsigned char MwbUInt8;
typedef short MwbInt16;
typedef unsigned short MwbUInt16;
typedef int MwbInt32;
typedef unsigned int MwbUInt32;
#ifdef MWB_SUPPORT_LONGLONG
typedef long long MwbInt64;
typedef unsigned long long MwbUInt64;
#endif


#endif /* MWB_TYPES_H */

/********************************************************************************
** end of file
********************************************************************************/
