struct Data1
    x::Float64
    y::String
end

d1 = Data1(1.2, "str")
# Data1(1.2, "str")

d1.x = 2.4

mutable struct Data2
    x::Float64
    y::String
end

d2 = Data2(1.2, "str")
# Data2(1.2, "str")

d2.x = 2.4;

d2
# Data2(2.4, "str")
