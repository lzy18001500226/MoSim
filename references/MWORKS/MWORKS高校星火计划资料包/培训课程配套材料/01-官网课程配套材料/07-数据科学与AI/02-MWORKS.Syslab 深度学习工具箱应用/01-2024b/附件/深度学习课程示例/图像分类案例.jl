# 加载手写数字数据集
using TyDeepLearning 
file = dataset_dir("digit")
XTrain, YTrain = DigitDatasetTrainData(file) 

# 将数据集划分为训练集和测试集
using Random
p = randperm(5000)
index1 = p[1:1000]
index2 = p[1001:end]
X_train = XTrain[index2, :, :, :]
Y_train = YTrain[index2, :]
X_test = XTrain[index1, :, :, :]
Y_test = YTrain[index1, :] 

# 随机选择 20 张图像进行绘制
using TyPlot
using TyImages
N, Channel, Hight, Width = size(X_train)
p2 = randperm(N)
index = p2[1:20]
figure(1)
for i in eachindex(range(1, 20))
    subplot(4, 5, i)
    imshow(X_train[index[i], 1, :, :])
end

# 图像增强处理，将图片在[-20, 20]度范围内随机旋转。
imageAugmenter = imageDataAugmenter(;RandomRotation = 20)            
X_train2 = permutedims(X_train, (1, 3, 4, 2))
imagesize = (28, 28)
augimds = augmentedImageDatastore(imagesize, X_train2, Y_train, imageAugmenter)

# 绘制图像增强处理后的图像。
augimds = permutedims(augimds, (1, 4, 2, 3))
figure(2)
for i in eachindex(range(1, 20))
    subplot(4, 5, i)
    imshow(augimds[index[i], 1, :, :])
end

# 指定网络训练选项。使用 CrossEntropyLoss 作为损失函数，Adam 为优化算法，评价指标为准确度，学习率为 0.01，epoch 为 100，bactchsize 为 64。
options = trainingOptions("CrossEntropyLoss", "Adam", "Accuracy", 64, 100, 0.01; Shuffle =false , Plots = true)

# 构建网络结构
layers = SequentialCell([
    convolution2dLayer(Channel, 8, 3), batchNormalization2dLayer(8),
    reluLayer(),
    maxPooling2dLayer(2; Stride = 2),
    convolution2dLayer(8, 16, 3), batchNormalization2dLayer(16),
    reluLayer(),
    maxPooling2dLayer(2; Stride = 2),
    convolution2dLayer(16, 32, 3), batchNormalization2dLayer(32),
    reluLayer(),
    flattenLayer(),
    fullyConnectedLayer(32 * 7 * 7, 10),
    softmaxLayer()]) 


# 训练网络
net = trainNetwork(augimds, Y_train, layers, options)

# 查看训练效果
YPred = TyDeepLearning.predict(net, X_test )
Y_test = reshape(Y_test, (1000))
acc = accuracy(YPred, Y_test) 

classes = [i - 1 for i in range(1, 10)]
YPred1 = probability2classes(YPred, classes) 
figure(4)
p2 = randperm(1000)
index = p2[1:9]
for i in eachindex(range(1, 9))
    TyPlot.subplot(3, 3, i)
    TyImages.imshow(X_test[index[i], 1, :, :])
    title1 = "Prediction Label"
    title2 = string(YPred1[index[i]])
    title(string(title1, ": ", title2))
end
