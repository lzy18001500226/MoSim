# 不定长的关键词参数使用 **kwargs 表示
def mul(x, y, **kwargs):
  z = 0
  if "z" in kwargs:
    z = kwargs["z"]

  return x + 2 * y + z

mul(y = 2, x = 1, z = 1)
# 2 + 1*2 + 1 = 6




