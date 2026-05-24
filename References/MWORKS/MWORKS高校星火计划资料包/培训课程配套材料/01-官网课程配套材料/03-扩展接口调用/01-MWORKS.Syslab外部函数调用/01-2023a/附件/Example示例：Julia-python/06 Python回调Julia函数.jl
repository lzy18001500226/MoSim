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

function my_add(xs::AbstractArray)
    return +(xs...)
end

function my_multiply(xs::AbstractArray)
    return *(xs...)
end

function setupapp(app_module::PyObject)
    py"""    
def _setupapp_add(mod, jl_func):
    mod.JuliaAPI.add = jl_func
def _setupapp_multiply(mod, jl_func):
    mod.JuliaAPI.multiply = jl_func
    """

    # 注册Julia函数
    py"_setupapp_add"(app_module, my_add)
    py"_setupapp_multiply"(app_module, my_multiply)
end

_set_python_path(@__DIR__)

function run()
    # 导入app
    myapp = pyimport("myfunctions.myapp")
    
    # 初始化app
    setupapp(myapp)

    # 执行app
    myapp.test()
end

# 热启动：修改python文件，无需重启REPL
function reload_myapp()
    py"""
from importlib import reload
import myfunctions.myapp as myapp
reload(myapp)
    """
end