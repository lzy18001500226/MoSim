#=
语法：
  ccall((函数名, 库名), 返回类型, (参数1类型, 参数2类型...), 参数值1, 参数值2...)
  ccall((function_name, library), returntype, (argtype1, ...), argvalue1, ...)
  ccall(function_name, returntype, (argtype1, ...), argvalue1, ...)
  ccall(function_pointer, returntype, (argtype1, ...), argvalue1, ...)
=#

path = ccall(:getenv, Cstring, (Cstring,), "PATH") # 注：函数名前面加冒号表示symbol类型
# Cstring(0x00007ffe6bb46a81)

unsafe_string(path)#Copy a string from the address of a C-style，表示从C地址中取字符串值
# "/usr/local/share/TongYuan/julia-1.9.3/bin:/usr/local/share/TongYuan/julia-1.9.3/lib:/usr/local/share/TongYuan/julia-1.9.3/lib/julia:/usr/bin:/usr/local/share/TongYuan/.julia/miniforge3:/usr/local/share/TongYuan/.julia/miniforge3/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

#= 
@ccall 的定义如下：
@ccall library.function_name(argvalue1::argtype1, ...)::returntype
@ccall function_name(argvalue1::argtype1, ...)::returntype
@ccall $function_pointer(argvalue1::argtype1, ...)::returntype
 =#

path = @ccall getenv("PATH"::Cstring)::Cstring
# Cstring(0x00007ffe6bb46a81)

unsafe_string(path)
# "/usr/local/share/TongYuan/julia-1.9.3/bin:/usr/local/share/TongYuan/julia-1.9.3/lib:/usr/local/share/TongYuan/julia-1.9.3/lib/julia:/usr/bin:/usr/local/share/TongYuan/.julia/miniforge3:/usr/local/share/TongYuan/.julia/miniforge3/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
