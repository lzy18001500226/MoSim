using BenchmarkTools
x = rand(10, 10);

@btime x * x;
using BenchmarkTools
function compute_sum(n)
    num = 0
    for i in 1:n
        num += i
    end
    return num
end
@btime compute_sum(1000000);
