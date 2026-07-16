/********************************************************************************
 * Copyright (C) 2005-2026, Suzhou Tongyuan Software&Control Technology Co.,Ltd.
 * All rights reserved.
 * 版权所有 (C) 2005-2026， 苏州同元软控技术股份有限公司
 * 保留所有权利。
 *
 * 该文件由MWORKS内核代码生成器自动生成。
 *
 * 文件名称: mwb_main.c
 * 生成时间: 2026-07-16 14:13:22
 *
********************************************************************************/

#include "MoSim_PID_Unified_Graphical_Sysblock.h"

/**
  * @brief  Main function
  * @param  None.
  * @retval 0 if succeeds; -1 if error.
  */
MwbInt main(void)
{

    MwbInt i = 0;              /* circle index in the for-loop */
    MwbInt circleNumber = (MwbInt)(50.5); /* variable that control the total number of cycles */


    /* BEGIN: assign value to the input variables of the model */

    /* END:   assign value to the input variables of the model */


    /* initialize the model */
    Init();


    /* BEGIN: use output variables of the model,
              such as printing them out or assigning them to other variables */

    /* END:   use output variables of the model,
              such as printing them out or assigning them to other variables */


    for(;i < circleNumber; ++i)
    {
        /* BEGIN: assign value to the input variables of the model */

        /* END:   assign value to the input variables of the model */



        /* perform a simulation step */
        Step();


        /* BEGIN: use output variables of the model,
                  such as printing them out or assigning them to other variables */

        /* END:   use output variables of the model,
                  such as printing them out or assigning them to other variables */
    }


    return 0;
}

/********************************************************************************
** end of file
********************************************************************************/
