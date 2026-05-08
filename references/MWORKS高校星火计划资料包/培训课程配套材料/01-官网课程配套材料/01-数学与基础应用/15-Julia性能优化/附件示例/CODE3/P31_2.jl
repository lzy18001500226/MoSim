#可变结构体的性能显著

mutable  struct My_1Float64 <: AbstractFloat
    x::Float64
end
Base.:(+)(a::My_1Float64, b::MyFloat64) = My_1Float64(a.x + b.x)

A = [My_1Float64(rand()) for i in 1:1024, j in 1:1024];