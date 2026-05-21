function mysum(pairs)
    r1, r2 = 0.0, 0.0
    @simd for p in pairs
        r1 += p[1]
        r2 += p[2]
    end
    return r1, r2

end
pairs = [(rand(), rand()) for _ in 1:1024];
pairs = [[rand(), rand()] for _ in 1:1024];


#2
function mysum(pairs)
    r1, r2 = 0.0, 0.0
    @simd for p in pairs
        r1 += p.first

        r2 += p.second
    end
    return r1, r2
end

pairs = [(; first=rand(), second=rand()) for _ in 1:1024];

#3

function mysum(pairs)
    r1, r2 = 0.0, 0.0
    @simd for p in pairs
        r1 += p[:first]

        r2 += p[:second]
    end
    return r1, r2
end

pairs = [Dict(:first=>rand(), :second=>rand()) for _ in 1:1024];