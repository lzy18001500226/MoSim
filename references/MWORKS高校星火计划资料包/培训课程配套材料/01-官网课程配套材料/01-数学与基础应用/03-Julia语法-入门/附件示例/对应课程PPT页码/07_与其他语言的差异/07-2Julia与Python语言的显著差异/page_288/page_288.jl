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




