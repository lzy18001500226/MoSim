include("Identifier.jl")

# 创建一个 Identifier 实例
id = Identifier(0x1234)

# 获取 Identifier 的原始值
println("Identifier value: ", value(id))
