f(x::Int) = "This is an Int: $(x)";
f(x::Float64) = "This is a Float: $(x)";
f(x::Any) = "This is a generic fallback";
f(10)
f("cat")


f(x::String) = "This is an String: $(x)";
f(x::Number) = "This is a Number: $(x)";
f("cat")
f(1 + 3im)



