sleep(5) # 让当前任务等待 5 秒
t = @task sleep(5)
schedule(t) # 立即返回（但任务还没执行完）
