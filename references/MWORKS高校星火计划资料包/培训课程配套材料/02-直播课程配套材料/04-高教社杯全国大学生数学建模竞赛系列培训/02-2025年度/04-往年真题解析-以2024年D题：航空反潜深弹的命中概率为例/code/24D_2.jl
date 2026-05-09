using TyStatistics
include("24D_2_1.jl")
include("24D_2_2.jl")
include("24D_2_3.jl")
include("24D_2_4.jl")

I1 = sum(x2())
I2 = sum(x3())
I3 = sum(x4())
I4 = sum(x5())

I =vcat(I4[1, 2:end], I3[1, 2:end], I2[1, 2:end], I1[1, 2:end])
d = vcat(collect(87.5:1:100),collect(100:1:140-1),collect(140:1:152.5),collect(152.5:1:180))
plot(d, I)