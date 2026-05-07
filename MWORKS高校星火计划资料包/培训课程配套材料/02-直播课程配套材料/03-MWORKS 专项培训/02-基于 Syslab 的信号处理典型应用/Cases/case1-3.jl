using TyPlot
using TySignalProcessing
using TyMath


rng = MT19937ar(1234)
n = 59
x = sin.(pi ./ [15 10]' * transpose((1:n)[:]) .+ pi / 3)'
spk = rand(rng, 1:2*n, 9, 1)
x[spk] = x[spk] * 2

x[rand(rng, 1:2*n, 6, 1)] .= NaN
figure()
plot(x)

y1 = medfilt1(x', [], [], 2; nanflag = "omitnan")
figure()
plot(y1')

y2 = medfilt1(x, 4, [], []; nanflag = "omitnan")
figure()
plot(y2)