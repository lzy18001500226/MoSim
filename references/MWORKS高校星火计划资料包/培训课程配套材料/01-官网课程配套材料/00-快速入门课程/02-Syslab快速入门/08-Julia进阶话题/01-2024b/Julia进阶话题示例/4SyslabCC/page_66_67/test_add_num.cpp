#include <iostream>
#include <stdint.h>
#include "libadd.h"
int main()
{
    double af = 1.2;
    double bf = 2.4;
    std::cout << "add_num_f64(a = 1.2, b = 2.4) = " << add_num_f64(af, bf) << std::endl;
    int64_t al = 2;
    int64_t bl = 4;
    std::cout << "add_num_i64(a = 2, b = 4) = " << add_num_i64(al, bl) << std::endl;
    return 0;
}
