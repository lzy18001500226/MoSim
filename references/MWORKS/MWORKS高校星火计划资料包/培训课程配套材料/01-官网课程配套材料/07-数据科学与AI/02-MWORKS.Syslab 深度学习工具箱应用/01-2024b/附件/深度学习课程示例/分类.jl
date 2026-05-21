using TyDeepLearning
using CSV
using DataFrames
set_backend(:mindspore)
file = dataset_dir("iris")
input_path = file*"/irisInputs.csv"
target_path = file*"/irisTargets.csv"
input = CSV.read(input_path, DataFrame; header = false)
target = CSV.read(target_path, DataFrame; header = false)
input = Array(input)
target = Array(target)


net = SequentialCell([
    fullyConnectedLayer(4, 20), 
    sigmoidLayer(), 
    fullyConnectedLayer(20, 3), 
    softmaxLayer()
])
options = trainingOptions("CrossEntropyLoss", "Adam", "Accuracy", 30, 1000, 0.01; Plots=true)


net_trained = trainNetwork(input, target, net, options)


prob = TyDeepLearning.classify(net_trained, input)
classes = [i - 1 for i in range(1, 3)]
YPred = probability2classes(prob, classes)
cm = confusionchart(target[:, 1], YPred)
