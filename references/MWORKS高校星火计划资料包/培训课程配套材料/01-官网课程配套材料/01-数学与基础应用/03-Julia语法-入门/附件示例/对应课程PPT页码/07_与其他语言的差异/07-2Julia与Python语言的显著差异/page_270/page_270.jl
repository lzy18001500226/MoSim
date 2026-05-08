# 使用 Any 作为容器的元素类型会降低 Julia 代码的运行速度
# 在使用前请确认容器是否真的需要存储不同类型的元素
# 创建可存储任意元素的列表
list = Any[1, "abc", 2.1] # 往列表内添加元素
push!(list, "text")
# 创建可存储任意元素的字典
dict = Dict{String,Any}(
    "a" => 1, "b" => "abc")






