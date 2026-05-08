i = 1;
while i <= 10
  global i += 1
  if i % 3 != 0
    continue
  end
  println(i)
end
for i = 1:10
  if i % 3 != 0
    continue
  end
  println(i)
end



