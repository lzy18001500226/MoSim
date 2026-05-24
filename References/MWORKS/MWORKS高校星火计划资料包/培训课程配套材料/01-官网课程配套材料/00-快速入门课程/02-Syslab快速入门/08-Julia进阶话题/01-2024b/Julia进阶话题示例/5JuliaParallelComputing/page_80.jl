function f_async()
    @sync begin
        for i in 1:5
            @async busywait(2)  # 时长 2 秒的计算密集型任务
            @async sleep(1)     # 时长 1 秒的IO密集型任务
        end
    end
end
@time f_async()
