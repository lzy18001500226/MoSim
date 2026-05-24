x = 1

for i in 1:10
    x = i
end

x = 1

for i in 1:10
    # 显式声明全局变量
    global x
    x = i
end

println(x)







