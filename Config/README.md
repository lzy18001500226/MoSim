# Configuration

`Config/` stores machine-readable project configuration. It is not a location
for generated logs, experiment-specific source copies, or informal notes.

## 路径注册表

`project_paths.json` 是源码路径与运行入口的机器可读注册表。它同时记录
`canonical_relpath`、`active_relpath` 和 `migration_state`，因此不能只看
`src/` 下是否存在同名目录来判断迁移完成：

| 状态 | 含义 |
| --- | --- |
| `canonical_active` | 当前注册的活动路径等于项目 `src/` canonical 路径；不代表已经通过运行时性能验收。 |
| `copied_pending_activation` | 项目源码已复制到 `src/`，但至少一个当前入口仍使用 `References/` 或 vendor 路径。 |

交付前先运行静态检查：

```powershell
python Scripts/quality/check_project_path_registry.py --project-root . --require-canonical-active
python Scripts/quality/check_local_source_activation.py --project-root .
```

根目录 [`README.md`](../README.md) 的“源码路径与运行入口对应表”是面向用户
的展开说明；本文件和 `project_paths.json` 不证明 Gazebo/PX4/ROS 运行成功。
本批次迁移的九个组件已由第二条检查验证为 `canonical_active`。保留的
`References/` 路径用于来源追溯、回退和 Sunray 大型资产再物化，不是这些组件的
活动源码入口；它们不能在未经依赖审计的情况下删除。

| Path | Responsibility |
|---|---|
| `controllers/`, `control_platform/`, `codegen/` | controller profiles, platform contracts, and code-generation configuration |
| `profiles/`, `scenarios/` | selectable ExperimentProfiles and scenario definitions |
| `planners/`, `plant/`, `gazebo/` | planning, vehicle/plant, and Gazebo-specific configuration |
| `capabilities/`, `protocol/`, `schemas/` | machine-readable capability, interface, and validation contracts |
| `rviz/` | current ROS1 review configuration |
| `ros2/`, `rviz2/` | future/reference routes; not the current Sunray ROS1 evidence lane |
| `legacy/` | compatibility and historical metadata; do not make it a new active dependency |

Keep configuration declarative. Scripts consume it, models implement it, and
`Results/` records its execution. Do not hard-code a new configuration copy
into a runner when an existing profile or scenario can be extended.

## 归档规则

发布源包保留控制器平台、Profile、Plant、Schema、代码生成、路径注册表以及
仍被当前脚本/模型引用的兼容配置。`Config/legacy/`、`Config/protocol/` 和
旧场景目录只有在静态引用替换或固定后才能归档。归档操作必须在
`E:\刘致远18001500226\MoSim_Archive\<archive-id>\` 生成哈希清单，并在原
路径留下说明；不能把“从压缩包排除”当作“可以删除”。

2026-08-01 的收敛扫描覆盖 `Config/` 的 16 个顶层目录，均发现仓库内引用，
所以本批次没有移动任何配置。下一次归档必须针对单个文件/子目录给出消费者
清单，不能以“旧”“重复”或“未进入当前报告”作为唯一理由。
