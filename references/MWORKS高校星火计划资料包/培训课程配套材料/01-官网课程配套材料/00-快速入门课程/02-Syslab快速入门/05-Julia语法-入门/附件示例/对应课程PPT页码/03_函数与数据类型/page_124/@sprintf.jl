using Printf

# 格式化整数
num = 42
formatted_str = @sprintf("Integer: %d", num)
println(formatted_str)  # 输出: "Integer: 42"

# 格式化浮点数
flt = 3.14159
formatted_str = @sprintf("Float: %.2f", flt)
println(formatted_str)  # 输出: "Float: 3.14"

# 格式化字符串
name = "Alice"
formatted_str = @sprintf("Name: %s", name)
println(formatted_str)  # 输出: "Name: Alice"
