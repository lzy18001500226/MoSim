function f(x, y)
    x + y
end
# f (generic function with 1 method)
f(1, 2)
# 3


# 与许多其他语言中一样，return 关键字会导致函数立即返回，提供一个返回值的表达式:
function g(x, y)
    return x + y
    x * y
end
g(1, 2)
# 3

