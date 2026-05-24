# 计算多个矩阵的乘积
function multiply_matrices_test(matrices::Vector{Array{Float64}})
    result = matrices[1]
    for i in 1:length(matrices)
        result = result * matrices[i]
    end
    return result
end