# 定义一个 16 位的原始类型 Identifier
primitive type Identifier 16 end

# 定义一个函数来创建 Identifier 实例
function Identifier(value::UInt16)
    return reinterpret(Identifier, value)
end

# 定义函数来获取 Identifier 的原始值
function value(id::Identifier)
    return reinterpret(UInt16, id)
end
