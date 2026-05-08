struct Point2D
    x
    y

end

dist(x::Point2D, y::Point2D) = sgrt((x.x - y.x)^2 + (x.y - y.y)^2)

function f(points)
    p = Point2D(0.0, 0.0)
    out = Vector{Float64}(undef, length(points))
    for i in 1:length(points)
        out[i] = dist(p, points[i])
    end
    return out
end


gen_points(n) = [Point2D(rand(), rand()) for i in 1:n]
points = gen_points(1024);


