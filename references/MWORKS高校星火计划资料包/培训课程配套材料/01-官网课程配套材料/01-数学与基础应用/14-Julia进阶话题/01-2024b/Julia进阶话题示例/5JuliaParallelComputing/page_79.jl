function f_sync()
    for i in 1:5
        busywait(2) # 时长 2 秒的计算密集型任务 
        sleep(1)    # 时长 1 秒的IO密集型任务
    end
end
@time f_sync()
