# Repo Layout Spec（仓库结构重构）

## Goal

将仓库结构重构为“多技术栈 SDK 共存、但源码不散落”的形式：

- **所有源代码都在 `src/` 下**。
- 不同技术栈的 SDK 各自收敛到一个目录（同级）：
  - `src/typescript-sdk/`
  - `src/python-sdk/`
- TypeScript SDK 的 Node 相关资源（`package.json`、`node_modules`、build/test/tools 配置等）不再放在仓库根目录。
- Python SDK 的资源同理（pyproject、tests、tools）集中在 `src/python-sdk/` 内。
- 仍然保留仓库级文档与工程规格在固定位置，避免“代码目录挟持文档目录”：
  - `docs/`：离线 API 文档、worklog、task summaries 等
  - `docs/specs/engineering-spec/`：可复刻级工程规格（Spec-Driven）

## Constraints

- 遵守 `AGENTS.md`：
  - 先文档/规格、后改代码与目录
  - 每次重构必须可离线回归验证（至少跑 unit/offline tests）
  - 新增/修改文档必须更新 `DOCS_INDEX.md`，并写入 `docs/worklog.md`
- **接口覆盖性门槛不变**：
  - TS：`operationIds` == catalog endpoint operationIds
  - Python：同上
- 生成器输出必须稳定（同输入同输出），并且生成产物与源代码同目录（便于复制与分发）。

## Target Structure（目标结构）

```
wkteam-api-sdk/
  AGENTS.md
  README.md
  DOCS_INDEX.md
  docs/
    api/
    worklog.md
    task-summaries/
  docs/specs/engineering-spec/
    ...
  src/
    typescript-sdk/
      package.json
      package-lock.json
      node_modules/          # 本地安装产物（不提交）
      src/                   # TypeScript SDK 源码（含 generated）
      test/                  # Vitest 离线回归
      tools/                 # Node 工具（解析离线文档 + codegen）
      dist/                  # 构建产物（不提交）
    python-sdk/
      pyproject.toml
      README.md
      wkteam_api_sdk/        # Python SDK 源码（含 generated）
      tests/                 # pytest 离线回归
      tools/                 # Python codegen
```

## Acceptance Criteria

1) Python SDK：
- 目录名为 `src/python-sdk/`（无歧义）
- `python3.11 src/python-sdk/tools/generate_sdk.py` 可生成：
  - `src/python-sdk/wkteam_api_sdk/manifest.py`
  - `src/python-sdk/wkteam_api_sdk/generated_api.py`
- `PYTHONPATH=src/python-sdk python3.11 -m pytest -q src/python-sdk/tests` 通过

2) TypeScript SDK：
- Node 相关资源不在仓库根目录（`package.json`/`node_modules`/`tsconfig`/`vitest`/`tsup`/`tools`/`test` 全部在 `src/typescript-sdk/`）
- `cd src/typescript-sdk && npm test` 通过
- `cd src/typescript-sdk && npm run generate:api` / `npm run generate:sdk` 可运行

3) 文档与索引：
- `DOCS_INDEX.md` 更新到新路径
- `docs/worklog.md` 记录：关键决策、迁移命令、验证结果

## Test Plan（离线回归）

- Python：
  - `python3.11 src/python-sdk/tools/generate_sdk.py`
  - `PYTHONPATH=src/python-sdk python3.11 -m pytest -q src/python-sdk/tests`
- TypeScript：
  - `cd src/typescript-sdk`
  - `npm test`
