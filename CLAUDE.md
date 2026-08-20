## Git 提交规范（强制执行）

**每次完成任务后必须立即提交到 git** — 这是硬性规则，不可协商。

- 任何对 `.mo` 文件、控制器、配置文件的修改完成后，立即 `git add` + `git commit`
- 提交信息必须清晰说明：修改了什么、为什么修改、影响范围
- 如果是重大修复或恢复工作，必须在提交前确认用户同意
- **禁止累积多次修改后再提交** — 每个独立任务完成即提交
- **禁止在未提交的情况下开始下一个任务** — 必须先提交当前工作

**教训来源**：2026-08-20 发生重大事故 — Codex 误执行 `git revert`，导致48个已修复的控制器被回退。虽然通过 `git reflog` 成功恢复（恢复到 `f23a8ea4ef`），但暴露了"不及时提交"的严重风险。

---

## 工作进度日志

- [2026-08-19 01:12] 完成Phase 1-5完整流水线：46个控制器核心从归档库恢复为纯Sysblock图形建模架构，38个生产控制器通过CheckModel验证（100%），28个通过50s ClimbPath仿真测试（73.7%成功率，终点误差<5m）— 涉及 `Scripts/restore_cores_phase2_final.py`（40个控制器Phase 2恢复）、`Scripts/restore_cores_phase3_final_12.py`（8个控制器Phase 3恢复）、`Scripts/phase4_phase5_complete_pipeline.py`（完整阶段四五自动化流程）、`Results/control_platform/phase4_phase5_complete/phase4_phase5_complete_report.json`（最终报告）、`Docs/Cache/investigation/phase3_restoration_complete.md`（阶段三总结）、`Docs/Cache/investigation/phase4_phase5_final_report.md`（阶段四五最终报告）
