# 比较运算符
a = [1, 3, 5, 7, 9]
b = [1, 3, 5, 7, 9]

# 数组判等
a == b
# true

# 数组元素判等（向量化操作）
a .== b
# Bool[1, 1, 1, 1, 1]


# ok：需要向量化操作
a .> 3
# Bool[0, 0, 1, 1, 1]


# 按位取反
~4 # -5

# 按位与
4 & 10 # 0
4 & 12 # 4

# 按位或
4 | 10 # 14
4 | 1 # 5

# 按位异或
xor(4, 7) # 3


# ... 运算符
# 用法1：将多个参数组合成一个参数
function printargs(args...)
  println(typeof(args))
  for (i, arg) in enumerate(args)
    println("Arg #$i = $arg")
  end
end
printargs(10, 20, 30)
#=
Tuple{Int64, Int64, Int64}
Arg #1 = 10
Arg #2 = 20
Arg #3 = 30
=#

# 用法2：将一个参数分解成多个不同参数
function threeargs(a, b, c)
  println("a = $a::$(typeof(a))")
  println("b = $b::$(typeof(b))")
  println("c = $c::$(typeof(c))")
end
x = [1, 2, 3]
threeargs(x...)
#=
a = 1::Int64
b = 2::Int64
c = 3::Int64
=#

# Julia没有续行符
y = 1 +
    2 +
    4
# 7

# 运算符优先级
# Julia中，^是右结合
4^3^2 # 等价于 4^(3^2)
# 262144
(4^3)^2
# 4096
