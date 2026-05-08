# 报错，if 关键词后不能使用非 Bool 类型变量
txt = "somthing"
if txt
  println("abc")
end
# ERROR: TypeError: non-boolean (String) used in boolean context
# 使用 !isempty(txt) 来表示字符串非空的条件
txt = "somthing"
if !isempty(txt)
  println("abc")
end







