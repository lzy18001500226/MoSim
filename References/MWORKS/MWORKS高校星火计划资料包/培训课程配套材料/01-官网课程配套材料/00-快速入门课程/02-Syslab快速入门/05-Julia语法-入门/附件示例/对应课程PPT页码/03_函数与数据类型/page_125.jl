@enum Fruit apple = 1 orange = 2 banana = 3

f(x::Fruit) = "I'm a Fruit with value: $(Int(x))"
f(apple)
# 创建一个枚举值
my_fruit = Fruit(1)

# 也可以在 begin 块中指定值：
@enum Fruit begin
       apple = 1
       orange = 2
       banana = 3
end

# 检查枚举值
if my_fruit == apple
       println("It's an apple!")
else
       println("It's not an apple.")
end
# 列出枚举的所有实例使用 instances
instances(Fruit)
# 可以从枚举实例构造符号：
Symbol(apple)






