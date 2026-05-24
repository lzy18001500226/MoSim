% 线图
x = linspace(0,2*pi);
y = sin(x);
figure(1)
plot(x,y,"r--")
xlabel("x")
ylabel("sin(x)")
title("Plot of the Sine Function")
hold on
y2 = cos(x);
plot(x,y2,":")
legend("sin","cos")
% 三维绘图
x = linspace(-2,2,20);
y = x';
z = x .* exp(-x.^2 - y.^2);
figure(2)
surf(x,y,z)