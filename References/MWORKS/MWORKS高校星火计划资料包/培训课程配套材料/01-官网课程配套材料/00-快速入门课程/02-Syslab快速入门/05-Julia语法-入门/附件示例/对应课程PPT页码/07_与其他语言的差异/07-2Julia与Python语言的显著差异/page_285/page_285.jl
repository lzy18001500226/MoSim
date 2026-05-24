function func(x=rand())
  println(x)
end
# 两次运行 x 的值不相同
# 每次运行都会调用一次 rand()
func()
func()







