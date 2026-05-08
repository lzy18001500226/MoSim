struct Bar end

# 定义两个方法实现
func(bar::Bar, y::Int) = 1
func(bar::Bar, y::String) = 2


# 根据所有参数的类型来派发
func(Bar(), 1)    # 1
func(Bar(), "abc") # 2
