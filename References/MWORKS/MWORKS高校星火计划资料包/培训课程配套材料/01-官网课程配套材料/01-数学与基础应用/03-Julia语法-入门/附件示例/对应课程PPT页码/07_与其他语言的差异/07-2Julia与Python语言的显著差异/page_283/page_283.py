# 最后一个形参名 args 前加 * 号表示不定长参数
def add(x, *args):
  res = 0
  for i in args:
    res += i
  return res + 2*x
print(add(1, 2, 3, 4, 5)) # 16




