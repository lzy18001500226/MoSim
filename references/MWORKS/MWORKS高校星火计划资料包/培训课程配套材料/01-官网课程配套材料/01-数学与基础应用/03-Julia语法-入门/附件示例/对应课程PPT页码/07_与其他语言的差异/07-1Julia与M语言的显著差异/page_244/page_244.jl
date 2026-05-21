# 不可变结构体
struct Foo
  baz::Int
  qux::Float64
end
# 创建实例
foo = Foo(23, 1.5)
# 不允许修改
foo.qux = 2.0
# ERROR: setfield!: immutable struct of type Foo cannot be changed


# 可变结构体
mutable struct Bar
  baz::Int
  qux::Float64
end

# 创建实例bar = Bar(23, 1.5);
# 允许修改
bar.qux = 2.0



