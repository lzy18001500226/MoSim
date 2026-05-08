% latcfilt 格型滤波器
%f,g = latcfilt(k,x)
%使用 k 指定的 FIR 格型滤波器系数对输入信号 x 进行滤波，并返回前向格型滤波器结果 f 和后向滤波器结果 g


%%
%生成具有 512 个样本点的高斯白噪声信号。
x = randn(512,1);
%%
%使用 FIR 格型滤波器过滤数据。指定反射系数，使格型滤波器等效于三阶移动平均滤波器
[f,g] = latcfilt([1/2 1],x);

%%
k=[1/2 1]
% 输入参数转为 Julia 类
jv_k = Julia(k);
jv_x=Julia(x)
% 关键字参数暂时没有


% 根据 Syslab 帮助文档，该函数有多个输出
jv = jcall("TySignalProcessing.latcfilt", jv_k, jv_x);

% 使用 jindex 将多个输出拆开
jv_1= jindex(jv, 1);
jv_2= jindex(jv, 2);

% 将输出参数转为 M 类型
f = fromJulia(jv_1);
g = fromJulia(jv_2);

%%

%在单独的绘图中绘制格型滤波器的最大相位和最小相位输出。
subplot(2,1,1)
plot(f)
title('Maximum-Phase Output')
subplot(2,1,2)
plot(g)
title('Minimum-Phase Output')
