运行步骤：
（1）需要更改SyslabGlobalConfig中的项目所在路径，具体方式
为右键菜单栏>>Syslab初始化配置>>找到变量g_abspath =
 "C:\\Users\\GlowTube\\Documents\\MWORKS\\SmartDrone"，
然后将其改为目前的路径。
（2）需要在Syslab里安装依赖，具体方式为：
在命令行输入"]"进入pkg模式，之后依次输入
add ONNXRunTime
add Images
add Luxor
add Colors
（3）仿真成功后，输出结果在文件夹SmartDrone\data\output中