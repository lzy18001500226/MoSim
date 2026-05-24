# 声明一个全局变量
global counter = 0

# 定义一个函数，演示局部变量和全局变量的使用
function increment()
    # 声明使用外部的全局变量
    global counter
    counter += 1

    # 声明一个局部变量
    local temp = 5

    # 对局部变量进行操作
    temp += 3
    println("局部变量 temp 的值: ", temp)
end

# 调用函数
increment()

println("全局变量 counter 的值: ", counter)
# 1

# 在循环中使用局部和全局变量
for i in 1:3
    # 修改全局变量
    global counter += 1
end

println("循环后的全局变量 counter 的值: ", counter)
# 4



