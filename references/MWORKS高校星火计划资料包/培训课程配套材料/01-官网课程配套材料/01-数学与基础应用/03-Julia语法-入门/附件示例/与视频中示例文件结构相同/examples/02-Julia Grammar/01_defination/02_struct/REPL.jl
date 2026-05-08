include("my_struct.jl")

d1 = Data1(1.2, "str")
Data1(1.2, "str")

d2 = Data2{Float64}(x=1.2)
Data2{Float64}(1.2, "default")

d3 = Data3{Float64}(1.2, "str")
Data3{Float64}(1.2, "str")

d3.x = 2.4;
d3
Data3{Float64}(2.4, "str")

d2.x = 2.4