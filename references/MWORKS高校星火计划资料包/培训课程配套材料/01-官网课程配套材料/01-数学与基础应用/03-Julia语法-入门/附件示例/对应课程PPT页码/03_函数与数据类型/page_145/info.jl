# 基本信息日志
@info "Starting the process"

# 带有变量的日志
x = 42
@info "The value of x is" x

# 带有上下文信息的日志
y = 100
@info "Calculating sum" value1 = x value2 = y result = (x + y)

# 在函数中使用 @info
function add_and_log(a, b)
    result = a + b
    @info "Adding numbers" a = a b = b result = result
    return result
end
sum = add_and_log(5, 7)



