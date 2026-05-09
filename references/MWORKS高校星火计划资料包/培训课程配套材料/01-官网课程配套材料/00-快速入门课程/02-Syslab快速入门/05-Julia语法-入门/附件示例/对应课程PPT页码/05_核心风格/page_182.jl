is_number(x) = false
# is_number (generic function with 1 method)

is_number(x::Number) = true
# is_number (generic function with 2 methods)

is_number(x::Int) = true
# is_number (generic function with 3 methods)

is_number(1)

is_number(1.0)

is_number([2])

is_number("hello world")

methodinstances(is_number)

is_number(x::Number) = false
is_number(1)
