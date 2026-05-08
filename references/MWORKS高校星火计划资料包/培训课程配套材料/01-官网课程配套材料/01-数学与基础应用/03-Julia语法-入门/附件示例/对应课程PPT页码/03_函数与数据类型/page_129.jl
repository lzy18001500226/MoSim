mutable struct Bar
    baz
    qux::Float64
end
bar = Bar("Hello", 1.5);

bar.qux = 2.0
mutable struct Baz
    a::Int
    const b::Float64
end

baz = Baz(1, 1.5);

baz.a = 2



