struct Point{T} <: Pointy{T}
    x::T
    y::T
end
Point{Float64} <: Pointy{Float64}
Point{Real} <: Pointy{Real}
Point{Float64} <: Pointy{Real}
Point{Float64} <: Pointy{<:Real}



