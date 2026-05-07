x = randn(512,1);
[f,g] = latcfilt([1/2 1],x);
subplot(2,1,1)
plot(f)
title('Maximum-Phase Output')
subplot(2,1,2)
plot(g)
title('Minimum-Phase Output')
