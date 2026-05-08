struct Data1
    x::Float64
    y::String
end

Base.@kwdef struct Data2{T}
    x::T
    y::String = "default"
end

mutable struct Data3{T}
    x::T
    y::String
end



