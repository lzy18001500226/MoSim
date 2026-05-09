#定义自变量t的取值范围
t = 0:pi/50:10*pi;
#定义xy坐标与t的关系
x = sin.(t);
y = cos.(t);
plot3(x, y, t);
title("三维螺旋线")
