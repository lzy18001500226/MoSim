# while for 
i = 1;
while i <= 5
    println(i)
    global i += 1
end

for i = 1:5
    println(i)
end

# break
while true
    println(i)
    if i >= 5
        break
    end
    global i += 1
end

for j = 1:1000
    println(j)
    if j >= 5
        break
    end
end

# continue
i = 1
while i <= 10
    global i += 1
    if i % 3 != 0
        continue
    end
    println(i)
end

for i = 1:10
    if i % 3 != 0
        continue
    end
    println(i)
end


# in, ∈
for i in [1, 4, 0]
    println(i)
end

for s ∈ ["foo", "bar", "baz"]
    println(s)
end

# 嵌套迭代合并到一个外部循环
for i = 1:2, j = 3:4
    println((i, j))
end


