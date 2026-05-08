struct DiagPoint{T} <: Pointy{T}
    x::T
end
calculate(a::Pointy, b::Pointy) = abs(a.x) - abs(b.x) > 0 ? b.x : a.x
calculate(Point(1, 2), DiagPoint(2))
calculate(Point(1, 2), Point(0, 1))
calculate(DiagPoint(3), DiagPoint(2))



