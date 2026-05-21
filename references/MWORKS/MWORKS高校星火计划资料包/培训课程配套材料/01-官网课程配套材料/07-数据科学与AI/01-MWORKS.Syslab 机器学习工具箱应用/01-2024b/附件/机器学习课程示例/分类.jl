using TyMachineLearning  # 机器学习工具箱
using TyPlot  # 图形工具箱
using CSV
using DataFrames
using TyStatistics


train_file = joinpath(pkgdir(TyMachineLearning), "data/Example/titanic_train.csv")
train_df = CSV.read(train_file, DataFrame);
test_df = train_df[1:200, :];
train_df = train_df[201:end, :];

println(first(train_df, 5))
println(first(test_df, 5))


# 计算特征之间的相关性
features_names = names(train_df[:, 2:end]);  # 保存特征的名字，用于绘图
feature_corr, _ = corr(Matrix(train_df[:, 2:end]));  # 计算特征之间的相关性
figure()
corr_heatmap = heatmap(  # 绘制相关性热力图
    feature_corr; xvalues=features_names, yvalues=features_names, fmt=".2f",rotation = 45)
tightlayout()

# 训练数据准备
select!(train_df, Not(:Survived), :Survived);
select!(test_df, Not(:Survived), :Survived);
# 训练模型
ada_clf = AdaBoostTree(train_df, 500, 0.75, 9, 1);
lgbm_clf = GradientcBoosting(
    Matrix(train_df[:, 1:(end - 1)]),
    train_df[:, end];
    n_estimators=500,
    max_depth=5,
    min_samples_leaf=2,
);
rf_clf = randomcforest(
    Matrix(train_df[:, 1:(end - 1)]),
    train_df[:, end];
    n_estimators=500,
    max_depth=6,
    min_samples_leaf=2,
);


ada_fi = ada_clf.feature_importances_;
lgbm_fi = lgbm_clf.feature_importances_;
rf_fi = rf_clf.feature_importances_;
ave_fi = (ada_fi + lgbm_fi + rf_fi) / 3;
println("AdaBoost: \t", ada_fi)
println("LGBM: \t\t", ada_fi)
println("Random Forest: \t", ada_fi)
println("平均: \t\t", ada_fi)


figure()
subplot(4, 1, 1)
scatter(features_names, ada_fi; filled=true)
xtickangle(12)
title("AdaBoost Feature Importances")
subplot(4, 1, 2)
scatter(features_names, lgbm_fi; filled=true)
xtickangle(12)
title("LGBM Feature Importances")
subplot(4, 1, 3)
scatter(features_names, rf_fi; filled=true)
xtickangle(12)
title("Random Forest Feature Importances")
subplot(4, 1, 4)
scatter(features_names, ave_fi; filled=true)
xtickangle(12)
title("Average Feature Importances of 3 Models")
tightlayout()

# 使用验证集查看各模型的预测精度
ada_score = ada_clf.score(Matrix(test_df[:, 1:(end - 1)]), test_df[:, end]);
lgbm_score = lgbm_clf.score(Matrix(test_df[:, 1:(end - 1)]), test_df[:, end]);
rf_score = rf_clf.score(Matrix(test_df[:, 1:(end - 1)]), test_df[:, end]);
print("AdaBoost: ", ada_score, "\n", "LGBM: ", lgbm_score, "\n", "RF: ", rf_score, "\n")


figure()
ada_cm, ClassLabelsada = confusionmat(
    test_df[:, end], 
    ada_clf.predict(Matrix(test_df[:, 1:(end - 1)]))
    )


subplot(1, 3, 1)
heatmap(ada_cm)
title("AdaBoost 混淆矩阵")

lgbm_cm, ClassLabelslgbm = confusionmat(
    test_df[:, end], 
    lgbm_clf.predict(Matrix(test_df[:, 1:(end - 1)]))
    )

subplot(1, 3, 2)
heatmap(lgbm_cm)
title("LGBM 混淆矩阵")

rf_cm, ClassLabelsrf = confusionmat(
    test_df[:, end], 
    rf_clf.predict(Matrix(test_df[:, 1:(end - 1)]))
    )
subplot(1, 3, 3)
heatmap(rf_cm)
title("RF 混淆矩阵")


# 取出各模型的预测值，进行堆叠 
ada_pred = ada_clf.predict(Matrix(train_df[:, 1:(end - 1)]))
lgbm_pred = lgbm_clf.predict(Matrix(train_df[:, 1:(end - 1)]))
rf_pred = rf_clf.predict(Matrix(train_df[:, 1:(end - 1)])) 

stack_pred = DataFrame(; Ada_pred=ada_pred, lgbm_pred=lgbm_pred, rf_pred=rf_pred) 
first(stack_pred, 5)


stack_names = names(stack_pred);
stack_corr, _ = corr(Matrix(stack_pred));
figure()
corr_heatmap = heatmap(stack_corr; xvalues=stack_names, yvalues=stack_names, fmt=".3f")


# 使用堆叠预测值训练一个 XGBoost 模型 
xgb_clf = HistcGradientBoosting(Matrix(stack_pred), train_df[:, end])


ada_test_pred = ada_clf.predict(Matrix(test_df[:, 1:(end - 1)]));
lgbm_test_pred = lgbm_clf.predict(Matrix(test_df[:, 1:(end - 1)]));
rf_test_pred = rf_clf.predict(Matrix(test_df[:, 1:(end - 1)]));
test_stack = DataFrame(;
    Ada_test_pred=ada_test_pred, Lgbm_test_pred=lgbm_test_pred, Rf_test_pred=rf_test_pred
    );
xgb_test_score = xgb_clf.score(Matrix(test_stack), test_df[:, end]);

print(xgb_test_score)
xgb_cm, ClassLabelsxgb = confusionmat(test_df[:, end], xgb_clf.predict(Matrix(test_stack)))
figure()
heatmap(xgb_cm)
