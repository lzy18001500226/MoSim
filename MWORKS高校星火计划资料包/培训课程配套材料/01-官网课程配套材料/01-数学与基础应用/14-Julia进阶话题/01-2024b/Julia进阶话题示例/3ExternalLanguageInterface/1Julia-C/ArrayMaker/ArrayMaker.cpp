#include "ArrayMaker.h"
#include <math.h>

using namespace std;

ArrayMaker* CreateObj()
{
    auto p = new ArrayMaker;
    p->nNumber = 0;
    p->pArray = nullptr;
    return p;
}

void DeleteObj(ArrayMaker** ppobj)
{
    if (ppobj == nullptr) {
        return;
    }

    auto& pobj = *ppobj;
    if (pobj != nullptr) {

        //删除数据
        if (pobj->pArray != nullptr) {
            delete[] pobj->pArray;
            pobj->pArray = nullptr;
        }

        //删除本身
        delete pobj;
        pobj = nullptr;
    }
}

double* FillArray(ArrayMaker* pobj, int num, double value)
{
    double* data = nullptr;

    if (pobj != nullptr) {
        
        data = pobj->pArray;
        if (data != nullptr)
        {
            delete[] data;
        }

        data = new double[num];
        for (int i = 0; i < num; i++)
        {
            data[i] = value;
        }
        pobj->pArray = data; 
        pobj->nNumber = num;
    }

    return data;
}