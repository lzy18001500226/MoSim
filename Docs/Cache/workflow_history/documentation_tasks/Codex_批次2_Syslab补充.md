# Codex 执行指令：批次2 —— Syslab传统工具补充

**目标文件**：
1. `Docs/报告/仿真分析报告_正文骨架.md`
2. `Docs/报告/用户手册_正文骨架.md`

**预计工作量**：1小时
**风险等级**：低（两处独立插入，不影响章节结构）

---

## 背景说明

当前文档对 Syslab 的描述过度聚焦于 AI Agent，缺失传统 Result Viewer 工具链的完整说明。Syslab 实际包含两层数据分析能力：

1. **传统层**：Result Viewer GUI（曲线对比、FFT频谱、CSV导出）
2. **AI层**：Claude API驱动的自然语言问答Agent

这两层应并列展示，不应只突出AI而忽略传统工具。本批次补充传统层内容。

---

## 任务A：仿真分析报告 §14.3 分层展开

**目标文件**：`Docs/报告/仿真分析报告_正文骨架.md`

### A.1 定位目标位置

**搜索**：`### 14.3 Syslab数据分析工具`

当前该节内容为：
```markdown
### 14.3 Syslab数据分析工具

本项目利用 MWORKS Syslab（Julia + Result Viewer GUI + AI Agent）进行结果后处理。

**AI Agent 能力边界**：
- 自然语言问答：... (后续内容)
```

### A.2 替换内容

**将整个 §14.3 替换为以下内容**：

```markdown
### 14.3 Syslab数据分析工具

本项目利用 MWORKS Syslab（Julia + Result Viewer GUI + AI Agent）进行结果后处理。Syslab 数据分析分为传统层和 AI 增强层两个层次。

#### 14.3.1 传统Result Viewer工具链

MWORKS Syslab 提供标准的 Result Viewer GUI，支持曲线对比、频谱分析和数据导出。

**核心功能**：

1. **多曲线叠加对比**
   - 同一变量跨多次仿真对比（例如：对比 Official PID、LQR、MPC 在同一场景下的位置跟踪曲线）
   - 不同变量同窗口展示（例如：位置误差、姿态角、控制输入三条曲线叠加）
   - 支持拖动缩放、时间轴对齐、图例自定义

2. **FFT频谱分析**
   - 选择时间序列变量 → 执行 FFT → 显示频率-幅值曲线
   - 用于识别振荡频率、验证带宽估计、排查谐振峰
   - 示例：对姿态角速率执行 FFT，观察是否存在 10 Hz 以上的高频振荡

3. **CSV批量导出**
   - 选择变量集 → 导出为 CSV 文件
   - 用于 MATLAB/Python 二次处理、生成LaTeX表格、绘制自定义图表
   - 批量导出支持多场景横向对比数据汇总

**操作流程**（详见用户手册第五章）：
- 启动 Syslab → 加载 Result.msr 文件
- 在变量树中勾选目标变量 → 右键选择"Plot"或"FFT"
- 调整时间范围、曲线颜色、图例位置
- 导出图像（PNG/SVG）或数据（CSV）

**传统工具与AI Agent的分工**：
- **传统工具适用场景**：精确数值读取、批量曲线叠加、频谱细节分析
- **AI Agent适用场景**：自然语言快速查询、趋势判断、异常模式识别

两者互补而非替代——传统工具提供精确控制，AI Agent 提供快速洞察。

> **图占位**
> - 内容：Result Viewer GUI 截图，显示三条控制器位置跟踪曲线叠加对比
> - 来源候选：运行一次多控制器对比实验，截取Result Viewer界面
> - 关键要素：变量树、曲线窗口、图例、时间轴工具栏清晰可见

![图14-3-Syslab Result Viewer多控制器曲线对比界面](./figures/fig14-3.png)

#### 14.3.2 AI Agent增强分析

在传统 Result Viewer 基础上，本项目开发了基于 Claude API 的 AI Agent，用于自然语言驱动的结果问答和趋势分析。

**AI Agent 能力边界**：
- 自然语言问答："哪个控制器的终端位置误差最小？"→ 返回排序表
- 趋势分析："LQR 在 ClimbPath50s 场景是否存在超调？"→ 读取 CSV 数据并判断
- 异常检测："所有 Official PID 场景中是否存在姿态角超过 15° 的情况？"→ 扫描全部记录
- 批量统计：对多场景结果执行统一门限检查，生成通过/失败汇总表

**技术实现**：
- Agent 通过 `read_result_csv` 工具读取 Syslab 导出的 CSV 数据
- 调用 Claude 3.5 Sonnet API 执行数据分析逻辑
- 返回 Markdown 格式的结构化答案

**典型用例**：
```
用户："对比 px4ctrl 和 Official PID 在 ClimbPath50s 的终端位置误差"
Agent：读取两份 Result.msr 对应 CSV → 计算 sqrt((x_ref - x)^2 + (y_ref - y)^2 + (z_ref - z)^2) → 返回：
  - px4ctrl: 2.3 m
  - Official PID: 3.1 m
  结论：px4ctrl 终端误差减少 26%
```

**局限性**：
- 依赖 CSV 导出质量（变量命名需一致）
- 复杂频域分析仍需传统 FFT 工具
- API 调用延迟（单次问答约 3-5 秒）

**与传统工具的协同**：AI Agent 快速定位问题变量 → 用户在 Result Viewer 中精确检查该变量的时域波形 → 必要时导出 CSV 进行 MATLAB/Python 深度分析。

> **图占位**
> - 内容：AI Agent 问答示例截图，显示用户问题、Agent 思考过程和返回的数值对比表
> - 来源候选：运行一次 AI Agent 会话，截取终端输出
> - 关键要素：问题清晰可读、返回表格格式规整、数值带单位

![图14-4-Syslab AI Agent自然语言问答示例](./figures/fig14-4.png)
```

