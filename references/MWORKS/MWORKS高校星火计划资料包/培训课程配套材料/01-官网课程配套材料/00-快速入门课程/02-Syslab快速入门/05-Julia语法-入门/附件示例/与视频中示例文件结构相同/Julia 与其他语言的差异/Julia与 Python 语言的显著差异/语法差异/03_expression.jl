# 报错，if 关键词后不能使用非 Bool 类型变量
txt = "somthing"
if txt
  println("abc")
end
# ERROR: TypeError: non-boolean (String) used in boolean context
# 使用 !isempty(txt) 来表示字符串非空的条件
txt = "somthing"
if !isempty(txt)
  println("abc")
end



# 最后一个形参名 args 后加 ... 表示不定长参数 
function add(x, args...)
  res = 0
  for i in args
    res += i
  end
  return res + 2 * x
end
println(add(1, 2, 3, 4, 5)) # 16


# 关键词参数在 ; 之后
function mul(; x, y, kwargs...)
  z = 0
  if haskey(kwargs, :z)
    z = kwargs[:z]
  end
  return x + 2 * y + z
end
mul(y=2, x=1, z=1)
mul(y=2, x=1, z=1)
# 1 + 2*2 + 1 = 6

function func(x=rand())
  println(x)
end
# 两次运行 x 的值不相同
# 每次运行都会调用一次 rand()
func()
func()


# 匿名函数，() 内为形参
myf = (x) -> x + 1
myf(1) # 2


function func(x)
  # 使用 isa 判断 x 是否是 Int 类型
  if x isa Int
    println("Int")
  else
    println("not Int")
  end
end
func(1) # "Int"


# 定义可变结构体
mutable struct Foo
      baz::Int
      qux::Float64
end

# 创建实例
foo = Foo(23, 1.5)
# 不允许增加字段
foo.abc = 3
# ERROR: type Foo has no field abc


struct Bar end
# 定义两个方法实现
func(bar::Bar, y::Int) = 1
func(bar::Bar, y::String) = 2

# 根据所有参数的类型来派发
func(Bar(), 1)    # 1
func(Bar(), "abc") # 2

# 三元运算符
true ? 1 : 0 # 1


!false  # 取非， true
2^2  # 幂运算，4
3 ÷ 2  # 整除（使用\div<tab>输入），1
1 ⊻ 0  # 异或（使用\xor<tab>输入），1
7 % -2  # 取余，1

