using Statistics
function kurtosis_loop(X)
    E = 0.0
    S = 0.0
    n = length(X)
    mu = mean(X)
    @inbounds @simd for i in 1:n
        x = X[i]
        x2 = (x - mu)^2
        x4 = x2^2
        E += x4
        S += x2
    end
    E = E / n
    S = S / n
    return E / (S^2)
end
