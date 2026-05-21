# Tiny Example（最小示例）

用户输入（示例）：

> 我有一份 PRD，需要你写一套“复刻级可落地”的 UI/UX 研发规格文档。要求：三栏工作台（左上下文/中操作/右指令监控），报告页面的章节未来会增减，图表工作区必须可交互，导出才静态化。

期望输出形态（要点）：
- 创建 `docs/specs/ui-ux-rd-spec/` 目录骨架（含 `OVERVIEW.md` / `DOCS_INDEX.md` / `COVERAGE.md`）
- 先写 `01_Foundation/FOUNDATION.md` 与 `04_Pages/WorkbenchShell.md`
- 为“报告可演进”设计 block/section 文档模型契约（组件级）
- 用 Coverage 映射 PRD 要点 → 规格落点，并列出未覆盖项

