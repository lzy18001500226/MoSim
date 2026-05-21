V4.12-20260326
一、安装包下载与准备
1. 平台的主体安装包为 RflySim*****.iso，正常情况下只需下载此文件即可。

注：以下软件可根据实际需求选择下载安装
2. 本云盘链接保持不变，但内部的安装包会实时更新，请定期检查以获取最新版本。
3. 云盘链接内 "OldFiles.txt" 提供历史版本安装包链接，正常情况下无需下载；若新版存在问题，可下载旧版进行回退。
4. RflySim平台安装直接运行OnekeyScript.exe即可一键完成，支持 Python/C++/ROS 等视觉、集群、AI算法开发。
  注意：如果用户电脑安装了全功能版本MATLAB（≥2022b），在启动时会自动发现并注册Simulink工具箱，还可进行底层飞控/运动模型定制/集群控制开发等需求。
  注意：如果电脑上已经安装了MATLAB（全功能板），还可以右键运行OnekeyScript.p，也可以一键安装并注册Simulink工具箱。
  注意：RflySim工具链的运行本身不需要MATLAB，但是提供Simulink的接口来加速控制和建模相关算法开发。
  这里提供一个推荐版本MATLAB的下载链接，用户请需要自行激活：https://pan.baidu.com/s/1msYUWukbD9pN9Sc0oCcVSw?pwd=b122
5. 对于底层飞控算法开发，平台支持 PX4 1.7 - 1.15 版本。因安装包大小限制，目前仅保留 1.12 和 1.14 版本固件。如需其他版本，请通过以下链接下载固件包（或使用官方固件包/自行修改的固件包），拷贝至 2.FirmwareZip 目录后，即可在一键安装脚本中选择对应固件。链接：https://pan.baidu.com/s/1SLyryqTvnTE2z1MZvzCGcA?pwd=w2ma

二、安装与使用方法
1. 使用资源管理器加载 RflySim*****.iso 镜像或使用解压软件解压后，阅读 "HowToInstall.pdf" 进行安装。
2. 平台流畅运行对电脑配置和操作系统有一定要求，请提前准备好相应的硬件环境。
3. 安装完成后，请阅读 PX4PSP/HowToUse.pdf 快速索引平台例程并学习使用方法。
4. 您也可以访问在线文档 rflysim.com 获取最新资讯与资料。
5. 如有任何问题，可访问 https://github.com/RflySim/Docs/issues 查找答案或提问。
6. 不同付费版本的功能区别与报价详见 PX4PSP/RflySimAPIs/1.RflySimIntro/RflysimVersions.pdf
7. 如有疑问或需咨询软硬件购买事宜，可在微信或淘宝搜索「飞思实验室」。

三、注意事项
1. 若安装过程中遇到任何问题，请先尝试关闭或卸载电脑杀毒软件（或在任务管理器中确保彻底关闭）。Windows 系统还需关闭系统实时防护功能，然后重新运行本脚本（MATLAB 安装方式可尝试以管理员身份启动 MATLAB）。若问题仍然存在，请下载 https://rflysim.com/res/DirectXRepair-v3.7.zip 并运行其中的修复程序。
2. 首次安装建议全部使用默认配置，直接点击「确定」即可，总安装时间约三十分钟。
3. 如需卸载 RflySim 系统，可运行 uninstall.exe 或 uninstall.m 进行自动卸载，或参考 uninstall.m 中的命令进行手动卸载。注意：付费版用户请保留 [我的文档]\Ogre 目录下的序列号文件 sn*.txt。
4. 杀毒软件可能会阻止脚本生成桌面快捷方式。若脚本提示快捷方式生成失败，请先关闭杀毒软件（Windows 系统还需关闭「设置」>「更新和安全」>「Windows 安全中心」>「病毒和威胁防护」>「管理设置」>「实时保护」），然后进入安装目录（默认为 C:\PX4PSP），双击运行 GenerateShortcutCMD.bat 脚本。
5. 如需针对不同 Pixhawk 硬件板更换编译命令（例如 px4_fmu-v3_default），在 MATLAB 中输入命令：PX4CMD('px4_fmu-v3_default') 或 PX4CMD px4_fmu-v3_default 即可。
6. 如需更改固件编译版本或还原/修复编译环境，可再次运行 "OnekeyScript" 命令并选择对应选项。
7. 对于 Windows 10 1903 及以上版本系统，推荐使用高级版并安装 Ubuntu 子系统，然后按「注意事项 2」方法重新配置环境选项，选择 WinWSL 编译器，可大幅加快编译速度。
8. 如果打开 CopterSim.exe 失败（提示找不到 “VCRUN****.dll” 或者无响应等），请检查杀毒软件是否存在误拦截，并运行本文件夹下文件 “4.HILApps\MSVCP_2019.07.20_X64.exe” 进行修复。

