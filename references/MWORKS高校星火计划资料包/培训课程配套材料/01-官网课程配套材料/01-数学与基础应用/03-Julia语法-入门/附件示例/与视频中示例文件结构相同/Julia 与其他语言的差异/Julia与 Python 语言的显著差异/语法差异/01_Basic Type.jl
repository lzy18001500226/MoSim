# 字符串
S = "text"
# 字符
C = 'c'
# 报错，''只能包含单个字符
C = 'text'
#=
ERROR: syntax: character literal contains multiple characters
=#


# 字符串拼接
S = "text" * "123" # "text123"
# 字符串重复 3 次
S = "ab"^3 # "ababab"


# 默认为 32/64 位整数类型
typeof(2) # Int64

# 整数运算溢出
2^64 # 0

# 如果需要可使用 BigInt
big(2)^64 # 18446744073709551616


# 使用 Any 作为容器的元素类型会降低 Julia 代码的运行速度
# 在使用前请确认容器是否真的需要存储不同类型的元素
# 创建可存储任意元素的列表
list = Any[1, "abc", 2.1] # 往列表内添加元素
push!(list, "text")
# 创建可存储任意元素的字典
dict = Dict{String,Any}(
    "a" => 1, "b" => "abc")


x = nothing
 # 使用 !isnothing(x) 来判断值是不是 nothing
if !isnothing(x)
  println("abc")
end