---

## 任务B：用户手册 §5.4 扩充操作步骤

**目标文件**：`Docs/报告/用户手册_正文骨架.md`

### B.1 定位目标位置

**搜索**：`### 5.4 数据分析与可视化`

当前该节内容为：
```markdown
### 5.4 数据分析与可视化

**待写**：
- Syslab Result Viewer 基础操作
- AI Agent 使用示例
- CSV 导出与二次处理
```

### B.2 替换内容

**将 §5.4 完整替换为以下内容**：

```markdown
### 5.4 数据分析与可视化

#### 5.4.1 Result Viewer传统工具操作

MWORKS Syslab 的 Result Viewer 提供图形化曲线分析界面。以下为典型操作流程。

**步骤1：启动Syslab并加载结果文件**

```bash
# 进入 Syslab 工作目录
cd /path/to/MoSim/Results/control_platform/

# 启动 Syslab（假设已配置 MWORKS 环境变量）
syslab

# 在 Syslab GUI 中：File → Open → 选择 Result.msr 文件
```

**步骤2：浏览变量树并选择目标变量**

- 左侧面板显示变量树（按模块层级组织）
- 展开 `quadrotor.control.` 节点，找到 `position_error_x`、`position_error_y`、`position_error_z`
- 勾选目标变量（可多选）

**步骤3：绘制时域曲线**

- 右键选中的变量 → 选择 **Plot**
- 曲线窗口自动弹出，显示时间-数值曲线
- 可拖动缩放时间轴，双击图例修改曲线颜色和标签

**步骤4：多场景对比（叠加多份结果）**

- File → Add Result → 选择另一个控制器的 Result.msr
- 勾选相同变量名 → Plot
- 两条曲线自动叠加在同一窗口，图例区分不同文件来源

**步骤5：执行FFT频谱分析**

- 选择时间序列变量（例如 `attitude_roll_rad`）
- 右键 → 选择 **FFT**
- 弹出频率-幅值曲线窗口
- 用于识别振荡频率、验证带宽假设

**步骤6：导出CSV数据**

- 勾选需要导出的变量集（可跨模块多选）
- 右键 → 选择 **Export to CSV**
- 指定输出路径和文件名
- CSV 文件包含时间列和各变量列，可用于 MATLAB/Python 二次处理

> **提示**：批量对比多个控制器时，建议先导出 CSV 再用脚本统一处理，比手动逐一加载 Result.msr 更高效。

#### 5.4.2 AI Agent自然语言问答

本项目提供基于 Claude API 的 AI Agent，用于快速查询和趋势分析。

**启动方式**：

```bash
cd /path/to/MoSim/Scripts/syslab/
python ai_agent_cli.py --result /path/to/Result.msr
```

**典型问答示例**：

```
用户：哪个控制器的终端位置误差最小？
Agent：读取所有控制器的 ClimbPath50s 结果...
        Official PID: 3.1 m
        LQR: 2.8 m
        px4ctrl: 2.3 m
        结论：px4ctrl 最优

用户：LQR 是否存在超调？
Agent：读取 position_z 曲线...
        最大值: 12.3 m，参考值: 10.0 m
        存在 2.3 m 超调（23%）

用户：Official PID 在哪些场景下失败？
Agent：扫描所有场景记录...
        ClimbPath50s: 通过
        Hover30s: 通过
        敏感度分析-电机故障-eta0.7: 失败（solver stall）
        结论：电机效率低于 0.75 时不稳定
```

**注意事项**：
- AI Agent 依赖 CSV 导出数据，首次运行需等待数据加载（约10-30秒）
- 复杂频域分析仍需使用传统 FFT 工具
- API 调用需配置 `ANTHROPIC_API_KEY` 环境变量

#### 5.4.3 CSV导出与二次处理

对于需要精确数值计算或批量统计的场景，推荐导出 CSV 后用 MATLAB/Python 处理。

**示例：计算终端位置误差**

```python
import pandas as pd
import numpy as np

# 读取导出的 CSV
df = pd.read_csv('Result_ClimbPath50s_OfficialPID.csv')

# 计算终端位置误差
x_ref_final = 50.0  # 参考位置
y_ref_final = 0.0
z_ref_final = 10.0

x_final = df['position_x'].iloc[-1]
y_final = df['position_y'].iloc[-1]
z_final = df['position_z'].iloc[-1]

error = np.sqrt((x_ref_final - x_final)**2 +
                (y_ref_final - y_final)**2 +
                (z_ref_final - z_final)**2)

print(f"终端位置误差: {error:.2f} m")
```

**批量对比脚本模板**：见 `Scripts/syslab/batch_compare_controllers.py`。
```

---

## 完成后验证

1. **节编号连续性**：确认 §14.3.1 和 §14.3.2 正确嵌套在 §14.3 下
2. **图占位格式**：确认图占位块包含"内容/来源候选/关键要素"三部分
3. **代码块语法**：确认所有 ```bash 和 ```python 代码块闭合正确
4. **Markdown渲染**：确认无裸露的标题符号或列表缩进错误

---

## 注意事项

1. **不要修改其他章节内容**
2. **不要删除任何现有图占位**
3. **图编号规则**：新增图继续沿用所在章节的编号（图14-3/14-4，图5-X等）
4. **操作完成后不要自动commit**，等待人工review
