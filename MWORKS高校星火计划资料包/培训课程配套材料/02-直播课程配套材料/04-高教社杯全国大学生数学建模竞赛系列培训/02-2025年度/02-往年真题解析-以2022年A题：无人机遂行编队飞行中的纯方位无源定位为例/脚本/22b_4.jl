##
#当无人机之间无法确定距离时
#假设此时无人机队伍中有两架位置无偏差，分别为FY05和FY01(若是其他无人机同理)

## 标准分布
ρ = 50
F05 = [0 0]
F01 = [2 * ρ * cos(pi / 6) 0]
F02 = [ρ * cos(pi / 6) ρ * sin(pi / 6)]
F03 = [ρ * cos(pi / 6) -ρ * sin(pi / 6)]
F04 = [0 ρ]
F06 = [0 -ρ]
F07 = [-ρ * cos(pi / 6) ρ + ρ * sin(pi / 6)]
F08 = [-ρ * cos(pi / 6) ρ * sin(pi / 6)]
F09 = [-ρ * cos(pi / 6) -ρ * sin(pi / 6)]
F10 = [-ρ * cos(pi / 6) -ρ - ρ * sin(pi / 6)]
F11 = [-2 * ρ * cos(pi / 6) ρ + 2 * ρ * sin(pi / 6)]
F12 = [-2 * ρ * cos(pi / 6) 2 * ρ * sin(pi / 6)]
F13 = [-2 * ρ * cos(pi / 6) 0]
F14 = [-2 * ρ * cos(pi / 6) -2 * ρ * sin(pi / 6)]
F15 = [-2 * ρ * cos(pi / 6) -ρ - 2 * ρ * sin(pi / 6)]
FF = [F01, F02, F03, F04, F05, F06, F07, F08, F09, F10, F11, F12, F13, F14, F15]
FF0 = deepcopy(FF)
for i in 1:15
    plot(FF0[i][1], FF0[i][2], "bo")
    hold("on")
end

axis("square")

## 有偏差分布
# 假设FY05、FY01没有位置偏差
for i in 1:15
    if i != 5 && i != 1
        FF[i][1] = FF[i][1] + (-10 .+ (10+10)*rand(1))[1]
        FF[i][2] = FF[i][2] + (-10 .+ (10+10)*rand(1))[1]
    end
end

for i in 1:15
    plot(FF[i][1], FF[i][2], "ro", markerfacecolor="r")
    hold("on")
end

## 
# 选定被动机的序号
LL = [2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15] # 将所有组合汇总备用

