# 第 10/11 章 TyPlot 统一排版规范（所有图生成脚本 include 本文件）
#
# 两条已验证的机理，写进 API 防止再犯：
#
# (1) 导出画幅只由 figure(figsize=[w,h]) 决定，单位英寸。
#     plt_set(gcf(), "OuterPosition", ...) 只影响屏幕窗口，对 exportgraphics 完全无效。
#     实测：默认 figsize [6.4,4.8] -> 裁边后 5.6x4.2 in；figsize [12,7] -> 7200x4200 px。
#
# (2) xticklabels/yticklabels/thetaticklabels 新建的 text 对象不继承 gca 已设字体。
#     必须先建标签、后设字体，否则回退无衬线。短缩写(RMSE)看不出，
#     长词组(Engineering Baseline)非常明显。本文件用 ticklab_x/ticklab_y/ticklab_theta
#     把顺序封死，调用点不可能弄反。
#
# 字号锚定：9 in 画布配 18 pt 轴标签 / 16 pt 刻度（已审定样张 p1_traj3d），
#     按画幅等比外推，保证图缩到报告 15 cm 时视觉字号一致。

const FIG_FONT = "Times New Roman"
const FIG_RES  = 600

lab_pt(w) = round(Int, 2.0 * w)
tik_pt(w) = round(Int, 1.78 * w)
leg_pt(w) = round(Int, 1.56 * w)

# 当前画布宽度（英寸），由 fig() 记录，供各 helper 推字号
const _FIG_W = Ref(9.0)

function fig(w::Real, h::Real)
    _FIG_W[] = Float64(w)
    return figure(figsize=[Float64(w), Float64(h)])
end

fig_w() = _FIG_W[]

# 设 gca 字体。无手动刻度标签的图直接调它；有的话必须在建完标签后调。
function axes_font()
    a = gca()
    plt_set(a, "fontname", FIG_FONT)
    plt_set(a, "fontsize", tik_pt(_FIG_W[]))
    return a
end

# 轴标签 / 标题
function styled(h)
    plt_set(h, "fontname", FIG_FONT)
    plt_set(h, "fontsize", lab_pt(_FIG_W[]))
    return h
end

# ---- 刻度标签：顺序封死版。传标签进来，内部保证 先建标签 -> 后设字体 ----
function ticklab_x(pos, labels; angle=nothing)
    xticks(pos)
    xticklabels(labels)
    angle !== nothing && xtickangle(angle)
    axes_font()
    return nothing
end

function ticklab_y(pos, labels)
    yticks(pos)
    yticklabels(labels)
    axes_font()
    return nothing
end

function ticklab_theta(angles_deg, labels)
    thetaticks(angles_deg)
    thetaticklabels(labels)
    axes_font()
    return nothing
end

function styled_legend(items; loc::String="best", ncol::Int=1)
    lg = legend(items; loc=loc, ncol=ncol)
    plt_set(lg, "fontname", FIG_FONT)
    plt_set(lg, "fontsize", leg_pt(_FIG_W[]))
    return lg
end

# (3) TyPlot 的 legend 会自动跟踪坐标区里所有数据序列：legend() 之后再画的曲线
#     同样被补进图例，标签 data3..dataN。MATLAB 那套"legend 之后加的线不进图例"
#     在这里不成立（实测 16 个墙盒 -> 图例 20 项，占掉半张图）。
#     图上有背景图元（墙、栅格、阈值面）时必须用本函数：显式传句柄子集，
#     句柄取 plot 返回值的 [1]。
function styled_legend_of(handles, labels; loc::String="best", ncol::Int=1)
    lg = legend(handles, labels; loc=loc, ncol=ncol)
    plt_set(lg, "fontname", FIG_FONT)
    plt_set(lg, "fontsize", leg_pt(_FIG_W[]))
    return lg
end

# 数据标注（barh 条端数值等）。注意 barh(text=...) 能在窗口渲染但会让
# exportgraphics 崩（PyCall.PyError），必须走这里手动标。
function annot(x, y, s; dy=0.0)
    return text(x, y + dy, s; fontsize=leg_pt(_FIG_W[]), fontname=FIG_FONT)
end

function save_fig(path::String)
    mkpath(dirname(path))
    exportgraphics(gcf(), path, resolution=FIG_RES)
    return path
end

# 抽稀：25001 点的曲线无需全画
thin(v, maxpts::Int=1200) = length(v) <= maxpts ? v : v[1:cld(length(v), maxpts):end]
