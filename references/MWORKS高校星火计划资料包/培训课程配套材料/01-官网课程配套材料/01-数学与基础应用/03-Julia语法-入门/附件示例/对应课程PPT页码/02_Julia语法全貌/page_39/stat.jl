function stat(x)
    n = length(x)
    m = sum(x) / n
    s = sqrt.(sum((x .- m) .^ 2 / n))
    return m, s
end



