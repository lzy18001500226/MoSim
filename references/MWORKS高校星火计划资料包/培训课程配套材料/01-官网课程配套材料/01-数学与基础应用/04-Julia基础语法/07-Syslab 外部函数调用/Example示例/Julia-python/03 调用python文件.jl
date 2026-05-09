#
# 该示例演示了如何集成并调用python文件
#

using PyCall

function _set_python_path(path::AbstractString)
    py"""
    import sys
    def set_path(path):
        if path not in sys.path:
            sys.path.append(path)
    """
    py"set_path"(path)
end

# 1. 将路径添加到python工作目录中
println(@__DIR__) 
_set_python_path(@__DIR__)

# 查看sys.path
pyimport("sys").path

# 2. 导入python文件 
@pyimport myfunctions.function as myfunc

# 3. 调用python接口
myfunc.Test("Syslab") # Hello, Syslab 
