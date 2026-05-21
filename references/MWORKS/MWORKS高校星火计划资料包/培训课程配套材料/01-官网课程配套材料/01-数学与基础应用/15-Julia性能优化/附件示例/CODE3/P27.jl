struct Point2D_1{T}
    x::T
    y::T

end
Point2D_1(3, 4)
Point2D_1(3.5, 4.5)

points = gen_points(1024);
typeof(points)

gen_points(n) = [Point2D_1{Any}(rand(), rand()) for i in 1:n]
points = gen_points(1024);