更新日志：
2026年03月26日 v4.12
1. 更新机器人大赛的例程bug
2. 更新例程文档。

2026年03月19日 v4.12
1. 批量更新bat，在RflySim3D启动脚本后面，增加预切换地图指令，提升场景加载时间。可参考：RflySimAPIs/SITLRunFw.bat
2. CopterSim更新，限制广播通信，解决局域网干扰问题。
3. 修复部分大模型控制例程bug，见1.RflySimIntro/2.AdvExps/e14.LocalLLMDepUse
4. 新增基于规则策略的3v3无人机区域防守系统实验，见2.AdvExps/e7.AISwarmCtrlExp/1.MultiUAVGameSimple
5. 新增开放鱼眼和光流传感器，详见多模态传感器详细介绍文档8.RflySimVision/VisionSensorAPI.pdf
6. 修复机器人比赛例程的各种bug，见8.RflySimVision/1.BasicExps/7.RobotCom26Basic和3.CustExps/e13.RobotCom26Adv
7. 修复exe版本的一键安装程序在安装过程中RflySimAPIs报错的bug
8. exe版本的一键安装程序支持倒计时自动确认功能，实现无人值守安装。

2026年03月11日 v4.12
1. DLL和exe生成脚本支持同时生成Windows和Linux版本。
2. 解决CopterSim的CSV日志时间戳问题的bug
3. 发布机器人比赛的新例程，见8.RflySimVision/1.BasicExps/7.RobotCom26Basic
4.新增打击爆炸的特效demo，见3.RflySim3DUE/0.ApiExps/e8_RflySim3DEffect

2026年03月04日 v4.12
1. 紧急修复自动代码生成控制器，因px4io问题导致CPU占用过高的bug
2. 修复桌面RflyTools中没有WinWSL快捷方式的bug
3. 更新部分章节的Readme实验文档。

2026年02月12日 v4.12
1. 优化EnableWSL.bat和TestWSL.bat，增强检查智能机制。
2. 修复RflySim3D小车轮转动和Attatch接口bug。
3. 优化按照脚本对MATLAB和Python的强关机制，增加提醒窗口。
4. 修复英文版安装包的bug

2026年02月06日 v4.12
1. 大幅提升视觉传感器的效率，提升频率和最大数量
2. 激光点云协议统一和修改，SendProtocol[7]位控制是否发送分割信息，默认不发送节省带宽。
3. SendProtocol[7]为1时，发送分割图以RGB555方式编码，粒度更细致。例程搜索segment相关。
4. 深度转点云传感器优化，增加分割信息发送
5. RflySim3D的其他UI优化与bug修复。
6. 修复exe安装脚本因文件占用删除失败而卡住的bug
7. 解决Simulink logger日志模块，中文路径生成代码报错的bug。
8. 新增展厅场景ExhibitionHall.zip
9. 更新自动代码生成的日志记录功能，增加高效日志记录模块。详见：5.RflySimFlyCtrl/0.ApiExps/5.Log-Write-Read

2026年01月31日 v4.12
1. 更新一键安装脚本OnekeyScript的界面，支持鼠标点击配置选项，支持进阶配置，更易用清晰。
2. OnekeyScript.exe和uninstall.exe重构完成，可双击直接运行，RflySim工具链已支持完全脱离MATLAB独立安装与运行。
3. 增加MATLAB自动识别与注册机制，电脑上所有MATLAB可以自动发现RflySim并进行注册与更新（可以先exe按照平台，后续根据需求安装MATLAB）。
4. 部分文档和例程的升级，解决部分Simulink例程的MATLAB版本过高无法打开的问题。
5. 解决视觉IMU传感器的加速度接口轴向问题
6. 优化MATLAB自动识别注册机制的异常处理，增加充足的修复提示。
7. 优化深度转点云的传输协议以及点云坐标系，详见8.RflySimVision/0.ApiExps/1-UsageAPI/3.PointCloudAPI/4.DepthPointCloudDemo
8. 大幅提升RflySim3D传感器取图与传输效率，延迟更低帧率更稳定

