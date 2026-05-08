af = 1.5 * pi / 180
ct = 120 * pi / 180
D0 = 110 #中心点的海水的深度
η = 0.1 
##系数测线
a1 = sin(ct / 2) / cos(ct / 2 - af)#wr的计算
a2 = sin(ct / 2) / cos(ct / 2 + af)#wl的计算
k1 = (1 - η) * cos(af)
k2 = tan(af)
L = 4 * 1852
Dmax = D0 + L * tan(af) / 2 #最深的海水深度

##第一条测线信息n=1
x1=Dmax*tan(ct / 2) #第一条的坐标x
D1 = Dmax - x1* tan(af)#第一条海水的深度

wr1= D1 * a1#第一条的右侧测线的宽度
w1 = D1 * (a1 + a2)#总的测线的宽度
d1=w1*(1 - η) * cos(af)/(1+sin(af)*(1 - η)*a2)

##初始
n=1
x =[x1]
D= [D1]
w= [w1]
wr=[wr1]
d= [d1]

while true
    if x[n] + wr[n] * cos(af) > L
        break 
    end
   global  n=n+1
  push!(D,D[n-1]-d[n-1]*tan(af))
  push!(x,x[n-1]+d[n-1])
  push!(wr,D[n]* a1)
  push!(w,D[n]* (a1+a2))
  push!(d,w[n] * k1/(1+k1*k2*a2))
end