x = -5:0.2:5;
y = x;#定义向量x和y
X, Y = meshgrid2(x, y);#生成坐标
Z = X .^ 2 + Y .^ 2;#表达式点运算
#图1：普通绘制
#subplot将多个图画到同一平面
subplot(2, 2, 1);
s = surf(X, Y, Z);#绘制三维图形
title("figure 1: surf");
#图2：平面阴影
subplot(2, 2, 2);
s = surf(X, Y, Z);
#set_edgecolor()用来修改网格属性，flat修饰网格
s.set_edgecolor("flat")
title("figure 2: surf with flat");
#图3：无网格边界
subplot(2, 2, 3);
s = surf(X, Y, Z);
#none表示无网格边界
s.set_edgecolor("none")
title("figure 3: surf with none");
#图4：遮挡绘制
subplot(2, 2, 4);
x1 = X[1, :];
y1 = Y[:, 1];
i = find((y1 .> 3) .& (y1 .< 4));
j = find((x1 .> 1) .& (x1 .< 3));
#赋空值
Z[i, j] .= NaN;
s = surf(X, Y, Z);
title("figure 4: surf with hole")
