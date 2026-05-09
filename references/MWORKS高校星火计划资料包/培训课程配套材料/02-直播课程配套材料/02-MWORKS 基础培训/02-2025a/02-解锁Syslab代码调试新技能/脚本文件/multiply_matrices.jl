# 计算多个矩阵的乘积
function multiply_matrices_test(matrices::Vector{Array{Float64}})
    result = matrices[1]
    for i in 2:length(matrices)
        result = result * matrices[i]
    end
    return result
end

# 定义矩阵A、B、C
A = [1.0 2.0; 3.0 4.0]
B = [5.0 6.0; 7.0 8.0]
C = [9.0; 10.0]
matrices = [A, B, C]
result = multiply_matrices_test(matrices)