2026年01月10日 v4.11
1. 更新修复RflySimAPIs例程和Readme文档。
2. 更新RflySimUE5修复部分bug。
3. 新增视觉8.RflySimVision例程2.AdvExps：e14_odomLiDAR3DPc/e15_TFTreeConstruction/e16_ESDFPathPlan

2025年12月30日 v4.11
1. 更新RflySimAPIs下的例程Readme的pdf到最新版格式，修复链接引用问题
2. 对RflySim3D进行Bug修复。
3. 修复自动代码生成SITL控制器控制不响应的bug。

2025年12月18日 v4.11
1. 新增机器狗的蓝图控制模型与接口
2. 新增三旋翼垂起模型和控制接口
3. 新增灯光秀控制例程和接口。
4. 新增管道特效编辑端口
5. 优化更新各种例程
6. CopterSim新增更全面的日志记录功能

2025年12月09日 v4.11
1. 更新CopterSim支持转发自定义MAVLINK消息
2. 更新RflySim3D修复地形高度匹配接口/激光点云里程计数据/云台吊舱控制万向锁等问题
3. 更新Readme.pdf修复链接无法跳转的bug
4. 新增部分集群例程

2025年12月03日 v4.11
1. 修复CopterSimNoUI不响应三维ID修改的bug
2. CopterSim传感器发送模式改成保频率
3. RflySim3D更新，bug修复
4. 例程库更新，各种bug修复
5. VisCreate更新，bug修复
6. 更新ExpsMap.html，解决部分链接失效问题。

2025年11月24日 v4.10
1. 完善大模型控制例程
2. 更新RflySimUE5三维导入接口
3. 优化WSL的备份速度
4. 更新Python环境支持强化学习训练genesis-world
5. 解决CopterSim组播失败的问题。
6. 增加WSL下PX4+Gazebo仿真例程，见2.RflySimUsage/0.ApiExps/e14_GazeboSim
7. 提升穿框穿环例程成功率（改善框识别算法），见8.RflySimVision/1.BasicExps/1-VisionCtrlDemos/e4_CrossRing
8. 改善PX4ROS2直连例程的成功率（优化WSL2的通信模式选择），见6.RflySimExtCtrl/0.ApiExps/e19_uXRCE-DDS_ROS2CtrlExps
9. 优化Simulink建模库中的加速度等传感器模型，解决高机动性时发散的bug。

2025年11月14日 v4.10
1. CopterSim增加以Json格式指定通信的Ip地址，满足docker等环境支持。
2. 更新API文档，同步最新接口。
3. 优化WinWSL环境/WinWSL2-GPU外挂环境/Python环境，兼容性更强。
4. 优化固定翼书稿例程，修复视觉控制例程的一些bug
5. 更新CopterSim的发送机制，大幅提升WSL2环境下的稳定性。
6. 优化bat脚本请求管理员权限机制，取消授权不会报错。
7. 修复视觉大模型比赛例程bug。
8. 修复健康管理例程在新WinWSL的运行错误问题。
9. Rflysim3D日常更新维护
10. 修复部分视觉ROS程序无法编译的bug

2025年11月07日 v4.10
1. 增加DistSim分布式仿真（限完整版）和相关Python接口
2. 修复飞控自动代码生成，PX4和Simulink无法正常切换的bug

2025年11月05日 v4.10
1. 解决无人小车行驶异常问题，见：4.RflySimModel/1.BasicExps/e3_CarAckermanModeCtrl
2. 解决1.14和1.15固件连接QGC缓慢的问题。
3. 解决吊舱例程运行失败的问题8.RflySimVision/2.AdvExps/e1_CameraKeyDemoOnUbuntu
4. 增加带GPU加速的WSL增量包，见https://pan.baidu.com/s/1-IdhF-GCVS9jPh4eOmas3w?pwd=suj6
5. 修复PX4Official、PX4CMD等命令在WSL2模式下失效的bug
6. 常规例程升级

