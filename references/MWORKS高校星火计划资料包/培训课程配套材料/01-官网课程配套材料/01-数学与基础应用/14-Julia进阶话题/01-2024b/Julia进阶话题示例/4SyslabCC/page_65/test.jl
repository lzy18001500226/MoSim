using TyMath
function main()
    A = 1:10000
    A = reshape(A, 100, 100)
    display(fft(A)[1, 1:2])
end
@static @isdefined(SyslabCC) || main()
