%% 
x = linspace(0,2*pi);
y = sin(x);
plot(x,y)
%% 

xlabel("x")
ylabel("sin(x)")
title("Plot of the Sine Function")

plot(x,y,"r--")

x = linspace(0,2*pi);
y = sin(x);
plot(x,y)

hold on

y2 = cos(x);
plot(x,y2,":")
legend("sin","cos")

hold off

x = linspace(-2,2,20);
y = x';
z = x .* exp(-x.^2 - y.^2);
surf(x,y,z)