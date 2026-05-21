export FooStruct, processFoo

# 版本1
struct FooStruct1
    bar::Int
end
FooStruct = FooStruct1

function processFoo(foo::FooStruct)
    @info foo.bar
end

# 版本2
struct FooStruct2 # change version here
    bar::Int
    str::String # new add
end
FooStruct = FooStruct2
