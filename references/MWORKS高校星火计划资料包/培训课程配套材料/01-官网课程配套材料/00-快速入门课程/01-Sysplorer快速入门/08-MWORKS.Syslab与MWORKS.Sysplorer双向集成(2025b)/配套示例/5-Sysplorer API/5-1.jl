## 打开Sysplorer
using SysplorerAPI
ConnectSysplorer()
LoadLibrary("Modelica", "4.0") #加载 Modelica 标准库
SimulateModel("Modelica.Blocks.Examples.PID_Controller") #仿真标准库示例模型
times = GetVarValues("time")
values = GetVarValues("PI.y") #获取 PI.y 变量的仿真结果
using TyPlot
plot(times, values) #绘制仿真结果曲线