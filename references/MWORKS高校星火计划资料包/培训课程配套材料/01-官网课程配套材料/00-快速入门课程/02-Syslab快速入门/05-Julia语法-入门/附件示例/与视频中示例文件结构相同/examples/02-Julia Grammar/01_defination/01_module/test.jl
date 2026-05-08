include("my_module.jl")
# 使用全名
@show ModuleA.add1(10)
# 导入模块符号
using .ModuleB
@show my_hypot(3, 4)


