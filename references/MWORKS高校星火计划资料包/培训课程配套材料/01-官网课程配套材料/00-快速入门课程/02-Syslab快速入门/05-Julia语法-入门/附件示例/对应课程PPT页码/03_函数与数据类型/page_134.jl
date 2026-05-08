Array{String} <: Array

Array{Int} <: Array

function mynorm1(p::Array{Real})
    sqrt.(p)
end

function mynorm2(p::Array{<:Real})
    sqrt.(p)
end



