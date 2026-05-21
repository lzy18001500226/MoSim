##
# 以α1、α2、α的大小关系直接判断
##

function pos(m, n, α1, α2, α)
    # m：被动机序号
    # n：第二架主动机序号
    # α1：第一架主动机、圆心主动机与被动机的夹角
    # α2：第二架主动机、圆心主动机与被动机的夹角
    # α ：第一架主动机、第二架主动机与被动机的夹角

    R = 100 #圆周排布半径
    ϕ0 = 40 / 180 * pi
    θ = (n - 1) * ϕ0
    α1 = α1 / 180 * pi
    α2 = α2 / 180 * pi
    α = α / 180 * pi
    # global r, ϕ

    if m > n
        if abs(α - (α1 + α2))<=1e-8
            # 可能性①
            ϕ = atan((-sin(α2 - θ) * sin(α1) + sin(α1) * sin(α2)) / (cos(α1) * sin(α2) + cos(α2 - θ) * sin(α1)))
            if ϕ < 0
                ϕ = 2pi + ϕ
            else
                ϕ = pi + ϕ
            end
            r = R * sin(α2 + ϕ - θ) / sin(α2)
        elseif abs(α1 - (α + α2))<=1e-8 
            # 可能性②
            ϕ = atan((sin(α2 + θ) * sin(α1) - sin(α1) * sin(α2)) / (-cos(α1) * sin(α2) + cos(α2 + θ) * sin(α1)))
            if ϕ < 0
                ϕ = 2pi + ϕ
            else
                ϕ = pi + ϕ
            end
            r = R * sin(α2 - ϕ + θ) / sin(α2)
        else
            # 可能性③
            ϕ = atan((sin(α2 - θ) * sin(α1) - sin(α1) * sin(α2)) / (cos(α1) * sin(α2) - cos(α2 - θ) * sin(α1)))
            if ϕ < 0
                ϕ = pi + ϕ
            end
            r = R * sin(α2 + ϕ - θ) / sin(α2)
        end

    else
        if abs(α - (α1 + α2))<=1e-8
            # 可能性④
            ϕ = atan((sin(α2 + θ) * sin(α1) - sin(α1) * sin(α2)) / (cos(α1) * sin(α2) + cos(α2 + θ) * sin(α1)))
            if ϕ < 0
                ϕ = pi + ϕ
            end
            r = R * sin(α2 - ϕ + θ) / sin(α2)
        elseif abs(α1 - (α + α2))<=1e-8
            # 可能性⑤
            ϕ = atan((sin(α2 - θ) * sin(α1) - sin(α1) * sin(α2)) / (cos(α1) * sin(α2) - cos(α2 - θ) * sin(α1)))
            if ϕ < 0
                ϕ = pi + ϕ
            end
            r = R * sin(α2 + ϕ - θ) / sin(α2)

        else
            # 可能性⑥
            ϕ = atan((sin(α2 + θ) * sin(α1) - sin(α1) * sin(α2)) / (-cos(α1) * sin(α2) + cos(α2 + θ) * sin(α1)))
            if ϕ < 0
                ϕ = 2pi + ϕ
            else
                ϕ = pi + ϕ
            end
            r = R * sin(α2 - ϕ + θ) / sin(α2)
        end

    end

    ϕ = ϕ / pi * 180
    return r, ϕ
end

r1, ϕ1 = pos(7, 9, 20, 40, 20)
r2, ϕ2 = pos(9, 5, 76, 12, 88)
r3, ϕ3 = pos(4, 9, 40, 18, 22)