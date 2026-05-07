#include <julia.h>
JULIA_DEFINE_FAST_TLS // only define this once, in an executable (not in a shared library) if you want fast code.

int main(int argc, char *argv[])
{
    jl_init();
    jl_eval_string("print(sqrt(2.0))");
    jl_atexit_hook(0);
    return 0;
}