a=Float64[1 2 3; 4 5 6]

a[2,2]

a[1]

a[1,2] = 0


# 数组切片
x = [1 2 3 4 5 6]
# 1×6 Matrix{Int64}

# 提取部分元素，返回向量
px = x[2:end]
# 5-element Vector{Int64}

# 该用法与MATLAB的x(2:end)或x(:,2:end)等价
px = x[:, 2:end]
# 1×5 Matrix{Int64}