# Deployment Specification（SDK 发布与交付）

> 说明：本项目包含 **TypeScript（npm）SDK** 与 **Python（pip）SDK**；不存在“服务部署/回滚数据库迁移”等传统运维动作。
> 本章节定义的是：**构建产物**、**发布流程**、**版本策略**、以及发布前的验证门槛。

## 1. 交付物（Artifacts）

实现阶段必须产出以下构建产物（用于最大化兼容性与可用性）：

| Artifact | Path（建议） | 目标 | 说明 |
|---|---|---|---|
| ESM bundle | `src/typescript-sdk/dist/esm/` | Node ESM / Bundlers | 默认现代项目使用 |
| CJS bundle | `src/typescript-sdk/dist/cjs/` | 旧 Node / 部分工具链 | 兼容性兜底 |
| Type declarations | `src/typescript-sdk/dist/types/` | TypeScript | 必须与运行时代码一致 |
| Source map | `src/typescript-sdk/dist/**/*.map` | 调试 | 便于定位线上问题 |

`package.json` 必须提供合理的 `exports` 映射（示例约束，具体实现可调整）：
- `import` → ESM
- `require` → CJS
- `types` → d.ts

## 2. 版本与兼容策略（SemVer）

| 变更类型 | 版本策略 | 示例 |
|---|---|---|
| 修复 bug / 文档更正（不改变对外行为） | `PATCH` | 解析规则修复、不影响类型签名 |
| 新增 endpoint wrapper / 新增可选配置 | `MINOR` | 新增 `client.messages.sendVoice()` |
| 破坏性变更 | `MAJOR` | 变更错误模型字段/导出路径/默认重试策略 |

**兼容承诺（实现阶段必须落实并写入 README）：**
- Node.js：支持 `>= 18.18`（建议 20 LTS），并在 CI 做矩阵测试（18/20）
- TS 类型：`strict` 模式下可用（不要求使用方开启 strict，但 SDK 自身应保持类型严谨）

## 3. 发布前验证门槛（Release Gate）

每次发布必须满足以下条件（即使手工发布也必须逐项执行并记录到 `docs/worklog.md`）：

1) **API 文档覆盖物更新**
   - 运行：`cd src/typescript-sdk && npm run generate:api`
   - 确认 `docs/specs/engineering-spec/02_Technical_Design/API_SPEC.md` 与 catalog 已更新
2) **规格完整性校验**
   - 运行：`bash /Users/okwinds/.claude/skills/prd-to-engineering-spec/scripts/validate_spec.sh docs/specs/engineering-spec`
3) **质量门槛（实现后启用）**
   - lint/typecheck 通过
   - 单元测试（离线回归）全部通过
   - 覆盖率门槛：核心模块（transport/error/serialization/catalog）必须高覆盖（详见 `05_Testing/TEST_PLAN.md`）
4) **安全门槛**
   - 确认不会打印 `Authorization` 等敏感信息（脱敏测试必须通过）
   - `npm pack` 产物中不包含 `.env`、日志、临时文件

## 4. 推荐 CI/CD Pipeline（可迁移模板）

> 这里给出“推荐流水线阶段”，不绑定具体平台（GitHub Actions/GitLab CI/Jenkins 均可）。

| Stage | 目标 | Trigger | Failure Action |
|---|---|---|---|
| `validate-docs` | 生成覆盖物 + spec 校验 | PR / push | 阻断合并 |
| `lint` | 代码风格/静态检查 | PR / push | 阻断合并 |
| `typecheck` | TS 类型检查 | PR / push | 阻断合并 |
| `unit-test` | 离线回归 | PR / push | 阻断合并 |
| `build` | 打包 ESM/CJS/types | PR / push | 阻断合并 |
| `integration-test`（可选） | 真实环境连通性 | 手动/带密钥分支 | 仅告警（不阻断默认 CI） |
| `publish` | 发布 npm 包 | tag / release | 失败则禁止继续发版并告警 |

## 5. 回滚与事故处置（SDK 场景）

npm 包无法真正“回滚线上服务”，但需要可操作的处置策略：

- 若发布版本存在严重 bug：
  - 立即在 npm 上执行 `npm deprecate <pkg>@<version> "<message>"`（提示升级/降级建议）
  - 发布 `PATCH` 修复版本，并在 `CHANGELOG`/release note 中标记影响面
- 若破坏性变更误发到 `MINOR/PATCH`：
  - 立刻发布 `MAJOR` 或更正版本，并在 README 顶部醒目标注迁移指引

## 6. 本地交付与复现命令（实现阶段必须可用）

实现完成后，以下命令必须在全新环境可复现（并写入 `README.md`）：
- TypeScript SDK：
  - 安装依赖：`cd src/typescript-sdk && npm i`
  - 生成覆盖物：`cd src/typescript-sdk && npm run generate:api`
  - 生成 SDK：`cd src/typescript-sdk && npm run generate:sdk`
  - 运行单元测试：`cd src/typescript-sdk && npm test`
  - 构建：`cd src/typescript-sdk && npm run build`
- Python SDK：
  - 生成 SDK：`python3.11 src/python-sdk/tools/generate_sdk.py`
  - 运行单元测试：`PYTHONPATH=src/python-sdk python3.11 -m pytest -q src/python-sdk/tests`

## 7. 开发环境（environment）与可选容器化

### 7.1 开发环境要求

最低要求：
- Node.js `>= 18.18`（建议 20 LTS）
- 包管理器：实现阶段确定并统一（当前实现使用 npm；也可迁移到 pnpm 但需同步文档与 lockfile）

实现阶段需要在 `README.md` 中提供“从零开始”的 environment setup：
- 安装 Node 与包管理器
- 安装依赖、运行测试、构建
- 可选：启用 integration smoke（不包含密钥）

### 7.2 Docker / Container（可选）

本项目作为 SDK **不需要** runtime docker 镜像交付；但为了让贡献者获得一致环境，允许提供以下可选项（二选一即可）：
- `devcontainer`（VS Code Dev Containers）
- `Dockerfile`（仅用于开发/CI 环境复现：安装依赖、跑测试、构建）

关键词（供校验脚本检索）：docker|container

> 约束：任何容器化方案不得内置密钥；必须只依赖 `.env.example` 描述配置项。
