%%
%原条件
x = randn(512,1);
%原函数
%[f,g] = latcfilt([1/2 1],x);
%%
%调用实现
k=[1/2 1]
% 输入参数转为 Julia 类
jv_k = Julia(k);
jv_x = Julia(x)
% 根据 Syslab 帮助文档，该函数有多个输出
jv = jcall('TySignalProcessing.latcfilt', jv_k, jv_x);
% 使用 jindex 将多个输出拆开
jv_1= jindex(jv, 1);
jv_2= jindex(jv, 2);
% 将输出参数转为 M 类型
f = fromJulia(jv_1);
g = fromJulia(jv_2);
%%
% 绘图
subplot(2,1,1)
plot(f)
title('Maximum-Phase Output')
subplot(2,1,2)
plot(g)
title('Minimum-Phase Output')
