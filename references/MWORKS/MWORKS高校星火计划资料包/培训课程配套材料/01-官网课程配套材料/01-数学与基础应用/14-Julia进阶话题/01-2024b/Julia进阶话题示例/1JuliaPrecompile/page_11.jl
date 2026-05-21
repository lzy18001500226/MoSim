function count_number(A::AbstractArray)
    rst = 0
    for x in A
        if smaller_than_5(x)
        rst += 1
        elseif larger_than_6(x)
        rst += 1
        end
    end
    return rst
end
smaller_than_5(x)  =  x < 5
larger_than_6(x)  =  x > 6
count_number([1, 2, 3])
methodinstances( count_number )
methodinstances( smaller_than_5 )
methodinstances( larger_than_6 )


