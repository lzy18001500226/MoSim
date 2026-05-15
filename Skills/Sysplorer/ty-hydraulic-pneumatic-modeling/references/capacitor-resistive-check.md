# 容阻检查

本文件用于把 Sysplorer 26a 文档中的“容阻检查（Capacitor-Resistive Check）”落到液压/气动 skill 的执行闭环中。参考页面为 Sysplorer 本地文档 `DevelopingModels/CheckAndCompileModel/CapacitiorResistiveCheck.html`。

## 适用范围

- 自动容阻检查机制当前按官方文档适配 `TYHydraulics` 和 `TYHydraulicComponents`。
- `TYPneumatics`、`TYThermalHydraulics`、`TYThermalHydraulicComponents` 的手册同样要求遵守容阻相连原则；若工具未提供自动检查入口，按本文规则做人工拓扑复核。
- 自建液压接口若要参与自动检查，需要在端口注解中标记容阻性。

## 触发时机

遇到下列情况时读取并执行本检查：

1. 新建或修复含泵、阀、管路、节流、容腔、蓄能器、油缸、油箱的 `TYHydraulics` / `TYHydraulicComponents` 模型。
2. `check_model`、翻译或仿真出现 NaN、发散、步长极小、压力异常偏高、预期动作下长期零流量等症状。
3. 修改了液压主回路拓扑、`UseVolumeA`、`UseVolumeB`、接口容腔、`Pipe_C`、`OilVolume*` 或同类容性/阻性组件。

## 容阻相连原则

1. 两个以上阻性件直接相连时，中间一般需要增加容性件，或只在其中一个相邻阻性元件上打开接口容腔。
2. 两个以上容性件直接相连时，中间一般需要增加阻性件。
3. 采用“打开接口容腔”的方式时，相连阻性元件之间只打开一个接口容腔；不要两侧同时打开造成过度容性连接。
4. 无容阻标识的自建端口不会参与自动容阻检查，不能把自动检查通过等同于自建接口已经物理合理。

常用修复方式：

- 在阻性元件之间插入 `Pipe_C`、`OilVolume*`、气腔或对应库中的容性件。
- 对具备 `UseVolumeA` / `UseVolumeB` 的元件，只打开当前连接集需要的一侧接口容腔。
- 在容性元件之间插入节流、阻尼、管阻、孔板或对应库中的阻性件。
- 对嵌套模型中的问题，打开子系统后在子系统内再次定位和修复。

## 执行闭环

1. 先通过父级规则完成模型路径、库、介质、拓扑表、图解语义和 `check_model` 的基础闭环。
2. 若 Sysplorer 界面或脚本能力可用，打开当前模型，使用“主页 > 仿真 > 检查下拉菜单 > 容阻连接检查”或等价入口执行检查。
3. 记录检查结果中的错误连接集数量和对象；对可定位项，定位到具体连线或连接集。
4. 对工具标红、无法自动修复或位于嵌套模型内的连接集，转为手工修复；必要时打开子系统再运行容阻检查。
5. 若使用“修复全部”等自动修复能力，必须把模型变更纳入后续源码/图面复核；不把自动修复结果直接视作最终通过。
6. 修复后依次重跑：容阻检查、`check_model`、必要的 `smart_layout`、`translate_model`、`simulate_model` 和目标变量验证。
7. 若自动修复不符合预期，可通过 Sysplorer 撤销；需要追溯自动修复步骤时，在工作目录日志中搜索 `MwCapresCheck`。

## 自建接口标识

自建液压接口要参与自动容阻检查时，在端口注解中添加 `__MWORKS(isCapacitive = ...)`：

```modelica
FluidPort_a port_A annotation(__MWORKS(isCapacitive = true));
FluidPort_a port_B annotation(__MWORKS(isCapacitive = false));
```

- `isCapacitive = true` 表示容性端口。
- `isCapacitive = false` 表示阻性端口。
- 未添加该标识时，端口视为非容性非阻性端口，不参与容阻性检查。

## 交付记录

当本检查被触发时，交付中补充：

- 是否运行了 Sysplorer 自动容阻检查；若未运行，说明采用人工拓扑复核的原因。
- 错误连接集数量、主要位置、修复动作。
- 修复后是否重跑容阻检查、`check_model`、翻译/仿真和目标变量验证。
