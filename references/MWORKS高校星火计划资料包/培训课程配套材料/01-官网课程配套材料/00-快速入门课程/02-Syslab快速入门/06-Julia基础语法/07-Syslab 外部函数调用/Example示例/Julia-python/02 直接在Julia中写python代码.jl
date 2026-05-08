module MyModule
using PyCall

function __init__()
    py"""
    def hello(s):
        return "Hello, " + s
    """
end

# 封装Python函数
hello(s) = py"hello"(s)
end

MyModule.hello("julia") 
# "hello julia"

using PyCall

# 直接嵌入python代码
py"""
str = "3 * 4 + 5"
a = compile(str,'','eval')
print("a =", eval(a)) 
"""
# a = 17