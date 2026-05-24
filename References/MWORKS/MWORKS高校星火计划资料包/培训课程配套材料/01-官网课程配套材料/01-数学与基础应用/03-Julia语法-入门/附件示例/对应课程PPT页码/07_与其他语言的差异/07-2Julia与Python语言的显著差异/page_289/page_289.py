class Bar:
    def func(self, x):
        if isinstance(x, int):
            return 1
        elif isinstance(x, str):
            return 2
    
bar = Bar()
bar.func(1)     # 1
bar.func("abc") # 2





