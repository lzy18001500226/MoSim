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
    def _setup_add(mod, jl_func):
        mod.JuliaAPI.add = jl_func

    def _setup_multiply(mod, jl_func):
        mod.JuliaAPI.multiply = jl_func
    """

    py"_setup_add"(app_module, my_add)
    py"_setup_multiply"(app_module, my_multiply)
end

_set_python_path(@__DIR__)

function run()
    myapp = pyimport("myfunctions.myapp")
    setupapp(myapp)
    myapp.test()
end
