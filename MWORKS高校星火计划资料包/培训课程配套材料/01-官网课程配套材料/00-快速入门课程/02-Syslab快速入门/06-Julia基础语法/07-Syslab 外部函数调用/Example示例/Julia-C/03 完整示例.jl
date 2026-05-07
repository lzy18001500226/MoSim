using Libdl

# 加载dll
lib_path = joinpath(@__DIR__, "ArrayMaker", "libtest")
lib = Libdl.dlopen(lib_path)

# 获取符号
CreateObj = Libdl.dlsym(lib, :CreateObj)
DeleteObj = Libdl.dlsym(lib, :DeleteObj)
FillArray = Libdl.dlsym(lib, :FillArray)

# 创建对象指针
pobj = @ccall $CreateObj()::Ptr{Cvoid}

# 填充数组
len = 5
parr = @ccall $FillArray(pobj::Ptr{Cvoid}, len::Cint, 3.5::Cdouble)::Ptr{Cdouble}
arr = [unsafe_load(parr, i) for i = 1:len]
#=
5-element Vector{Float64}:
 3.5
 3.5
 3.5
 3.5
 3.5
=#

# 销毁对象
@ccall $DeleteObj(Ref(pobj)::Ptr{Ptr{Cvoid}})::Cvoid
pobj = C_NULL

# 关闭dll
Libdl.dlclose(lib)