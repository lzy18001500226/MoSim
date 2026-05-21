function addme2(a, b)
  result = a + b
  absResult = abs(result)
  return result, absResult
end
addme2(1, -3)
# 返回元组 (-2, 2)
x, = addme2(1, -3)
# x = -2
x, y = addme2(1, -3)
# x = -2, y = 2



