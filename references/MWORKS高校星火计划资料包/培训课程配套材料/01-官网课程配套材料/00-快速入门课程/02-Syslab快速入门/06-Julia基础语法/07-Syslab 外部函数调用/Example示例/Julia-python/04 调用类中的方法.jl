
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

# 将路径添加到 python 工作目录中
println(@__DIR__) # f:\Syslab\MwSyslab\04 详细设计\Julia-python
_set_python_path(@__DIR__)

# 导入python文件
@pyimport myfunctions.myclass as myclass

# 调用python类中的方法
my_net = myclass.MyNet()
my_net.add(20) # 30


