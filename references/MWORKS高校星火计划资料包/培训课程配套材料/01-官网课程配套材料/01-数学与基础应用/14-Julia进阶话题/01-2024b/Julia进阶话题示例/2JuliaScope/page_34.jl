function sum_to_def(n)
    s = 0 # new local
    for i = 1:n
        t = s + i # new local `t`
        s = t # assign existing local `s`
    end
    return s, @isdefined(t)
end
sum_to_def(1)
