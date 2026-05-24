##第二问

af=1.5*pi/180
ct=120*pi/180
D0=120#中心点的海水的深度
n=8
β=0:45*pi/180:315*pi/180
fai=atan.(-tan(af)*cos.(β))
kes=atan.(tan(af)*sin.(β))
D=zeros(8,8)
wr=zeros(8,8)
wl=zeros(8,8)
w=zeros(8,8)
r=0:0.3*1852:2.1*1852
for i=1:n
    j=1:n
    D[i,j]=D0.-r[j].*tan.(fai[i])
    wr[i,j]=sin(ct/2).*D[i,j]./sin.(pi/2-ct/2 .+kes[i]);
    wl[i,j]=sin(ct/2).*D[i,j]./sin.(pi/2-ct/2 .-kes[i]);
    w[i,j]=wl[i,j]+wr[i,j]
end