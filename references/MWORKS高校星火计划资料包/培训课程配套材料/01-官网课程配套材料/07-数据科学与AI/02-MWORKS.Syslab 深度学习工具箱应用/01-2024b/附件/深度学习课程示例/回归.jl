using TyDeepLearning
file = dataset_dir("simplefit")
x, t = simplefit_dataset(file)

hiddenSizes = 10
net = feedforwardnet(hiddenSizes)
net_trained = train(net, x, t; epochs = 2000, lr = 0.05)

TyDeepLearning.plotfit(net_trained, x, t)
