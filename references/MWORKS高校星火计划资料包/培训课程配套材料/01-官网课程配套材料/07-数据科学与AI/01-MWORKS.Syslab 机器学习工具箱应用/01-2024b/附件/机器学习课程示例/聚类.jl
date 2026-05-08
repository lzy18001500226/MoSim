# 加载鸢尾花数据集
using TyMachineLearning
using CSV
using DataFrames
file = joinpath(pkgdir(TyMachineLearning), "data/Classification/iris.csv")
iris = CSV.read(file, DataFrame; header=false)
X = iris[:, 1:4] 


# 可视化原始数据集
rename!(iris, [:Column5 => :SH])
X1,y1,convs=convent_columns(iris,"SH")
fgdata_x1=Matrix(X1.values)
fgdata_y1=Array(y1.values)
scatter(X[:,1],X[:,2];c=fgdata_y1,filled="true")



# 对输入数据X训练层次聚类模型
n = 3 #聚类数
clf, idx = TyMachineLearning.cluster(fgdata_x1, n) 
# 可视化层次聚类后对数据的分配情况
scatter(X[:, 1], X[:, 2]; c=Array(idx), filled="true") 

xlabel("Feature 1")
ylabel("Feature 2")
title("Cluster Assignment of Iris Data")


