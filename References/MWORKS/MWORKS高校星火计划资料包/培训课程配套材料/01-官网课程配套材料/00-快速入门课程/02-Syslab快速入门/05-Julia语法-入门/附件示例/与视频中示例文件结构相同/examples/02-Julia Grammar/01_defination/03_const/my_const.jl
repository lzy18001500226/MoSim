const string_const = "hello"
const number_const = 1
const data_const = [1.2, 5.7]
const data_const2 = [
    data_const,
    data_const
]
push!(data_const, 1.2)
@show data_const2