2025年10月30日 v4.10
1. 进一步提升CopterSim的实时性
2. 新旧WSL编译器分为两个安装包发布
3. RflySim3D持续更新，提升用户体验
4. 例程更新，修复部分bug
5. 8.RflySimVision\1.BasicExps\5.LLMUavComp切换为GPS定位源，提升操控体验。

2025年10月15日 v4.10
1. VcXsrv版本升级，提升显示效果
2. 修复Python环境serial模块报错，增加json5模块。
3. 修复NS-3编译问题。
4. 适配Gazebo Classic和最新版Gazebo的PX4 SITL仿真。

2025年9月29日 v4.10
1. 增加具身智能比赛（本地大模型）无人机控制例子。见8.RflySimVision/1.BasicExps/5.LLMUavComp
2. RflySim3D更新，进一步完善模型库和UI操作。
3. CopterSim更新，修复固定翼仿真失败的bug
4. VisCreate更新，新增ROS1/ROS2的Python/C++最小demo生成按钮。
5. 新增集群控制例子，见10.RflySimSwarm/0.ApiExps/e8.ROS2_Matlab（ROS控制）和e9.MultVehiclesStart（异构载具仿真）
6. 固定翼书稿例程进一步校验完善。

2025年9月24日 v4.10
1. 增加一个反恐场景，名字为TerrorTest
2. 更新WSL预装库，优化视觉例程部署流程、编译速度和安装包大小。
3. 修复固定翼书稿例程，见5.RflySimFlyCtrl/1.BasicExps/e10-FixedWingCtrl
4. 下放完整的视觉SLAM比赛穿环、避障、跟踪小车和降落例程到免费版，见8.RflySimVision/1.BasicExps/4_CompSlamNav

2025年9月20日 v4.10
1. SimCreate增加Python和ROS例程模版输出
2. RflySim3D模型库完善，增加三维模型库和场景保存功能
3. 修复Pixhawk6x等飞控自动代码生成固件无遥控器信号bug。
4. 新增PX4直连ROS2例程，见6.RflySimExtCtrl/0.ApiExps/e19_uXRCE-DDS_ROS2CtrlExps
5. 增加WSL2 GPU加速和Docker例程，1.RflySimIntro/2.AdvExps/e11_WSL2_GPUAccConfig
6. 免费版CopterSim支持HITL_NET连接带网口PX4（如 6x）进行硬件在环仿真，多机集群仿真更可靠。
7. 修复QGroundControl部分时候无法显示的bug
8. 新增视觉传感器快速预览接口，8.RflySimVision搜索quick_show_sens.bat

2025年8月21日 v4.10
1. 删除了1.7和Msys编译器安装包支持（清理空间）
2. WinWSL内部系统从Ubuntu 20.04 迁移到 22.04（WinWSL内输入lsb_release -a可查看版本），Python版本从3.8升级到3.12，删除了FlightGear安装包。注意：如果有需求想继续使用旧版环境，可以直接从https://pan.baidu.com/s/1voBFTUMzohBVFj5__amdZg?pwd=2g1x 下载文件，拷贝到现有安装包内部，则可使用旧的Ubuntu和Python，以及安装FlightGear和CygwinToolchain（支持Win7，限完整版）。
3. 免费版工具链安装包内新增1.14版本固件的支持，确保最新飞控的兼容性。
4. 支持直接安装WinWSL2，而不需要安装完手动切换
5. 增加Docker环境的完整支持，并开通GPU加速服务。
6. ROS2启用cyclonedds服务，支持零拷贝共享内存来加速
7. 增加VisCreate视觉传感器创建程序，详见[桌面]/RflyTools/VisCreate

2025年8月20日 v4.10
1. 升级WinWSL到Ubuntu 22.04，对应ROS2升级到Humble
2. WinWSL切换到WSL2后，支持镜像网络模式实现所有功能，且支持docker相关设置。
3. RflySim3D进一步优化UI功能。
4. 视觉取图协议更新，sendprotocal[6]支持设置UDP分包大小。默认WSL下按1400分包解决WSL打包丢图的问题。
5. 修复部分快捷方式生成失败的问题

