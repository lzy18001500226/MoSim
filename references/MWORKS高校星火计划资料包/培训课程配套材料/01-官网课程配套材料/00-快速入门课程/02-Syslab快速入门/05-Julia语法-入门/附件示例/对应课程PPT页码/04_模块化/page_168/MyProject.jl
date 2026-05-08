module MyProject
export my_sum
function my_sum(first::Integer, last::Integer)
    if first > last
        return 0
    end
    return div((first + last) * (last - first + 1), 2)
end
end# module MyProject





