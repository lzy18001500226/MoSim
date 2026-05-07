module Example

export greet

# export FooStruct, processFoo
# 版本1
# struct FooStruct1
#     bar::Int
# end
# FooStruct = FooStruct1

# 版本2
# struct FooStruct2 # change version here
#     bar::Int
#     str::String # new add
# end
# FooStruct = FooStruct2

# 稳定版本
# struct FooStruct # change version here
#     bar::Int
#     str::String
# end

# function processFoo(foo::FooStruct)
#     @info foo.bar
# end

# f() = pi
greet() = "Hello, World!"

end # module