2025年8月16日 v4.10
1. Python38环境全面升级为Python3.12，例程完成适配
2. 新增WinWSL覆盖安装提示，便于备份代码
3. 修复第5章固定翼例程中的bug
4. 修复1.13.2小车、UUV无法SITL仿真的bug，修复1.14/1.15部分bug
5. 修复最新Win系统上传固件失败问题，增加多飞控固件上传选择框
6. 新增RflyTools\ExpsMap的思维导图例程索引文件
7. 解决最新版Win11取消wmic导致的部分功能异常
8. 修复SIH仿真的部分问题。
9. 更新QGC到4.4.5版本。
10. RflySim3D更新模型库
11. CopterSim增加QT使用声明
12. 开始兼容22.04版本WSL

2025年7月30日 v4.00
1. 新增TestWSL.bat来检查WSL并自动弹出更新包
2. 更新RflySim3D，新增小地图移动等功能
3. WinWSL支持在WSL1和WSL2之间一键切换，见RflySimAPIs\WslSwitch2.bat
4. 修复Pixhawk 6x在1.12固件中的网络配置异常问题
5. RflySim3D界面显示持续优化更新
6. WSL2环境下的RflySimSDK\ctrl\ReqCopterSim.py请求IP出错bug修复。

2025年7月23日 v4.00
1. 进一步优化Win11下CopterSim性能问题
2. CopterSim右下角增加频率监测功能，用于确认仿真稳定性
3. 修复例程bug，完善文档

2025年7月20日 v4.00
1. 更新CopterSim修复SITL不稳定的bug，修复CopterSimNoUI显示bug，提升稳定性。
2. 更新CopterSim，完善SiH模式的支持，进一步提升大规模集群仿真时的稳定性。
3. 更新RflySim3D，增加UI界面，修复部分bug，增加日志记录与回放功能（测试中）
4. 第5章底层开发新增电机输出例程：5.RflySimFlyCtrl/0.ApiExps/20.FlyCtrlsSingalsTest，适配各种实飞场景。
5. 修复10.RflySimSwarm的Simulink集群控制库链接问题。
6. 故障注入例程新增故障注入RflySim3D提示并进一步完善，见7.RflySimPHM/1.BasicExps
7. 进一步完善大模型控制无人机例程。
8. 新增PC性能调优步骤HowToFix.pdf，进一步提升稳定性，解决飞行仿真抖动问题。

2025年06月30日 v4.00beta
1. 新增SimCreate软件
2. RflySim3D升级4.00，新增UI操控界面和更方便的物体创建功能
3. 新增大模型无人机控制例程（暂限完整版）6.RflySimExtCtrl/3.CustExps/e1.LLM_CtrlUAVExps（大模型控制接口），8.RflySimVision/3.CustExps/e10.LLM-BehaviorTreeUAVCtrl（大模型行为树控制）。待加入：大模型多模态控制、大模型集群编队等。
4. 优化无人车控制例程。4.RflySimModel/2.AdvExps/e6_CarR1DiffCtrl
5. 新增电池故障例程7.RflySimPHM/1.BasicExps/e8_BatteryFault

4.0计划新增功能（持续更新中）：
1. DistSim分布式管理软件：支持单台电脑控制所有仿真计算机和机载计算机，完成复杂分布式仿真任务。
2. VisCreate视觉传感器配置与预览软件：以图形界面的方式创建视觉传感器并预览，保存为Config.json。
3. ROSTrans转发工具：支持mavros和视觉传感器使用C++程序转发到WSL空间，实现更方便的ROS无人机/机器人控制接口。
4. DistVisSwarm多机协同视觉开发套件：支持在Gazebo环境中开发多机视觉协同算法（单台电脑非实时），并迁移RflySim3D分布式仿真（多台电脑实时），再到多台真机实验解决方案。
5. 新增鱼眼相机、全景相机、四目鱼眼环视相机、毫米波雷达、声呐等多模态传感器。
6. RflySim3D支持机器人+机器狗的蓝图控制模型，以及完整的AI训练解决方案。支持英伟达Isaac Sim算法接入，构建全方位具身智能AI训练解决方案。
7. 基于Python DLL综合模型的强化学习、深度强化学习加速训练框架。
8. 全方位大模型控制功能接入。
9. 基于RflySimUE5的虚拟实验室：支持无人机的装调配虚拟实验，支持无人机组装与性能估算，导出三维模型+运动模型到RflySim，进行后续HITL仿真和真机实验。
10. PX4 1.16固件支持。

