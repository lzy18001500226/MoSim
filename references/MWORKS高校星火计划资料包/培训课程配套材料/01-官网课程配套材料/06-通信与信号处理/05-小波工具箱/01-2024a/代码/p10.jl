using TyWavelet

rng = MT19937ar(1234)
x = randn(rng, 100, 1024)
fb = cwtfilterbank()
cfs, = cwt(x[1, :])
res = zeros(ComplexF64, 100, size(cfs, 1), size(cfs, 2))
print("cwt: ")
@time begin
    for k in 1:100
        res[k, :, :], = cwt(x[k, :])
    end
end
print("wt:  ")
@time begin
    for k in 1:100
        res[k, :, :], = wt(fb, x[k, :])
    end
end
