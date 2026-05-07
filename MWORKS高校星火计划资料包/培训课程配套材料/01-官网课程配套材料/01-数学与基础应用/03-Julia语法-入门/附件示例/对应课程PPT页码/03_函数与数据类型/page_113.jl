a = Array{Float64}(undef, 2, 1)
using LinearAlgebra
b = Matrix(I, 2, 3)
c = trues(1, 3)
d = rand(1, 3)
e = range(1, 3, 3)
f = range(1, step=1, length=2)
[f;] #还可以使用[f…]


