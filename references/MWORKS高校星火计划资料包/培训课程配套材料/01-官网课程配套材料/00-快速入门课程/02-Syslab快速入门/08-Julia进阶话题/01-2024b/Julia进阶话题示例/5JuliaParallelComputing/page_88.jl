@time @sync for i in 1:10
    Threads.@spawn begin
        sleep(1)
        @show i, threadid()
    end
end
