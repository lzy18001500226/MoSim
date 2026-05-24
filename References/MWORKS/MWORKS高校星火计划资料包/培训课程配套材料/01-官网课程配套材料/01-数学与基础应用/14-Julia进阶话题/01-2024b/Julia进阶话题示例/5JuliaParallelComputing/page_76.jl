f() = println("Hello")
t = Task(f)
t = @task println("Hello")