add(x, y) = x + y
add(1, 2)
add(3, 4)
add(1.0, 2.0)
add(1.0, 2)
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


