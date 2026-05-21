# page 16
a = "Hello, World" # 定义变量
# "Hello, World"

a   # 展示变量
# Hello, World

function f(x, y)       # 定义函数
    return x + y
end

for i = 1:10             # 执行循环语句
    a = i * 2
    print(a)
end

# page 17
x = 1
for i in 1:10
    x += i
end
x

x = 1
for i in 1:10
    # 触发错误，x未定义
    x += i
end

x = 1
for i in 1:10
    # 显式声明全局变量
    global x
    x += i
end
println(x)

# page 20
function compute_area(length, width)
    area = length + width
    println("The area is $area")
end

# page 21
test = 1
