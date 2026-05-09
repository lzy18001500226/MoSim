# 根据题目给出所有无人机的横纵坐标
F0 = [0 0]
F1 = [100 0]
F2 = [98 * cos(40.1 / 180 * pi) 98 * sin(40.1 / 180 * pi)]
F3 = [112 * cos(80.21 / 180 * pi) 112 * sin(80.21 / 180 * pi)]
F4 = [105 * cos(119.75 / 180 * pi) 105 * sin(119.75 / 180 * pi)]
F5 = [98 * cos(159.86 / 180 * pi) 98 * sin(159.86 / 180 * pi)]
F6 = [112 * cos(199.96 / 180 * pi) 112 * sin(199.96 / 180 * pi)]
F7 = [105 * cos(240.07 / 180 * pi) 105 * sin(240.07 / 180 * pi)]
F8 = [98 * cos(280.17 / 180 * pi) 98 * sin(280.17 / 180 * pi)]
F9 = [112 * cos(320.28 / 180 * pi) 112 * sin(320.28 / 180 * pi)]
FF = [F1, F2, F3, F4, F5, F6, F7, F8, F9] # 将所有坐标汇总备用

#绘制初始时刻各无人机所处位置
for i in 1:9
    plot(FF[i][1], FF[i][2], "ro")
    hold("on")
end

η = 10 # 设定每一轮循环迭代次数

# 设定选定不同发射信号的无人机时，被动机的序号
L1 = [2, 3, 5, 6, 8, 9]
L2 = [1, 3, 4, 6, 7, 9]
L3 = [1, 2, 4, 5, 7, 8]
LL = [L1, L2, L3] # 将所有组合汇总备用

## 

