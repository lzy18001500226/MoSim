using MethodAnalysis
function count_number(A::AbstractArray)
rst = 0
    for x in A
        if is_positive(x)
        rst += 1
        end
    end
return rst
end
is_positive(x) = x > 0
count_number(Bool[1, 0, 1])
methodinstances(count_number )
methodinstances( is_positive )
is_positive(x::Bool) = x
count_number(Bool[1, 0, 1])
methodinstances( is_positive )
methodinstances( count_number )

mi=methodinstances(is_positive)
mi[1].def
mi[2].def