2025年06月15日 v3.07
1. 新增Python310环境，以支持大模型等先进控制，暂限完整版。
2. 更新适配MATLAB 2025a，不会安装出错。


2025年05月27日 v3.07
1. 更新RflySimAPIs中的例程到最新版。
2. 更新WinWSL环境，确保视觉课程正常运行。
3. 例程适配Linux版本。

2025年03月31日 v3.07
1. CopterSim修复Simulink固定翼速度、偏航接口bug
2. 更新RflySim3D和视觉Python接口，修复视觉例程激光传感器和激光点云的bug
3. 完整版WinWSL环境更新，支持Gazebo多机视觉仿真环境。见：8.RflySimVision\3.CustExps\e8_GazeboSlam
4. 升级QGC到官方最新版4.4.4，解决部分飞控姿态不显示的问题
5. 修复视觉比赛例程无法起飞的bug
6. 新增2025年机器人大赛三维场景

2025年03月20日 v3.07
1. 修复部分安装bug
2. 更新例程。
3. 升级到PX4 1.15.4固件
4. 更新RflySim3D修复激光测距传感器bug


2025年02月16日 v3.07
1. 更新优化各章例程、API等文档。
2. 修复exe安装失败问题，以及新增Simulink组件不全的提示。

2025年01月13日 v3.07
1. CopterSim发布熙流仿真模式
2. 增加机制，自动更新WSL主目录下配置文件
3. 增加Simulink/mavros2自动配置功能（仅限MATLAB2024a/b）
4. 更新RflySim3D和RflySimUE5到3.07

2024年12月27日 v3.07
1. 更新适配无人机空中加油场景
2. 增加wsl自动升级的机制，解决wsl需要update的安装错误。
3. 升级Python环境的Opencv到4.10版本。


2024年12月12日 v3.06
1. 修复1.7版固件fmu-v3兼容性问题
2. 优化集群例程10.RflySimSwarm结构
3. 修复自动代码生成SITL突然电机停转问题

2024年11月28日 v3.06
1. 自动代码生成支持SITL仿真，见：5.RflySimFlyCtrl/0.ApiExps/14.SITLVeriGenCodeFirm。注：限收费版。
2. 更新RflySim3D库，内置Opencv等插件。
3. 更新RflySim3D软件，支持外部盒子直接控制场景（视觉硬件在环仿真）
4. 增加PX4固件1.15.2的支持。注：限收费版
5. 解决2.4.8（fmu-v3）的新飞控在1.7、1.12及之后版本无法使用的问题
6. 修复1.14-1.15版本实飞PWM和AUX通道的控制问题
7. 修复CopterSim的csv日志数据中，加速度和四元数错位问题。

2024年10月10日 v3.06
1. 修复虚拟机NAT模式下，分布式仿真的bug
2. MATLAB最低版本提升到2022b，解决高版本MATLAB无法实时运行的bug
3. 升级PX4固件，从1.14.3到1.14.4。注：限收费版

2024年9月19日 v3.05
1. 修复自动代码生成的一个bug
2. 修复CopterSim硬件在环不起飞的bug
3. 新的Simulink日志记录功能。
4. 修复Simulink的Aux模块单独编译问题
5. 修复RflySim3D显示问题

2024年9月14日 v3.05
1. UDP_Mode增加了一个模式Mavlink_Vision，会自动给飞控发送EKF2_AID_MASK，用于支持无GPS下SLAM视觉仿真。
2. 优化WinWSL.bat脚本机制优化，支持自动弹出图像窗口（不再需要运行WslGUI）
3. 更新Readme例程文档到最新版

2024年8月31日 v3.05
1. 新增Python加载DLL综合模型进行加速仿真的例程，见：4.RflySimModel/0.ApiExps/12.DllModelImport
2. QGroundControl 更新最新的固件版本

2024年8月23日 v3.05
1. 修复CopterSim的HITL_NET仿真bug
2. Simulink模块集群库更新
3. 更新到1.14.3版本固件

