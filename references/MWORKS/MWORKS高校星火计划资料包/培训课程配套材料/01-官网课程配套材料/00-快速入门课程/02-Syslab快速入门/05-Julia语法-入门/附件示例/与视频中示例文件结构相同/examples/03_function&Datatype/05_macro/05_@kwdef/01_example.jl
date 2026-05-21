using Base: @kwdef

@kwdef struct Person
    name::String
    age::Int = 30
end

p1 = Person(name="Alice")
p2 = Person(name="Bob", age=25)
