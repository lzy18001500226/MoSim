# 将向量转为列向量
v = [1, 2, 3]  # Vector
column_matrix = reshape(v, :, 1)  # 转为列 3x1 矩阵
println(column_matrix)  # 输出：[1; 2; 3;;]

# 将向量转为行向量
v = [1, 2, 3]  # Vector
row_matrix = reshape(v, 1, :)  # 转为 1x3 矩阵
println(row_matrix)  # 输出：[1 2 3]

# 将向量转为指定形状的矩阵
v = [1, 2, 3, 4, 5, 6]  # Vector
matrix_2x3 = reshape(v, 2, 3)  # 转为 2x3 矩阵
println(matrix_2x3)  # 输出：[1 2 3; 4 5 6]