for m in 1:10 #设定大循环次数
    for i in 1:3
        # 此循环选定不同主动机的组合
        # i=1代表主动机序号为1、4、7
        # i=2代表主动机序号为2、5、8
        # i=3代表主动机序号为3、6、9

        for k in LL[i]
            # 此循环为不同主动机对应的被动机序号
            if k != 1
                # 判断如果被动机序号是1则不进行调整
                for δ in 1:η
                    # 此循环为被动机调整位置使得目标函数最小
                    global Fk1 = zeros(1, 2)
                    global Fk2 = zeros(1, 2)
                    global Fk3 = zeros(1, 2)
                    global Fk4 = zeros(1, 2)
                    α = acos(((norm(FF[k] - FF[i])^2) + (norm(FF[k] - F0))^2 - (norm(FF[i] - F0))^2) / (2 * norm(FF[k] - FF[i]) * norm(FF[k] - F0)))
                    β = acos(((norm(FF[k] - FF[i+3])^2) + (norm(FF[k] - F0))^2 - (norm(FF[i+3] - F0))^2) / (2 * norm(FF[k] - FF[i+3]) * norm(FF[k] - F0)))
                    γ = acos(((norm(FF[k] - FF[i+6])^2) + (norm(FF[k] - F0))^2 - (norm(FF[i+6] - F0))^2) / (2 * norm(FF[k] - FF[i+6]) * norm(FF[k] - F0)))
                    x = [α β γ]

                    y = [(abs(4.5 - abs((i - k))) * 20) / 180 * pi (abs(4.5 - abs((i + 3 - k))) * 20) / 180 * pi (abs(4.5 - abs((i + 6 - k))) * 20) / 180 * pi]

                    f = (norm(x - y))^2 # 初始位置目标函数大小计算

                    ## 
                    # 将被动机分别向不同方向预调整并计算对应的目标函数大小
                    Fk1[1] = FF[k][1] + 0.1
                    Fk1[2] = FF[k][2] + 0.1
                    α1 = acos(((norm(Fk1 - FF[i])^2) + (norm(Fk1 - F0))^2 - (norm(FF[i] - F0))^2) / (2 * norm(Fk1 - FF[i]) * norm(Fk1 - F0)))
                    β1 = acos(((norm(Fk1 - FF[i+3])^2) + (norm(Fk1 - F0))^2 - (norm(FF[i+3] - F0))^2) / (2 * norm(Fk1 - FF[i+3]) * norm(Fk1 - F0)))
                    γ1 = acos(((norm(Fk1 - FF[i+6])^2) + (norm(Fk1 - F0))^2 - (norm(FF[i+6] - F0))^2) / (2 * norm(Fk1 - FF[i+6]) * norm(Fk1 - F0)))
                    x1 = [α1 β1 γ1]
                    f1 = (norm(x1 - y))^2

                    Fk2[1] = FF[k][1] - 0.1
                    Fk2[2] = FF[k][2] + 0.1
                    α2 = acos(((norm(Fk2 - FF[i])^2) + (norm(Fk2 - F0))^2 - (norm(FF[i] - F0))^2) / (2 * norm(Fk2 - FF[i]) * norm(Fk2 - F0)))
                    β2 = acos(((norm(Fk2 - FF[i+3])^2) + (norm(Fk2 - F0))^2 - (norm(FF[i+3] - F0))^2) / (2 * norm(Fk2 - FF[i+3]) * norm(Fk2 - F0)))
                    γ2 = acos(((norm(Fk2 - FF[i+6])^2) + (norm(Fk2 - F0))^2 - (norm(FF[i+6] - F0))^2) / (2 * norm(Fk2 - FF[i+6]) * norm(Fk2 - F0)))
                    x2 = [α2 β2 γ2]
                    f2 = (norm(x2 - y))^2

                    Fk3[1] = FF[k][1] - 0.1
                    Fk3[2] = FF[k][2] - 0.1
                    α3 = acos(((norm(Fk3 - FF[i])^2) + (norm(Fk3 - F0))^2 - (norm(FF[i] - F0))^2) / (2 * norm(Fk3 - FF[i]) * norm(Fk3 - F0)))
                    β3 = acos(((norm(Fk3 - FF[i+3])^2) + (norm(Fk3 - F0))^2 - (norm(FF[i+3] - F0))^2) / (2 * norm(Fk3 - FF[i+3]) * norm(Fk3 - F0)))
                    γ3 = acos(((norm(Fk3 - FF[i+6])^2) + (norm(Fk3 - F0))^2 - (norm(FF[i+6] - F0))^2) / (2 * norm(Fk3 - FF[i+6]) * norm(Fk3 - F0)))
                    x3 = [α3 β3 γ3]
                    f3 = (norm(x3 - y))^2

                    Fk4[1] = FF[k][1] + 0.1
                    Fk4[2] = FF[k][2] - 0.1
                    α4 = acos(((norm(Fk4 - FF[i])^2) + (norm(Fk4 - F0))^2 - (norm(FF[i] - F0))^2) / (2 * norm(Fk4 - FF[i]) * norm(Fk4 - F0)))
                    β4 = acos(((norm(Fk4 - FF[i+3])^2) + (norm(Fk4 - F0))^2 - (norm(FF[i+3] - F0))^2) / (2 * norm(Fk4 - FF[i+3]) * norm(Fk4 - F0)))
                    γ4 = acos(((norm(Fk4 - FF[i+6])^2) + (norm(Fk4 - F0))^2 - (norm(FF[i+6] - F0))^2) / (2 * norm(Fk4 - FF[i+6]) * norm(Fk4 - F0)))
                    x4 = [α4 β4 γ4]
                    f4 = (norm(x4 - y))^2
                    ## 
                    
                    FFk = [Fk1, Fk2, Fk3, Fk4] # 四个被动机调整后坐标
                    n = argmin([f1, f2, f3, f4, f]) # 确定最小的目标函数
                    # 如果调整前目标函数最小则不变，否则更新为调整后的位置
                    if n < 5
                        FF[k] = FFk[n]
                    end
                end
            end
        end
    end
end
## 
# 绘制调整后的无人机坐标及圆形区域
for i in 1:9
    plot(FF[i][1], FF[i][2], "go")
    hold("on")
end

w = 0:2*pi/100:2*pi
x = 100 * cos.(w)
y = 100 * sin.(w)
plot(x, y)
axis("square")