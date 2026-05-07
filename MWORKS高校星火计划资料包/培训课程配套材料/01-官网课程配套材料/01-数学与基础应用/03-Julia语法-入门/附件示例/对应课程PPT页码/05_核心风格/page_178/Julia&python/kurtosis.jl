# Julia 的 kurtosis 实现
using Statistics
function kurtosis(X)
    mu = mean(X)
    n = length(X)
    tmp = (X .- mu) .^ 2
    # 对 tmp 中的每个元素求平方并求和，它等价于 sum(tmp.^2) 但是会更高效
    fourth_moment = sum(abs2, tmp) / n
    second_moment = sum(tmp) / n
    return fourth_moment / (second_moment^2)
end
