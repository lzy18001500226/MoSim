# 载入图像
using TyWavelet
dir = pkgdir(TyWavelet) * "/examples/Resources/hexagon.jpg"
Im = imread(dir)
# 显示图像
img = imagesc(Im)
# 使用cauchy小波计算二维小波变换
cwtcauchy = cwtft2(
    Im; wavelet="cauchy", scales=1, angles=collect(0:(pi / 8):(2 * pi - pi / 8))
)
# 使用墨西哥帽小波计算二维小波变换
cwtmexh = cwtft2(Im; wavelet="mexh", scales=1, angles=collect(0:(pi / 8):(2 * pi - pi / 8)))
angz = [
    "0",
    "pi/8",
    "pi/4",
    "3pi/8",
    "pi/2",
    "5pi/8",
    "3pi/4",
    "7pi/8",
    "pi",
    "9pi/8",
    "5pi/4",
    "11pi/8",
    "3pi/2",
    "13pi/8",
    "7pi/4",
    "15pi/8",
]
# 绘制cauch和mexh小波在不同角度的小波系数
figure()
for angn in eachindex(angz)
    subplot(2, 1, 1)
    imagesc(abs.(cwtmexh.cfs[:, :, 1, 1, angn]))
    title("Mexican hat at $(angz[angn]) radians")
    subplot(2, 1, 2)
    imagesc(abs.(cwtcauchy.cfs[:, :, 1, 1, angn]))
    title("Cauchy wavelet at $(angz[angn]) radians")
    gcf().tight_layout()
    pause(1)
end
