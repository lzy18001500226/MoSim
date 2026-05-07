class JuliaAPI:
    @staticmethod
    def add(xs):
        raise NotImplementedError
    
    def multiply(xs):
        raise NotImplementedError

def test():
    print("add 执行结束，结果为：", JuliaAPI.add([2,3,5]))
    print("multiply 执行结束，结果为：", JuliaAPI.multiply([2,3,5]))