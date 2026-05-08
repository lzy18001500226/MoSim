using BenchmarkTools

# v1
function kurtosis(A)
    mean(abs.(A) .^ 4) / (mean(abs.(A) .^ 2))^2
end

# v2
function kurtosis(A)
    tmp = abs2.(A)
    mean(tmp .^ 2) / mean(tmp)^2
end

# v3
function kurtosis(A)
    mean(abs4, A) / mean(abs2, A)^2
end

# v4
function kurtosis(A)
    E = zero(Float64)
    S = zero(Float64)
    @inbounds @simd for i in eachindex(A)
        x = A[i]
        x2 = abs2(x)
        x4 = abs2(x2)
        E += x2
        S += x4
    end
    return E * length(A) / S^2
end

A = rand(10240)
@btime kurtosis(A);
