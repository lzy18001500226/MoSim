##第一问

af=1.5*pi/180
ct=120*pi/180
dx=200 #间距
h0=70 #中心水深
n=9 #测线数量
D=zeros(1,n);#水深
w=zeros(1,n);#宽度
wr=zeros(1,n);#宽度
wl=zeros(1,n);#宽度
wp=zeros(1,n);#投影宽度
η=zeros(1,n);#覆盖率

for i=1:n
    dis=(i-5)*dx
    D[i]=h0-dis*tan(af)
    wr[i]=sin(ct/2)*D[i]/sin(pi/2-ct/2+af);
    wl[i]=sin(ct/2)*D[i]/sin(pi/2-ct/2-af);
    w[i]=wl[i]+wr[i]
    wp[i]=w[i]*cos(af)
    if i>1
        η[i]=1-dx/(wr[i-1]+wl[i])*cos(af)
    end
end

