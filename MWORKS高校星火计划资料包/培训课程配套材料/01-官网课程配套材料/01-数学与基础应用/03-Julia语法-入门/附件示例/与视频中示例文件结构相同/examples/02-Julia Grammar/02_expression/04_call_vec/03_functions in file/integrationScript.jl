using TyMath

function myIntegrand(x)
    return sin.(x) .^ 3
end

# Compute the value of the integrand at 2*pi/3.
x = 2 * pi / 3;
y = myIntegrand(x)
println(y)

# Compute the area under the curve from 0 to pi.
xmin = 0
xmax = pi
f = myIntegrand
a, = integral(f, xmin, xmax)
println(a)