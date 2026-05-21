x = rand(8)
[0.25 * x[i-1] + 0.5 * x[i] + 0.25 * x[i+1] for i = 2:length(x)-1]


