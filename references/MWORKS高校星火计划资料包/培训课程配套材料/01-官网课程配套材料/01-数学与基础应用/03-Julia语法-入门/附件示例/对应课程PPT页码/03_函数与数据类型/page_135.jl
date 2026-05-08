struct Point{T}
    x::T
    y::T
end
p = Point{Float64}(1.0, 2.0)
typeof(p)

Point{Float64}(1.0)


