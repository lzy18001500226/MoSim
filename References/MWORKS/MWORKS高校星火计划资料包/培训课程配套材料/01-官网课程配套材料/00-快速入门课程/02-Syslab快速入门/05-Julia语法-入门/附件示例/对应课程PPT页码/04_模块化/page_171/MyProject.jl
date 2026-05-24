module MyProject
export my_sum

"""
##  my_sum

my_sum(first, last)

计算 [first, last] 之间的所有整数的求和
"""
function my_sum(first::Integer, last::Integer)
    if first > last
        return 0
    end
    return div((first + last) * (last - first + 1), 2)
end

end


