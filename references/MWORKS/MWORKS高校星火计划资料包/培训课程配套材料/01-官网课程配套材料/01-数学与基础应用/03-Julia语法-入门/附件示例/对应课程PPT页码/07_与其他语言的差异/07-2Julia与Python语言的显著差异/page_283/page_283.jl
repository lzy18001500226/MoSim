# 最后一个形参名 args 后加 ... 表示不定长参数 
function add(x, args...)
  res = 0
  for i in args
    res += i
  end
  return res + 2 * x
end
println(add(1, 2, 3, 4, 5)) # 16






