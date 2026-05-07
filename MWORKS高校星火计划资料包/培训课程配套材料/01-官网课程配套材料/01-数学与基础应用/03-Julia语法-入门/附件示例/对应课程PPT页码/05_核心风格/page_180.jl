add(x, y) = x + y
# add (generic function with 1 method)

add(1, 2)
# 3

add(3, 4)
# 7

add(1.0, 2.0)
# 3.0

add(1.0, 2)
# 3.0


using MethodAnalysis

add(x, y) = x + y

methodinstances(add)

add(1, 2)

methodinstances(add)

add(3, 4)

methodinstances(add)

add(1.0, 2.0)

methodinstances(add)

add(1.0, 2)

methodinstances(add)