2024年8月17日 v3.05
1. 初步完成对所有例程的修复，更新完善Readme文档，确保例程正确运行。
2. 建模、底层控制、集群控制、健康评估的Simulink库基本建立完毕。
3. API.html逐步完善，各类接口使用介绍更清晰。
4. 3DDisplay软件使用RflySim3D LowGUI版本替代，解决无法正常打开的问题。
5. 更新bat脚本机制，运行更可靠完善。
6. 增加大量新例程，平台功能更完善。

2024年7月23日 v3.05
1. 硬件在环bat脚本更新，更精确地识别可连接的飞控
2. 支持自动连接飞控串口功能，只需设置COM号为0，例程见：RflySimAPIs\HITLRunAuto.bat
3. 大量例程重构推进中，文档进一步完善

2024年7月10日 v3.05
1. 修复碰撞模式空气墙的bug
2. 视觉传输协议1和3互换，默认使用jpeg传图方式
3. 修复自动代码生成参数导入不识别的bug。

2024年7月3日 v3.05
1. Simulink集群控制接口整合Pixhawk工具箱内
2. 新增UAV工具箱/Mavlink解析数据例程，见10.RflySimSwarm\1.BasicExps\e1_RflyUdpSwarmExp
3. 更新视觉例程8.RflySimVision和Readme文档，增加实验原理
4. 增加一个室内动捕实验场景CameraRoom.zip

2024年6月27日 v3.04
1. 更新Simulink集群仿真接口
2. 修复卓翼飞控1.13.2的固件bug

2024年6月19日 v3.04
1. 修复WinWSL安装失败的bug
2. 修复起飞嵌入地下不稳定的问题（解决比赛场景起飞炸机）
3. 优化机器人比赛例程，实现一键运行
4. 修复自动代码生成rfly_ext问题

2024年6月13日 v3.04
1. 更新文档，发布新版
2. WinWSL环境更新，使用Opencv4.2+ceres1.14的配置

2024年6月8日 v3.04
1. 优化WinWSL环境，支持NS3+Vins-Fusion的编译
2. 优化RflySimSDK的API方式，使用html索引方式。
3. 增加ROS1/ROS2控制的例子，包括访问自动代码生成的底层飞控

2024年5月30日 v3.04
1. 更新bat机制，跨电脑拷贝例程时，不再需要修改bat脚本。
2. 更新bat机制，支持电脑上多WSL并存时，正常运行平台。
3. RflySim平台更名为RflySim工具链，强化ROS1/ROS2开发功能，覆盖智能无人算法开发全流程。
4. 修复部分视觉例程bug
5. 更新QGroundControl，更好地支持硬件在环仿真。

2024年5月24日 v3.03
1. 修复接口bug
2. 新增offboard速度控制接口，简化比赛流程，见RflySimAPIs/8.RflySimVision/1.BasicExps/2-BaseDemoAuto
3. 新增1.13版本固件，Droneyee飞控的编译命令
4. 增加MavrosRun快捷方式，支持快速开启单机/多机的Ros/ROS2版本的mavros。

2024年5月21日 v3.03
1. 机器人比赛例程，新增激光SLAM与mavros起飞例子，见RflySimAPIs/8.RflySimVision/1.BasicExps/2-BaseDemoAuto
2. 修复特殊情况下，CopterSim与RflySim3D通信失败，导致飞机无法创建的问题。
3. Free免费版开放了新的WinWSL编译器，支持ROS视觉算法开发。见RflySimAPIs/1.RflySimIntro/2.AdvExps/e7_WslGUI/Intro.pdf
4. 比赛场景优化相机、激光雷达位置分布，使之更贴近真机。

2024年5月15日 v3.03
1. 机器人比赛场景增加屋顶，SLAM起飞更稳定。
2. 修复VisionAPI中，获取python路径的接口，在特殊情况下能获取json目录。
3. 优化虚拟机ROS切换和加载库的步骤
4. 优化比赛例程

2024年5月13日 v3.03
1. 修复部分电脑生成快捷方式出错的问题
2. 修复1.12.3固件，6c飞控电压无法识别的bug

2024年5月13日 v3.03
1. 增加MAVLink_NoGPS模式下，自动修改PX4参数，启用EKF里面的视觉位姿融合。（不再需要手动修改参数）
2. 修复CopterSim地形无法贴合的bug。

