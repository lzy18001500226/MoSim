class JuliaAPI:
    @staticmethod
    def add(xs):
        raise NotImplementedError
    
    def multiply(xs):
        raise NotImplementedError

    def medfilt1(x, n):
        raise NotImplementedError


def test():
    print("add执行结束，结果为：", JuliaAPI.add([2, 3, 5])) #10
    print("multiply执行结束，结果为：", JuliaAPI.multiply([2, 3, 5])) #30
