#
# 直接在Julia中写python代码
# 

module MyModule
using PyCall

function __init__()
    py"""
    def hello(s):
        return "Hello, " + s
    """
end

# 调用python函数
hello(s) = py"hello"(s)
end

MyModule.hello("Syslab") # "Hello, Syslab"


# 直接嵌入python代码
py"""
str = "3 * 4 + 5"
a = compile(str,'','eval')
print("a =", eval(a)) 
# a = 17
"""

