function foo(a, b)
    a + b, a * b
end
# foo (generic function with 1 method)

# 如果您在交互式会话中调用它，而没有在任何地方分配返回值，您将看到元组返回:
foo(2, 3)
# (5, 6)

# 将每个值提取到一个变量中:
x, y = foo(2, 3)

x
# 5

y
# 6
