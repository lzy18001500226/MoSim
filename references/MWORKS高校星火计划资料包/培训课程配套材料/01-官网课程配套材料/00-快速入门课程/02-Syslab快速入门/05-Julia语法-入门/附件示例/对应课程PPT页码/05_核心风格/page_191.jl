function mymax(a, b)
    if a > b
        return a
    else
        return b
    end
end

function mymax_stable(a, b)
    a_, b_ = promote(a, b)
    if a_ > b_
        return a_
    else
        return b_
    end
end

A = rand(Float64, 64, 64);
B = rand(0:1, 64, 64);
@btime mymax(A[1], B[1]);
@btime mymax_stable(A[1], B[1]);
@btime sum(mymax.(A, B));
@btime sum(mymax_stable.(A, B));