η = 300 # 设定每一轮循环迭代次数
for m in 1:5
    ## 
    for k in LL
        for δ in 1:η
            # 此循环为被动机调整位置使得目标函数最小
            global Fk1 = zeros(1, 2)
            global Fk2 = zeros(1, 2)
            global Fk3 = zeros(1, 2)
            global Fk4 = zeros(1, 2)
            if k == 13
                α = acos(((norm(FF[k] - FF[5]))^2 + (norm(FF[k] - FF[1]))^2 - (norm(FF[5] - FF[1]))^2) / (2 * norm(FF[k] - FF[5]) * norm(FF[k] - FF[1])))
                β = acos(((norm(FF[k] - FF[5]))^2 + (norm(FF[k] - FF[12]))^2 - (norm(FF[5] - FF[12]))^2) / (2 * norm(FF[k] - FF[5]) * norm(FF[k] - FF[12])))
                x = [α β]
                y = [0 pi / 2]
                f = (norm(x - y))^2 # 初始位置目标函数大小计算    
                ## 
                # 将被动机分别向不同方向预调整并计算对应的目标函数大小
                Fk1[1] = FF[k][1] + 0.01
                Fk1[2] = FF[k][2] + 0.01
                α1 = acos(((norm(Fk1 - FF[5]))^2 + (norm(Fk1 - FF[1]))^2 - (norm(FF[5] - FF[1]))^2) / (2 * norm(Fk1 - FF[5]) * norm(Fk1 - FF[1])))
                β1 = acos(((norm(Fk1 - FF[5]))^2 + (norm(Fk1 - FF[12]))^2 - (norm(FF[5] - FF[12]))^2) / (2 * norm(Fk1 - FF[5]) * norm(Fk1 - FF[12])))
                x1 = [α1 β1]
                f1 = (norm(x1 - y))^2

                Fk2[1] = FF[k][1] - 0.01
                Fk2[2] = FF[k][2] + 0.01
                α2 = acos(((norm(Fk2 - FF[5]))^2 + (norm(Fk2 - FF[1]))^2 - (norm(FF[5] - FF[1]))^2) / (2 * norm(Fk2 - FF[5]) * norm(Fk2 - FF[1])))
                β2 = acos(((norm(Fk2 - FF[5]))^2 + (norm(Fk2 - FF[12]))^2 - (norm(FF[5] - FF[12]))^2) / (2 * norm(Fk2 - FF[5]) * norm(Fk2 - FF[12])))
                x2 = [α2 β2]
                f2 = (norm(x2 - y))^2

                Fk3[1] = FF[k][1] - 0.01
                Fk3[2] = FF[k][2] - 0.01
                α3 = acos(((norm(Fk3 - FF[5]))^2 + (norm(Fk3 - FF[1]))^2 - (norm(FF[5] - FF[1]))^2) / (2 * norm(Fk3 - FF[5]) * norm(Fk3 - FF[1])))
                β3 = acos(((norm(Fk3 - FF[5]))^2 + (norm(Fk3 - FF[12]))^2 - (norm(FF[5] - FF[12]))^2) / (2 * norm(Fk3 - FF[5]) * norm(Fk3 - FF[12])))
                x3 = [α3 β3]
                f3 = (norm(x3 - y))^2

                Fk4[1] = FF[k][1] + 0.01
                Fk4[2] = FF[k][2] - 0.01
                α4 = acos(((norm(Fk4 - FF[5]))^2 + (norm(Fk4 - FF[1]))^2 - (norm(FF[5] - FF[1]))^2) / (2 * norm(Fk4 - FF[5]) * norm(Fk4 - FF[1])))
                β4 = acos(((norm(Fk4 - FF[5]))^2 + (norm(Fk4 - FF[12]))^2 - (norm(FF[5] - FF[12]))^2) / (2 * norm(Fk4 - FF[5]) * norm(Fk4 - FF[12])))
                x4 = [α4 β4]
                f4 = (norm(x4 - y))^2
            else
                α = acos(((norm(FF[k] - FF[5]))^2 + (norm(FF[k] - FF[1]))^2 - (norm(FF[5] - FF[1]))^2) / (2 * norm(FF[k] - FF[5]) * norm(FF[k] - FF[1])))
                β = acos(((norm(FF[k] - FF[5]))^2 + (norm(FF[5] - FF[1]))^2 - (norm(FF[k] - FF[1]))^2) / (2 * norm(FF[k] - FF[5]) * norm(FF[5] - FF[1])))
                x = [α β]
                y = [acos(((norm(FF0[k] - FF0[5]))^2 + (norm(FF0[k] - FF0[1]))^2 - (norm(FF0[5] - FF0[1]))^2) / (2 * norm(FF0[k] - FF0[5]) * norm(FF0[k] - FF0[1]))) acos(((norm(FF0[k] - FF[5]))^2 + (norm(FF[5] - FF[1]))^2 - (norm(FF0[k] - FF[1]))^2) / (2 * norm(FF0[k] - FF[5]) * norm(FF[5] - FF[1])))]
                f = (norm(x - y))^2 # 初始位置目标函数大小计算    
                ## 
                # 将被动机分别向不同方向预调整并计算对应的目标函数大小
                Fk1[1] = FF[k][1] + 0.01
                Fk1[2] = FF[k][2] + 0.01
                α1 = acos(((norm(Fk1 - FF[5]))^2 + (norm(Fk1 - FF[1]))^2 - (norm(FF[5] - FF[1]))^2) / (2 * norm(Fk1 - FF[5]) * norm(Fk1 - FF[1])))
                β1 = acos(((norm(Fk1 - FF[5]))^2 + (norm(FF[5] - FF[1]))^2 - (norm(Fk1 - FF[1]))^2) / (2 * norm(Fk1 - FF[5]) * norm(FF[5] - FF[1])))
                x1 = [α1 β1]
                f1 = (norm(x1 - y))^2

                Fk2[1] = FF[k][1] - 0.01
                Fk2[2] = FF[k][2] + 0.01
                α2 = acos(((norm(Fk2 - FF[5]))^2 + (norm(Fk2 - FF[1]))^2 - (norm(FF[5] - FF[1]))^2) / (2 * norm(Fk2 - FF[5]) * norm(Fk2 - FF[1])))
                β2 = acos(((norm(Fk2 - FF[5]))^2 + (norm(FF[5] - FF[1]))^2 - (norm(Fk2 - FF[1]))^2) / (2 * norm(Fk2 - FF[5]) * norm(FF[5] - FF[1])))
                x2 = [α2 β2]
                f2 = (norm(x2 - y))^2

                Fk3[1] = FF[k][1] - 0.01
                Fk3[2] = FF[k][2] - 0.01
                α3 = acos(((norm(Fk3 - FF[5]))^2 + (norm(Fk3 - FF[1]))^2 - (norm(FF[5] - FF[1]))^2) / (2 * norm(Fk3 - FF[5]) * norm(Fk3 - FF[1])))
                β3 = acos(((norm(Fk3 - FF[5]))^2 + (norm(FF[5] - FF[1]))^2 - (norm(Fk3 - FF[1]))^2) / (2 * norm(Fk3 - FF[5]) * norm(FF[5] - FF[1])))
                x3 = [α3 β3]
                f3 = (norm(x3 - y))^2

                Fk4[1] = FF[k][1] + 0.01
                Fk4[2] = FF[k][2] - 0.01
                α4 = acos(((norm(Fk4 - FF[5]))^2 + (norm(Fk4 - FF[1]))^2 - (norm(FF[5] - FF[1]))^2) / (2 * norm(Fk4 - FF[5]) * norm(Fk4 - FF[1])))
                β4 = acos(((norm(Fk4 - FF[5]))^2 + (norm(FF[5] - FF[1]))^2 - (norm(Fk4 - FF[1]))^2) / (2 * norm(Fk4 - FF[5]) * norm(FF[5] - FF[1])))
                x4 = [α4 β4]
                f4 = (norm(x4 - y))^2
            end
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
for i in 1:15
    plot(FF[i][1], FF[i][2], "go")
    hold("on")
end
axis("square")