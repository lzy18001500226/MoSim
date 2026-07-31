# Windows Command Entrypoints

`cmd/` contains the Windows double-click entrypoints formerly placed at the
repository root. Each wrapper resolves the repository root as the parent of
this directory, so keep these top-level launchers here and do not copy them
back to the root. Internal wrappers under `Scripts/` and skills remain in
their owning directories.

## Common Entrypoints

| Purpose | Entrypoint |
| --- | --- |
| MoSim Ground Control / QGC operator interface | `启动MoSim地面站.cmd` |
| Managed Gazebo/PX4 flight runtime | `启动Gazebo飞行仿真.cmd` |
| Stop managed simulation processes | `停止所有仿真.cmd` |
| Sunray grounded infrastructure check | `01_启动Sunray基础自检.cmd` |
| Sunray Gazebo visual review | `02_启动Sunray基础可视化审核.cmd` |
| Stop only the Sunray foundation runtime | `00_停止Sunray基础仿真.cmd` |

`Start_MoSim_QGC.cmd` is retained as a compatibility alias for
`启动MoSim地面站.cmd`.
