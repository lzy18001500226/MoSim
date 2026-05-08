function func(x)
  # 使用 isa 判断 x 是否是 Int 类型
  if x isa Int
    println("Int")
  else
    println("not Int")
  end
end
func(1) # "Int"





