using TyMath
A = magic(3);
# 公式：A*X = det(A)*eye(n) = X*A
X = det(A) * inv(A)
#=
3×3 Matrix{Float64}:
-53.0  52.0 -23.0
 22.0  -8.0 -38.0
 7.0 -68.0  37.0
=#



