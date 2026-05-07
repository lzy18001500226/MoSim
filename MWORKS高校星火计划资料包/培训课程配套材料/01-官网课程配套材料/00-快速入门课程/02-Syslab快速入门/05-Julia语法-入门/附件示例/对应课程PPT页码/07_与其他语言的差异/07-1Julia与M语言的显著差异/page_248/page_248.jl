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



