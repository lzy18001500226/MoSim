module MyPkg

fast_mode() = get(ENV, "FAST_MODE")

end
methodinstances(MyPkg.fast_mode)
module MyPkg

f(x)  =  x  +  2 

end
methodinstances(MyPkg.f)
# module MyPkg

# fast_mode()  =  get(ENV, "FAST_MODE")

# # 顶层模块执行触发  fast_mode  的预编译
# if fast_mode()
#    # do something
# else
#    # do something else
# end

# end

# methodinstances(MyPkg.fast_mode)
module MyPkg

f(x)  =  x  +  2 


# 主动告诉 Julia 预编译
# f(::Int) 与 f(::Float64) 方法
precompile(f, (Int, ))
precompile(f, (Float64, ))

end
methodinstances(MyPkg.f)
