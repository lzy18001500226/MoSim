function compute()
    # 生成 1000x1000 的随机矩阵
    @time A = rand(1000, 1000)

    # 矩阵乘法
    @time B = A * A
    return B
end

R = compute();
