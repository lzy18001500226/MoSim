include("average.jl")

z = 1:99;
ave = average(z)

average_REPL(x) = sum(x[:])/length(x);
ave2 = average_REPL(z)
