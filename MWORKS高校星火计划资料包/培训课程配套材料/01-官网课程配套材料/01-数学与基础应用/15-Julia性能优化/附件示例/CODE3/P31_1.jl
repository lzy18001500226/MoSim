#基于 Float64 封装的自定义数值类型

struct MyFloat64 <: AbstractFloat
    x::Float64
end
Base.:(+)(a::MyFloat64, b::MyFloat64) = MyFloat64(a.x + b.x)

A = [MyFloat64(rand()) for i in 1:1024, j in 1:1024];




