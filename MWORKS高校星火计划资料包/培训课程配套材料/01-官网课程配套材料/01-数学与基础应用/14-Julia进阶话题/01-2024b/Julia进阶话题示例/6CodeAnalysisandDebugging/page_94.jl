x = rand(10, 10);

@time x * x; # 第一次存在编译时间

@time x * x;
