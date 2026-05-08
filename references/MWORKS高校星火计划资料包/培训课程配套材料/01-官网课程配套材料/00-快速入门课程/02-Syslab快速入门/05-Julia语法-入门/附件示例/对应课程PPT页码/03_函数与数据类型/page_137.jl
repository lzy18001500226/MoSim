abstract type Pointy{T} end
Pointy{Int64} <: Pointy
Pointy{1} <: Pointy
Pointy{Float64} <: Pointy{Real}
Pointy{Float64} <: Pointy{<:Real}



