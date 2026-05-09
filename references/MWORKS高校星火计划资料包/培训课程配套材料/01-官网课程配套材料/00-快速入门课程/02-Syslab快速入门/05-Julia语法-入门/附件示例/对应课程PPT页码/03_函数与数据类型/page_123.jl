num = 42;
str = string(num)

str = "$num"
str = "42";


str = "42";
num = parse(Int, str)
str = "3.14";
num = parse(Float64, str)

num = 42;
num = tryparse(Int, str)

invalid_str = "abc";
invalid_num = tryparse(Int, invalid_str)



