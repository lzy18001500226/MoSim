function mysum_threads(A)
    rst = 0
    @threads for i in 1:length(A)
        rst += A[i]
    end
    return rst
end

mysum_threads(1:100_000)