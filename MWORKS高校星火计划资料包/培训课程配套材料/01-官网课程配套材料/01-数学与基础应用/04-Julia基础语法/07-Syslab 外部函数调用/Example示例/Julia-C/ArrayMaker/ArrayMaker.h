#ifndef ARRAYMAKER_H
#define ARRAYMAKER_H

#include "ArrayMaker_global.h"

struct ArrayMaker {
    int nNumber;  
    double* pArray;      
};

extern "C" ARRAYMAKER_EXPORT double GetSum(double x, double y);

extern "C" ARRAYMAKER_EXPORT ArrayMaker* CreateObj();
extern "C" ARRAYMAKER_EXPORT void DeleteObj(ArrayMaker ** ppobj); 
extern "C" ARRAYMAKER_EXPORT double* FillArray(ArrayMaker* pobj, int num, double value);
extern "C" ARRAYMAKER_EXPORT double* SetValue(ArrayMaker* pobj, int nth/*base-1*/, double value);
extern "C" ARRAYMAKER_EXPORT int GetValues(ArrayMaker * pobj, double* out, int len);
extern "C" ARRAYMAKER_EXPORT void encd1(int *a, int *b, int *c);

extern "C" ARRAYMAKER_EXPORT void SinglePrint();

////////////////////////////////////////////////////////////////

/* 
//struct ARRAYMAKER_EXPORT emxArray_real_T
//{
//    double* data;
//    int* size;
//    int allocatedSize;
//    int numDimensions;
//    boolean_T canFreeData;
//}; 

extern "C" ARRAYMAKER_EXPORT void* Mfsgolay(double order, double framelen);

extern "C" ARRAYMAKER_EXPORT double* GetData(void* p);

extern "C" ARRAYMAKER_EXPORT int* GetSize(void* p);

//extern "C" ARRAYMAKER_EXPORT int GetAllocatedSize(void* p);

extern "C" ARRAYMAKER_EXPORT int GetNumDimensions(void* p);
*/

#endif
