struct Foo
    bar
    baz::Int
    qux::Float64
end
foo1 = Foo("Hello, world.", 23, 1.5) # 该构造函数接受与字段类型完全匹配的参数
foo2 = Foo("Hello, world.", 23.0, 1) # 该构造函数调用 Convert 将对应的参数转换为对应的字段类型



