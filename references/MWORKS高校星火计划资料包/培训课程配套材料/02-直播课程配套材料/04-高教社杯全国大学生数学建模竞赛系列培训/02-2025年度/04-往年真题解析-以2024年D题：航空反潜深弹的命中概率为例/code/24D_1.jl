# f(x)=1/(sqrt(2*pi)*120)*exp(-(x^2)/(2*120^2))
# x=-1000:1:1000
# y = -1000:1:1000

# X, Y = meshgrid2(x, y)
# Z = f.(X).*f.(Y)
# mesh(X, Y, Z)

L = 100
W=20
R=20
t=0
s=0
f1(x,y)=(1/(2*pi*120^2))*exp(-(x^2+y^2)/(2*120^2))
ymin1(x) = -sqrt(R^2-(x-t+L/2)^2)+s-W/2
ymax1(x) = sqrt(R^2-(x-t+L/2)^2)+s+W/2
ymin2(x) = s-R-W/2
ymax2(x) = s+R+W/2
ymin3(x) = -sqrt(R^2-(x-t-L/2)^2)+s-W/2
ymax3(x) = sqrt(R^2-(x-t-L/2)^2)+s+W/2
q = integral2(f1, t-R-L/2, t-L/2, ymin1, ymax1)[1]+integral2(f1, t-L/2, t+L/2, ymin2, ymax2)[1]+integral2(f1, t+L/2, t+R+L/2, ymin3, ymax3)[1]