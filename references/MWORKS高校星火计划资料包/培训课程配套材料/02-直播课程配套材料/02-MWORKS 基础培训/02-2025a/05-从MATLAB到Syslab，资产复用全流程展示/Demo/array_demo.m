% 数组创建
a = [1 3 5; 2 4 6; 7 8 10]
z = zeros(5,1)
% 矩阵和数组运算
a + 10
sin(a)
a'
format long
p = a*inv(a)
format short
p = a.*a
a.^3
% 串联
A = [a,a]
A = [a; a]
% 复数
sqrt(-1)
c = [3+4i, 4+3j; -i, 10j]