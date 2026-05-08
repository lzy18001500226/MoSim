x=0:0.02*1852:4*1852
y=0:0.02*1852:5*1852
X,Y = meshgrid2(x,y)

file_path = "附件.xlsx"
Z = xlsread(file_path,"C3:GU253")
U=-Z
subplot(2,1,1)
ms=mesh(X,Y,U)
subplot(2,1,2)
con = contourf(X, Y, U, 35)



