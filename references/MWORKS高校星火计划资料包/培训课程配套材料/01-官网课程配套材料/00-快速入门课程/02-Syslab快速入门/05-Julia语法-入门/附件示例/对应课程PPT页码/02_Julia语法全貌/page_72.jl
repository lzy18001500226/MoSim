[1, 2, 3] # 元素类型为 Int 的向量
promote(1, 2.3, 4 // 5) # Int, Float64 以及 Rational 类型放在一起则会提升到 Float64
[1, 2.3, 4 // 5] # 从而Float64就是这个数组的元素类型
[]



