# 控制器文档证据采集规范

状态：比赛文档证据补齐的当前执行规范，2026-07-20。

## 1. 范围

权威路线来自：

```text
Results/control_platform/classic_controller_closeout_20260717/CLASSIC_CONTROLLER_FINAL_MATRIX.json
```

当前只补正文需要的模型、仿真结果和指标证据，不执行67项乘7场景全排列，
不继续扩展APP，不把Gazebo结果改写成MWORKS结果。

## 2. 每项最小证据

每条路线按以下四类独立记录：

1. 图形模型截图：能够识别模型名、主要模块和连线。CFunction密集桥图不能单独
   代表算法结构；若只能复用家族公共图，必须标注“家族共享结构”。
2. 结果查看器截图：能够识别结果窗口和路线，至少显示一个与该路线有关的有效变量。
3. 数值结果与指标：CSV/JSON必须能够回溯控制器、场景、时间轴或评价指标。
4. 原生结果：优先保存可追溯的`Result.msr`；没有独立MSR时，保留等价权威结果并
   明确证据上限，禁止用CSV/JSON冒充MSR。

`accepted`、`executed_blocked`和`not_run`是运行结论，不是截图完整度。性能未达门限的
真实结果仍可用于问题分析，但必须保留失败原因，不得写成通过。

## 3. 文件命名

新补证据统一写入：

```text
Results/control_platform/controller_document_evidence_20260720/<cohort>/<controller>/
  model/<controller>__model__mworks.png
  result/<controller>__result__mworks.png
  logs/<controller>__capture_manifest.json
```

能直接复用的历史截图不复制，盘点表引用其原路径。只有裁剪、模糊、窗口名错误、
空白或版本不一致时才重新采集。

## 4. 截图质量门禁

- 普通模型图与结果图使用DPI感知的后台窗口捕获，不抢占用户前台。
- 窗口最小化时，仅恢复到可绘制状态，截图后恢复最小化；默认不最大化。
- 图片不得空白、严重裁切或来自错误窗口；失败后只允许一次有界重试。
- 模型图应尽量完整显示主要模块和连线，结果图应显示有效曲线而非空坐标区。
- 登录、许可、授权、崩溃报告或未知弹窗立即停止现场仿真，不点击未知控件。
- 一个批次只复用一个Sysplorer会话，避免重复打开大量窗口。

## 5. 执行顺序

1. PID、线性/鲁棒、滑模、MPC：已有图形模型图和数值结果，优先补结果图。
2. 增强、安全：已有模型和数值结果，补模型图与结果图。
3. FTC、编队、学习：复用现有少量结果图，补其余模型图和结果图。
4. G9五条未完成运行门禁路线：先核对现有家族模型与生成代码，缺模型或结果时再补跑。
5. `mu_synthesis`、`neural_smc`：只做有界实现缺口尝试，不阻塞其余65项。

## 6. 当前盘点入口

```text
python Scripts/quality/build_controller_document_evidence_inventory.py
python Scripts/tests/test_controller_document_evidence_inventory.py
```

生成结果：

```text
Results/control_platform/controller_document_evidence_20260720/
  CONTROLLER_DOCUMENT_EVIDENCE_INVENTORY.json
  CONTROLLER_DOCUMENT_EVIDENCE_INVENTORY.md
```
