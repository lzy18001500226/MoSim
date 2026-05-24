using TyMachineLearning
S_points, S_color = get_curve() # 获取数据集
using TyPlot
scatter3(S_points[:, 1], S_points[:, 2], S_points[:, 3], c=S_color, s=50, filled=true)

"""     
plot_2d(data, fig, fig_title): 使用 TyPlot 绘制降维后的 2D 散点图
    args: 
        data: 用于绘图的 2D 数据
        fig: 用于绘图的画布        
        fig_title: 图标题
"""
        
function plot_2d(data, fig, fig_title; sub_pos=(0, 0, 0))
    if sub_pos != (0, 0, 0)
        subplot(sub_pos[1], sub_pos[2], sub_pos[3])
    end
    figure(fig)
    scatter(data[:, 1], data[:, 2]; c=S_color, s=50, filled=true)
    title(fig_title)
    return true
end


function build_lle_models(data)
    # 定义一个函数来构建并训练 4 种 LLE 模型
    print("-> Computing standard...\n")
    sd_embedding, ev = fitLocallyLinearEmbedding(data; n_neighbors=12, eigen_solver="auto")
    lle_standard = sd_embedding.embedding_
    print("-> Computing ltsa...\n")
    lle_ltsa = fitltsaEmbedding(data).fit_transform(data)
    print("-> Computing hessian...\n")
    lle_hessian = fitHessianEigenmapping(data).fit_transform(data)
    print("-> Computing modified...\n")
    lle_mod = fitMLLEmbedding().fit_transform(data)
    return Dict(
        "lle_standard" => lle_standard,
        "lle_ltsa" => lle_ltsa,
        "lle_hessian" => lle_hessian,
        "lle_mod" => lle_mod,
        )
end


# 使用 LLE 模型对数据进行降维
lle_models = build_lle_models(S_points)

fig = figure()
global position = 0  # 用于确定子图位置
for key in keys(lle_models)
    global position += 1
    plot_2d(lle_models[key], fig, key; sub_pos=(2, 2, position))
end
tightlayout()

# 使用 Isomap 模型对数据进行降维 
print("-> Computing isomap...\n") 
isomap_embedding, isomap_ev = fitIsomap(S_points) 
isomap_result = isomap_embedding.embedding_ 
plot_2d(isomap_result, figure(), "Isomap Embedding")

# 使用 MDS 模型对数据进行降维
print("-> Computing MDS...\n")
mds_embedding, ts = cmdscale(S_points)
mds_result = mds_embedding.fit_transform(S_points)
plot_2d(mds_result, figure(), "MDS Embedding")


# 使用 Spectral 模型对数据进行降维
print("-> Computing spectral...\n")
spectral_embedding = fitSpectralEmbedding("nearest_neighbors")
spectral_result = spectral_embedding.fit_transform(S_points)
plot_2d(spectral_result, figure(), "Specture Result")

# 使用 tsne 模型对数据进行降维
print("-> Computing tsne...\n")
tsne_embedding = tsne(; init="random")
tsne_result = tsne_embedding.fit_transform(S_points)

plot_2d(tsne_result, figure(), "t-SNE Result")
