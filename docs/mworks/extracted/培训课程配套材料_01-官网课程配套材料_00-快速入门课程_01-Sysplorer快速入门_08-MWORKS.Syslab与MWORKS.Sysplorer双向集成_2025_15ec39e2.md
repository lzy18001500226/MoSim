# 5-1.jl

- Source: `培训课程配套材料/01-官网课程配套材料/00-快速入门课程/01-Sysplorer快速入门/08-MWORKS.Syslab与MWORKS.Sysplorer双向集成(2025b)/配套示例/5-Sysplorer API/5-1.jl`
- Category: `sysplorer_modeling`
- Score: `130`
- Size: `0.00 MB`
- Extract mode: `text`

## Extracted Text

```text
## 打开Sysplorer
using SysplorerAPI
ConnectSysplorer()
LoadLibrary("Modelica", "4.0") #加载 Modelica 标准库
SimulateModel("Modelica.Blocks.Examples.PID_Controller") #仿真标准库示例模型
times = GetVarValues("time")
values = GetVarValues("PI.y") #获取 PI.y 变量的仿真结果
using TyPlot
plot(times, values) #绘制仿真结果曲线
```
