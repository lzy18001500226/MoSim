#加载数据
using TyDeepLearning
file = dataset_dir("iris")
x, t = iris_dataset(file)


#创建自组织映射网络并训练
net = selforgmap(8, 8, 4);
net.train(x, 5000, verbose=true)


#绘制自组织映射样本命中
plotsomhits(net,x)

plotsomnd(net,x)