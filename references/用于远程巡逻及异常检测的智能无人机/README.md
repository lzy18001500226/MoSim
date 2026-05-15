# 用于远程巡逻及异常检测的智能无人机
## 获奖团队介绍
学校：北京邮电大学
指导老师：高月红
团队成员：李熠然、张雨吉、 武鹏、赵梓岐
## 简介
本案例为一个具有图像识别的四旋翼无人机模型，在巡逻过程中，无人机能够悬停拍照，模拟信道传输，将拍摄的照片传回地面站判断是否存在异常情况。该模型在 Sysplorer 中，建立整个系统架构，完成仿真设置模块、飞行控制模块的建模。在 Syslab 中，完成图像采集及回传模块、智能识别模块的编写，并在 Sysplorer 中对编写好的函数进行调用，进行联合仿真。

## 使用说明
1.在打开示例前，请提前在 Syslab 中安装对应的依赖包，具体方式为： 在命令行输入"]"进入 pkg 模式，之后依次输入：
``` 
add ONNXRunTime
add Images
add Luxor
add Colors
```
2.在 Sysplorer 中，需要更改 SyslabGlobalConfig 中的项目所在路径，具体方式为右键菜单栏>>Syslab初始化配置>>找到变量g_abspath，然后将其改为目前模型保存的路径。
完整的 Modelica 模型如下图所示：
<p align="center">
  <img src="/mohub/resource/question/image_1756881721708.png" width="800">
</p>

## 仿真结果分析
1.在 Sysplorer 中，单击仿真，待仿真结束后，结果如下图所示：
<p align="center">
  <img src="/mohub/resource/question/image_1756881809109.png" width="800">
</p>
无人机运行位置与输入信号中预设的（100,100,100）一致，且飞到目的地后，进行了悬停拍照，实现了训练和异常检测功能。
<p align="center">
  <img src="/mohub/resource/question/image_1756881818609.png" width="800">
</p>
<p align="center">
  <img src="/mohub/resource/question/image_1756881823416.png" width="800">
</p>
仿真结果中，传输时延约为 0.137 s，SNR 为 17.6 dB，信道传输过程时间符合设计要求，可以完成异常检测要求。

**注**：生成结果图片为随机图片，时间和信道结果根据电脑性能不同而不同。
2.在 Sysplorer 仿真界面，在仿真界面>选择图表>动画，绘制起竖装置的三维动画，单击回放控制>播放按钮，实现动画播放。
<p align="center">
  <img src="/mohub/resource/question/07_1756881941011.gif" width="800">
</p>

## 版本说明
**V0.0.1，2025-09-03 14:09**
- 初始版本

## 使用许可
本模型库版权由北京邮电大学蓝桥杯参赛团队版权所有，未经原创作者许可，不得用于商业用途。

