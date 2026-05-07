function mymax(a, b)
    if a > b
        return a
    else
        return b
    end
end

typeof(mymax(1.5, 2))
typeof(mymax(1, 2.5))

@code_warntype mymax(1.5, 2)

@code_warntype mymax(1, 2.5)
