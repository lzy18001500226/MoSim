using Libdl

# 加载库
lib_path = joinpath(@__DIR__, "ArrayMaker","libtest") # 用户库实际路径
lib = Libdl.dlopen(lib_path)

# 获取调用函数的符号
GetSum = Libdl.dlsym(lib, :GetSum)

# 调用函数
c = @ccall $GetSum(2::Cdouble, 3::Cdouble)::Cdouble

# ...

# 关闭dll
Libdl.dlclose(lib)

