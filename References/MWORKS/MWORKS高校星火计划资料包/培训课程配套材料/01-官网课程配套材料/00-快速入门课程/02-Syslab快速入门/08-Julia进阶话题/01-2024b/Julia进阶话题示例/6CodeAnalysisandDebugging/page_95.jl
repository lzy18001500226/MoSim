x = rand(10, 10);

time_taken = @elapsed x * x

function compute_sum(n)
    num = 0
    for i in 1:n
        num += i
    end
    return num
end
time_taken = @elapsed compute_sum(1000000)
