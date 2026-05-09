# 初等数学

t = -10:10;
x = t .^ 3 + 6 * t .^ 2 + 4 * t .+ 3;
bp = 0;
y = detrend(x, 1, bp; SamplePoints=t, Continuous=false);
plot(t, x, t, y, t, x - y, ":k");
legend(["Input Data", "Detrended Data", "Trend"]);

b = [2, 1, 0, 0];
a = [1, 0, 1, 1];
r, p, k = residue(b, a);



X, Y = meshgrid2(-4:0.002:2, -1.5:0.002:1.5)
Z = X + im * Y
H = zero(Z)

for i in 1:length(Z)
    if abs(Z[i]) == 0
        H[i] = 0
    else
        H[i] = besselh(0, Z[i])
    end
end

contour(X, Y, abs.(H); levels=0:0.2:3.2)

using TyImages
for n in 1:16
    ax = subplot(4, 4, n)
    ord = n + 8
    m = magic(ord)
    imagesc(m)
    title("$ord")
    axis("equal")
    axis("off")
end

# 多项式

p = [1, -4, 4]
p = [4, 0, 0, -3, 2, 33]



p1 = [1, -4, 4]
p2 = [3, 0, 2, 4]
[0; p1] + p2
[0; p1] - p2
conv(p1, p2)
q, r = deconv(p1, p2)



p1 = [1, -4, 4]
q1 = polyder(p1)
p2 = [2, 4];
q2 = polyder(p1, p2)[3];



p = [1, -4, 4]
polyval(p, 2)
X = [2 4 5; -1 0 3; 7 1 5]
Y = polyvalm(p, X)

p = [3, -2, -4];
r = roots(p)
p = [1, 0, 0, 0, -1];
r = roots(p)
#线性方程求解
A = magic(3)
B = [15, 15, 15]
x = linsolve(A, B)
B = inv(A)
C = A * B;
ty_format("short", C);

#线性方程组求解
A = [1 2 3; 1 4 9; 1 8 27]
B = [5, -2, 6]
x = linsolve(A, B)
#矩阵求逆和伪逆
A = [1 2 3; 1 4 9; 1 8 27]
B = [5, -2, 6]
X = A \ B
X = inv(A) * B
A = [1 2 3; 4 5 6; 7 8 9]
#inv(A)
pinv(A)

#奇异值分解
A = [1 2; 3 4; 5 6; 7 8]
F = svd(A, full=true)


#矩阵分解
A = [10 -7 0
    -3 2 6
    5 -1 5]

L, U = lu(A, NoPivot())
L, U = lu(A)
L, U, P = lu(A)
m = diagm([1, 1, 1])
P = m[P, :]
P' * L * U

A = magic(5)
qr(A)

#矩阵结构
a = [1 2 3; 4 5 6; 7 8 9]
b = tril(a)
c = triu(a)
d = bandwidth(a)
isbanded(a, 2, 2)
isdiag(a)
ishermitian(a)
issymmetric(a)
d = bandwidth(a)
isbanded(a, 2, 2)
istril(b)
istriu(c)

#矩阵属性
A = [1 3 2; -3 2 1; 4 1 2]
B = det(A)
A = [1 2 3; 3 4 5; 4 5 6]
B = rank(A)
A = [1 2 3; 3 4 5; 4 5 6]
B = tr(A)
A = [1 2 3; 3 4 5; 4 5 6]
B = norm(A)
A = magic(3);
B = cond(A, 1)
B = cond(A, 2)
B = cond(A, Inf)

#均匀分布随机数
a = rand(3,4)
a = rand(ComplexF64,3,4)
b = rand(UInt64,3,4)
rng1 = MT19937ar(5489)
rng2 = MT19937ar(5489)
for i = 1:10
global a1 = rand(rng1,3,4)
global a2 = rand(rng2,3,4)
end
a1 == a2
#三次样条插值
x=LinRange(-1,1,9)
y= @. 1/(1+25*x^2)
xx=LinRange(-1,1,100)
yy=spline(x,y,xx)
yr=@. 1/(1+25*xx^2)
plot(x,y,"o",xx,yy,xx,yr,"--")

#差值
x = [-3,-2,-1,0,1,2,3];
y = [-1, -1 ,-1 ,0, 1, 1, 1];
xq1 = -3:0.01:3;
p = interp1(x, y, xq1,"pchip");
s = interp1(x, y, xq1,"spline");
m = interp1(x, y, xq1,"makima");
plot(x, y, "o", xq1, p, "-", xq1, s, "-.", xq1, m, "--")
legend(["Sample Points", "pchip", "spline", "akima"], loc = "southeast")
figure(2)
x = 0:15;
y = besselj.(1, x);
xq2 = 0:0.01:15;
p = interp1(x, y, xq2,"pchip");
s = interp1(x, y, xq2,"spline");
m = interp1(x, y, xq2,"makima");
plot(x, y, "o", xq2, p, "-", xq2, s, "-.", xq2, m, "--")
legend(["Sample Points", "pchip", "spline", "akima"])


gx = -5:5
gy = -3:3
X, Y = ndgrid(gx, gy)
f1 = @. X^2 + Y^2
f2 = @. X^3 + Y^3
f3 = @. X^4 + Y^4
V = cat(f1, f2, f3, dims=3)
F = griddedInterpolant(X, Y, V)
qx = -5:0.4:5
qy = -3:0.4:3
XQ, YQ = ndgrid(qx, qy)
VQ = F(XQ, YQ)
subplot(3, 2, 1);surf(X, Y, f1);title("f1")
subplot(3, 2, 2);surf(XQ, YQ, VQ[:, :, 1]);title("Interpolated f1")
subplot(3, 2, 3);surf(X, Y, f2);title("f2")
subplot(3, 2, 4);surf(XQ, YQ, VQ[:, :, 2]);title("Interpolated f2")
subplot(3, 2, 5);surf(X, Y, f3);title("f3")
subplot(3, 2, 6);surf(XQ, YQ, VQ[:, :, 3]);title("Interpolated f3")
tightlayout()

include(pkgdir(TyMath)*"/examples/docs/flujet.jl")
V = X[200:300, 1:25]
figure()
ims = imagesc(reverse(V, dims = 2), xvalue = [0 125], yvalue = [100 0])
colormap(ims, "gray")
axis("off")
title("Original Image")
figure()
Vq = interp2(V,5)
ims = imagesc(reverse(Vq,dims=2), xvalue = [0 125], yvalue = [100 0])
colormap(ims, "gray")
axis("off")
title("Linear Interpolation")

X, Y = meshgrid2(-2:0.75:2, -2:0.75:2)
R = @. sqrt(X^2 + Y^2) + $eps()
V = @. sin(R) / R
figure()
surf(X, Y, V)
xlim([-4 4])
ylim([-4 4])
title("Original Sampling")
Xq, Yq = meshgrid2(-3:0.2:3, -3:0.2:3)
Vq = interp2(X, Y, V, Xq, Yq, "cubic", 0)

figure()
surf(Xq, Yq, Vq)
title("Cubic Interpolation with Vq=0 Outside Domain of X and Y")