2024年5月11日 v3.03
1. 修复部分机器人比赛场景的bug
2. 修复SITL仿真无HIGHER_IMU消息的bug
3. 优化地面接触模型，减小振荡
4. 新增QGC中显示视觉仿真消息，便于视觉算法调试。


2024年5月8日 v3.03
1. 修复OnekeyScript.exe安装报错的bug

2024年5月8日 v3.03
1. 修复UDP_Simple模式，初始化位置错位问题
2. 修复MAVLink_NoGPS模式无法连接地面站的问题。

2024年5月7日 v3.03
1. 针对机器人比赛场景的部分更新，包括支持mid360传感器。
2. 修复RflySim3D不响应CopterSim地图切换的bug。
3. 修复RflySim3D不响应Python位置创建的bug。

2024年5月1日 v3.03
1. 自动代码生成新增新接口，支持电机（之前版本仅支持电机）、力+力矩、角速度、角度、姿态、速度、位置等任意环路的控制
见RflySimAPIs/5.RflySimFlyCtrl/0.ApiExps/15.InputSourceAPI、16.CtrlsSingalsAPI和17.OffboardCtrlsAPI
2. 更新PX4代码屏蔽机制，现支持在Simulink控制器和PX4官方控制器之间切换，使得实验更简单。
3. DLL模型协议更新，输入输出均改为double向量格式，为未将来支持Python/Simulink内加载DLL模型实现AI训练做准备。
4. 新增分布式视觉仿真实验例子。见RflySimAPIs/8.RflySimVision/0.ApiExps/2-DistributedSimAPI/Intro.pdf
5. 更新安装步骤HowToInstall.pdf，更新RflySimAPIs文件夹，新增大量例子，并完善文档，以及修复bug，见RflySimAPIs/Intro.pdf。
6. bat脚本默认管理员方式启动，提升仿真稳定性。此外，bat脚本启动QGC时，增加额外参数，不会误连飞控，导致串口占用。
7. CopterSim的“UDP收端口”选项，重定义为“三维ClassID”，支持修改RflySim3D显示的飞机三维样式。见“RflySimAPIs/SITLRunChange3D.bat”
8. RflySim3D新增机器人比赛地图场景，新增310飞机，新增DJI mid360激光点云传感器，可进行室内探索。（例程待开发）
9. 更新CopterSim界面上的文字描述，使之更贴近语义。
10. QGrondControl更新到4.3.0版本，并修改固件下载路径，支持本地路径烧录。优先使用1.13.2版本固件，使之更好支持硬件在环仿真。
11. CopterSim发送RflySim3D和30100仿真真值的数据结构体发生调整，增加GPS标志位（兼容未来全球大场景仿真）。
12. WinWSL的Ubuntu环境，由18.04更新到20.04（它不再兼容PX4 1.7和1.8版本固件编译），但是未来兼容mavros、Ros等（例程待开发）。

注：基于新的WinWSl编译环境，3.04版本会增加更多的基于Simulink的Windows/Linux通用的ROS/ROS2/Mavros控制例程。

其他：
1. WinWSL编译器取消PX4 1.17/1.18版本支持(WSL升级不再兼容低版本固件)，因为1.12/1.13版能满足实验需求。
2. 为节省安装包体积，完整版取消Cygwin编译器的支持，仅限企业版。
3. 安装包内取消1.11版本的安装包，以节省体积（可通过2.FirmwareZip/readme.txt链接手动下载带入）。
4. CopterSim新增波特率修改按钮（限完整版），支持修改波特率到指定值（兼容第三方飞控）。见：RflySimAPIs/HITLRun.bat
5. CopterSim新增GPS初始化选项（限完整版）。见RflySimAPIs/BatScripts/SITLPosStrGPS.bat
6. 完善对1.14版本的兼容（目前已完全兼容，但仅限完整版）


2024年3月8日 v3.02
1. 优化分布式仿真的功能，见8.RflySimVision/0.ApiExps/2-DistributedSimAPI
2. 完善英文版文档
3. 修复bug


2024年01月01日 v3.00
1. 3.00版本正式发布

2023年11月10日 v3.00
1. 重构了所有例程
2. 完善了readme文档体系
3. 自动代码生成支持SITL仿真、支持多模块开发等功能
4. 支持1.14版本固件
5. 支持红外相机等
6. 增加健康评估章节例程
7. 增加组网仿真章节例程
...
