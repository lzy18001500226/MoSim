# 示例3-2.jl

- Source: `培训课程配套材料/01-官网课程配套材料/00-快速入门课程/01-Sysplorer快速入门/08-MWORKS.Syslab与MWORKS.Sysplorer双向集成(2025b)/配套示例/3-FromWorkspace/示例3-2.jl`
- Category: `sysplorer_modeling`
- Score: `120`
- Size: `0.00 MB`
- Extract mode: `text`

## Extracted Text

```text
#Syslab脚本：
# 标量
i_val = 5
f_val = 7.5
b_val = true# 向量 
i_vec = [1, 2, 3]
f_vec = [1, 2.5, 3.5]
b_vec = [true, false, true]# 矩阵
i_mtx = [1 2 3; 4 5 6]
f_mtx = [1 2.5 3.5; 4 5.5 6.5]
b_mtx = [true false true; false true false]# 三维数组
i_arr = fill(1, (2, 3, 4))
i_arr[2, 1, 3] = 17
f_arr = fill(2.5, (2, 3, 4))
f_arr[2, 1, 3] = 17
b_arr = fill(true, (2, 3, 4))
b_arr[2, 1, 3] = false
```
