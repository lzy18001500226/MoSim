function f(x, y)
    x[1] = 42    # mutates x
    y = 7 + y    # new binding for y, no mutation
    return y
end

a = [4, 5, 6];

b = 3;

f(a, b) # returns 7 + b == 10
# 10

a  # a[1] is changed to 42 by f
# 3-element Vector{Int64}:
#  42
#   5
#   6

b  # not changed
# 3
