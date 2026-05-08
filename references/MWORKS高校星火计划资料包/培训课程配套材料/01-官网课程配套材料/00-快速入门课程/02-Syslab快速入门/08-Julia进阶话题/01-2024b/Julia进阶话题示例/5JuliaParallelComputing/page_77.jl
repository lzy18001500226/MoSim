function busywait(seconds=5)
    # 该函数本身没有实际意义
    # 在这里仅仅是构造一个一直占用 CPU 的定时函数，用于演示异步任务的调度
    tstart = time_ns()
    while (time_ns() - tstart) / 1e9 < seconds
        continue
    end
    return (time_ns() - tstart) / 1e9
end
t = Task(busywait)
schedule(t)
