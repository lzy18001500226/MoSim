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

@code_warntype mymax_stable(1.5, 2)