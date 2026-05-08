# 定义一些变量
a = 10

# 使用 @show 打印变量的值
@show a

# 计算并打印表达式的结果
result = a + 5
@show result

# 在函数中使用 @show
function add_and_show(x, y)
    result = x + y
    @show result  # 打印 result 的值
    return result
end

sum = add_and_show(5, 7)
