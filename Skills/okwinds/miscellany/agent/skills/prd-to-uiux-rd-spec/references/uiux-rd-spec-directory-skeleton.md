# UI/UX 研发规格目录骨架（skeleton）

> 用途：先让目录结构“像工程交付”，再补细节内容。

```text
docs/specs/ui-ux-rd-spec/
├── README.md
├── OVERVIEW.md
├── DOCS_INDEX.md
├── 00_SourceInventory/
│   ├── SOURCE_INVENTORY.md
│   └── COVERAGE.md
├── 01_Foundation/
│   └── FOUNDATION.md
├── 02_Components/
│   └── COMPONENTS.md
├── 03_Patterns/
│   └── PATTERNS.md
├── 04_Pages/
│   ├── PAGES.md
│   └── WorkbenchShell.md
└── 05_A11y/
    └── A11Y.md
```

建议（但不强制）：
- 组件/页面用“名词 + 场景/模块”命名，减少歧义（例如 `ReviewCenter_ScriptEval.md`）
- 任何新增文件都先登记到 `DOCS_INDEX.md`，避免内容散落

