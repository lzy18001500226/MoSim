import numpy.polynomial

class MyNet(numpy.polynomial.Polynomial):
    def __init__(self, x=10):
        self.x = x
    def add(self, a):
        return self.x+a



