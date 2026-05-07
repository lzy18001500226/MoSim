module MyPkg
Base.log2(x::Int) = log(x)
end

module MyPkg
struct MyInt
   x::Int
end
Base.log2(x::MyInt) = log(x.x)
end

module MyPkg
ty_log2(x::Int) = log(x)
end




module MyPkg
using LinearAlgebra
LinearAlgebra.dot(x, y) = …
end

module MyPkg
ty_dot(x, y) = …
end

module MyPkg
dot(x, y) = …
end




