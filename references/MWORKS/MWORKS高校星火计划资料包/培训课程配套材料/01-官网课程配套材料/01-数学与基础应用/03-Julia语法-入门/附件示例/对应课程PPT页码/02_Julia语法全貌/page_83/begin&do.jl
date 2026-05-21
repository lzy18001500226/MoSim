# 定义一个数组
numbers = [1, 2, 3, 4, 5]

# 使用 `do` 结构和 `map` 函数来对数组中的每个元素加倍
doubled_numbers = map(numbers) do number
    2 * number
end

# 使用 `begin` 和 `end` 来定义一个更复杂的代码块
total = begin
    su = 0
    for num in doubled_numbers
        global su += num
    end
    su  # 返回总和
end

println("原始数字: ", numbers)
println("加倍后的数字: ", doubled_numbers)
println("数字总和: ", total)



