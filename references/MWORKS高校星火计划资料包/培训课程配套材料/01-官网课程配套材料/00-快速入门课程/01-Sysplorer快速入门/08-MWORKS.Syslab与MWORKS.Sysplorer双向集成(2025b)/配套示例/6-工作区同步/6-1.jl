## Parameter 类型
VP3 = SysplorerParam();
VP3.Value = [1,2,3,4,5,6];
VP3.Description = "Sysplorer参数，向量类型";
VP3.DataType = "Float64"
VP3.Dimensions = [6]

## Scalar 数值类型
s1 = Float64(64.1)

## Vector 数值类型
v1 = Bool[1,0,1,0,1,1,0,0]
v2 = Float32[32.1,32.2,32.3,32.4,36.0]

## 2维矩阵
m1 = Bool[1,0,1,0,1,0,1,0,0,0];
m2 = reshape(m1,2,5)
