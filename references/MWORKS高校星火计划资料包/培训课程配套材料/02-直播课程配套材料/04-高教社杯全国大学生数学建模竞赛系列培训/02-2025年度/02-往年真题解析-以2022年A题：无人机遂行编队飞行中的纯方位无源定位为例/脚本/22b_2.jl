# 根据题目给出所有无人机的横纵坐标
F0 = [0 0]
F1 = [100 0]
F2 = [100 * cos(40 / 180 * pi) 100 * sin(40 / 180 * pi)]
F3 = [100 * cos(80 / 180 * pi) 100 * sin(80 / 180 * pi)]
F4 = [100 * cos(120 / 180 * pi) 100 * sin(120 / 180 * pi)]
F5 = [100 * cos(160 / 180 * pi) 100 * sin(160 / 180 * pi)]
F6 = [100 * cos(200 / 180 * pi) 100 * sin(200 / 180 * pi)]
F7 = [100 * cos(240 / 180 * pi) 100 * sin(240 / 180 * pi)]
F8 = [100 * cos(280 / 180 * pi) 100 * sin(280 / 180 * pi)]
F9 = [100 * cos(320 / 180 * pi) 100 * sin(320 / 180 * pi)]
FF = [F1, F2, F3, F4, F5, F6, F7, F8, F9] # 将所有坐标汇总备用
FF0 = deepcopy(FF) # 将所有坐标汇总备用
#绘制初始时刻各无人机所处位置
plot(F0[1], F0[2], "bo")
for i in 1:9
    hold("on")
    plot(FF[i][1], FF[i][2], "bo")
end

# 随机选取被动无人机序号
j = randi((2, 9), 1)[1]
# 随机选取另一主动无人机序号，需与被动无人机不同
f = 1
while f == 1
    global i = randi((2, 9), 1)[1]
    if i == j
        global f = 1
    else
        global f = 0
    end
end

# 为被动无人机增加偏差
FF[j][1] = FF[j][1] + (-10 .+ (10+10)*rand(1))[1]
FF[j][2] = FF[j][2] + (-10 .+ (10+10)*rand(1))[1]
plot(FF[j][1], FF[j][2], "ro")

# 根据无人机位置计算出三个角度，这三个角度实际上是被动无人机接收到的
α = acos(((norm(FF[j] - FF[i]))^2 + (norm(FF[j] - FF[1]))^2 - (norm(FF[i] - FF[1]))^2) / (2 * norm(FF[j] - FF[i]) * norm(FF[j] - FF[1])))
α1 = acos(((norm(FF[j] - FF[1]))^2 + (norm(FF[j] - F0))^2 - (norm(F0 - FF[1]))^2) / (2 * norm(FF[j] - FF[1]) * norm(FF[j] - F0)))
α2 = acos(((norm(FF[j] - FF[i]))^2 + (norm(FF[j] - F0))^2 - (norm(F0 - FF[i]))^2) / (2 * norm(FF[j] - FF[i]) * norm(FF[j] - F0)))
αα = [α, α1, α2]
n = argmax(αα) # 判断三个角度中哪个最大
if j <= 5
    if n == 1
        m = argmin(abs.([α2 - 10 / 180 * pi, α2 - 30 / 180 * pi, α2 - 50 / 180 * pi, α2 - 70 / 180 * pi]))
        if m == 1
            ii = j + 4
        elseif m == 2
            ii = j + 3
        elseif m == 3
            ii = j + 2
        else
            ii = j + 1
        end
    elseif n == 2
        m = argmin(abs.([α - 20 / 180 * pi, α - 40 / 180 * pi, α - 60 / 180 * pi]))
        if m == 1
            ii = 9
        elseif m == 2
            ii = 8
        else
            ii = 7
        end 
    else
        m = argmin(abs.([α - 20 / 180 * pi, α - 40 / 180 * pi, α - 60 / 180 * pi]))
        if m == 1
            ii = 2
        elseif m == 2
            ii = 3
        else
            ii = 4
        end
    end
else
    if n == 1
        m = argmin(abs.([α2 - 10 / 180 * pi, α2 - 30 / 180 * pi, α2 - 50 / 180 * pi, α2 - 70 / 180 * pi]))
        if m == 1
            ii = j - 4
        elseif m == 2
            ii = j - 3
        elseif m == 3
            ii = j - 2
        else
            ii = j - 1
        end
    elseif n == 2
        m = argmin(abs.([α - 20 / 180 * pi, α - 40 / 180 * pi, α - 60 / 180 * pi]))
        if m == 1
            ii = 2
        elseif m == 2
            ii = 3
        else
            ii = 4
        end
    else
        m = argmin(abs.([α - 20 / 180 * pi, α - 40 / 180 * pi, α - 60 / 180 * pi]))
        if m == 1
            ii = 9
        elseif m == 2
            ii = 8
        else
            ii = 7
        end
    end
end

R =100
w = 0:2*pi/R:2*pi
x = R * cos.(w)
y = R * sin.(w)
plot(x, y)
hold("on")
plot([FF[ii][1],FF[1][1],F0[1]], [FF[ii][2],FF[1][2],F0[2]], "ko",markerfacecolor="k")
plot([FF[ii][1], FF[j][1]], [FF[ii][2], FF[j][2]],"r--")
plot([100, FF[j][1]], [0, FF[j][2]],"r--")
plot([0, FF[j][1]], [0, FF[j][2]],"r--")
axis("square")
[ii, i]