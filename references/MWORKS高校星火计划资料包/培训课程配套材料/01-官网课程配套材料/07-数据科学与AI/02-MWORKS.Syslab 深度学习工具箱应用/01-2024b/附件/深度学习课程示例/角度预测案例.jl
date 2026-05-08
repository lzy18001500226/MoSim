using TyDeepLearning
using TyImages
using TyPlot
using TyMath
file = dataset_dir("digit")
XTrain, YTrain = DigitTrain4DArrayData(file) 

index = randperm(5000)[1:20]
figure(1)
for i in eachindex(range(1, 20))
    subplot(4, 5, i)
    imshow(XTrain[index[i], 1, :, :])
end

# 将数据集划分为训练集和测试集
using Random
p = randperm(5000)
index1 = p[1:1000]
index2 = p[1001:end]
X_train = XTrain[index2, :, :, :]
Y_train = YTrain[index2, :]
X_test = XTrain[index1, :, :, :]
Y_test = YTrain[index1, :] 


layers = SequentialCell([
    convolution2dLayer(1, 25, 12),
    reluLayer(),
    flattenLayer(),
    fullyConnectedLayer(25 * 28 * 28, 1),
])

options = trainingOptions("RMSELoss", "Adam", "MSE", 50, 500, 0.0001; Plots=true)
net = trainNetwork(X_train,Y_train,layers,options);

YPred = TyDeepLearning.predict(net, X_test)
rmse = sqrt(mse(Y_test, YPred))
index = randperm(1000)[1:9]
figure(3)
for i in range(1, 9)
    subplot(3, 3, i)
    hold("on")
    imshow(X_test[index[i], 1, :, :])
    x = [7:21...]
    plot(x, tan((90 + YPred[index[i]]) / 180 * pi) * (x .- 14) .+ 14, "r")
    ax = gca()
    ax.set_ylim(28,0)
    ax.set_xlim(0, 28)
    hold("off")
end
