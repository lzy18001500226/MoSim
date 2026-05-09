# 查找标准库函数的定义
@which sqrt(4)

# 查找用户定义函数的定义
# 定义一个简单的函数
function add(a, b)
    return a + b
end

# 使用 @which 查找函数定义
@which add(1, 2)
