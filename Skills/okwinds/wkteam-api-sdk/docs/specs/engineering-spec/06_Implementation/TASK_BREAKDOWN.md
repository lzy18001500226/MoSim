# Task Breakdown（实现任务拆解）

> 说明：本章节把工程规格落到可执行任务。  
> 约束：任务拆解不是一次性文档；实现过程中允许细化，但必须保持 **可追溯**（US/FR → TASK）。

## 任务约定

- ID 格式：`TASK-XXX`
- 每个任务必须声明：实现哪些需求（US/FR）、验收方式（测试/脚本/人工 check）、以及依赖关系
- 与 API 覆盖相关的任务必须引用：
  - `docs/specs/engineering-spec/02_Technical_Design/schemas/api_catalog.json`
  - `docs/specs/engineering-spec/02_Technical_Design/API_SPEC.md`

---

## M1：仓库与基础 SDK 骨架（P0）

### TASK-001：初始化 SDK 工程骨架
**Implements:** US-001 | **Estimate:** 4h | **Phase:** M1

**Description:**
- 建立 `src/` 基础结构（client、transport、errors、types、modules）
- 配置 TypeScript（strict）、Vitest、lint/format（若选择）

**Definition of Done:**
- [ ] `pnpm test` 可运行（即使只有占位测试）
- [ ] `pnpm build` 产生 dist（可先最小可用）
- [ ] `README.md` 有最小安装与使用示例

### TASK-002：实现配置模型与校验
**Implements:** US-001, FR-BASIC-001/002 | **Estimate:** 6h | **Phase:** M1

**Description:**
- 定义 `WkteamClientConfig` 类型
- 实现初始化校验（`ValidationError`）
- 支持 `authorization` 为字符串或函数（sync/async）

**Done Criteria:**
- [ ] 单测覆盖：缺失 baseUrl/authorization 的失败；prefix 逻辑；headerName 逻辑

### TASK-003：实现 transport 抽象（fetch 默认 + 可注入）
**Implements:** ADR-002, FR-BASIC-003 | **Estimate:** 8h | **Phase:** M1

**Description:**
- 设计 `TransportRequest/TransportResponse`（见 `DATA_MODEL.md`）
- 默认 fetch transport：超时（AbortController）、JSON body、header 归一化
- 支持注入自定义 transport（用于 mock 与特殊网络）

**Done Criteria:**
- [ ] 单测覆盖：超时、非 2xx、网络错误映射

### TASK-004：统一错误模型与解析器
**Implements:** ADR-003, US-007 | **Estimate:** 10h | **Phase:** M1

**Description:**
- 实现错误类型：`NetworkError/TimeoutError/HttpError/ApiBusinessError/ParseError/ValidationError`
- 实现 envelope 解析：`code/message/msg/data`
- 默认成功判定 `code==1000`，预留 endpoint 覆盖点

**Done Criteria:**
- [ ] 单测覆盖：各种错误映射与字段完整性（含 requestId/operationId）

### TASK-005：日志、hook 与脱敏
**Implements:** US-007, `04_Operations/MONITORING.md` | **Estimate:** 8h | **Phase:** M1

**Description:**
- 结构化日志事件
- hook：onRequest/onResponse/onRetry/onError
- header 与 body 脱敏（至少 Authorization）

**Done Criteria:**
- [ ] 单测覆盖：日志不包含 token 原文；hook 输入已脱敏

---

## M2：API 覆盖与模块化封装（P0）

### TASK-006：固化 API Catalog → SDK 模块命名规则
**Implements:** US-008 | **Estimate:** 4h | **Phase:** M2

**Description:**
- 明确 module → client 子模块命名（例如 `deng-lu` → `auth` 或保留拼音）
- 明确 operationId → 方法名规则（snake_case → camelCase）
- 在代码中导出稳定 manifest（operationId 列表）

**Done Criteria:**
- [ ] 文档（spec/README）写清规则
- [ ] 单测为规则提供覆盖（输入样例 → 输出方法名）

### TASK-007：实现 endpoint wrapper 生成或批量封装机制
**Implements:** US-003/US-005/US-006/US-008 | **Estimate:** 16h | **Phase:** M2

**Description:**
- 选择实现策略（二选一，需 ADR 确认）：
  - A) 自动生成 TS 方法（由 catalog 驱动）
  - B) 运行时通用 `request(operationId, params)` + 手写薄封装
- 无论策略，必须能确保 127 endpoints 不遗漏，并可持续维护

**Done Criteria:**
- [ ] 能调用至少 3 个模块的 representative endpoint（离线 fake transport）
- [ ] 覆盖性测试（AT-008）可执行并通过

### TASK-008：实现代表性模块（先 P0 再铺开）
**Implements:** US-002/003/005 | **Estimate:** 24h | **Phase:** M2

**Description:**
- 先落地 P0 模块（建议）：登录（`deng-lu`）、消息发送（`xiao-xi-fa-song`）、消息接收参考（`xiao-xi-jie-shou`）
- 再逐步扩展：好友、群、朋友圈、视频号、标签、收藏夹、特殊接口

**Done Criteria:**
- [ ] 每个模块至少 1 个单元测试覆盖请求构造与响应解析

---

## M3：回调与异步任务 helper（P1）

### TASK-009：回调 payload 解析与去重 key helper
**Implements:** US-004 | **Estimate:** 10h | **Phase:** M3

**Description:**
- 根据 reference 文档实现 `callbacks.parse()` 与 `callbacks.dedupKey()`
- 提供最小 in-memory deduper（可选），明确其局限性

**Done Criteria:**
- [ ] AT-005 可落地并通过

### TASK-010：轮询 helper（异步接口）
**Implements:** `02_Technical_Design/BUSINESS_LOGIC.md` | **Estimate:** 6h | **Phase:** M3

**Description:**
- 实现 `pollUntil`，支持超时/最大次数/可取消
- 提供示例：异步发送朋友圈/下载等（离线 stub）

---

## M4：集成验证与发布（P1）

### TASK-011：集成 smoke（可选）
**Implements:** AT-009 | **Estimate:** 6h | **Phase:** M4

**Description:**
- 增加 integration 测试开关（`WKTEAM_INTEGRATION=1`）
- 提供只读/低风险 endpoint 的 smoke 列表（可配置）

### TASK-012：发布流程与文档收尾
**Implements:** `04_Operations/DEPLOYMENT.md` | **Estimate:** 6h | **Phase:** M4

**Description:**
- 补齐 `.env.example`
- 补齐 CHANGELOG（若采用）
- 确保 release gate 可复现并在 worklog 记录

**Done Criteria:**
- [ ] 任何人可按 README 在新环境完成 build/test

---

## M5：Python SDK（Python 3.11）交付（P0）

> 说明：本里程碑在 TypeScript SDK 的基础上，交付同一套 API 的 Python SDK。
> 覆盖性门槛与权威输入不变：`docs/api/` + `schemas/api_catalog.json`。

### TASK-013：初始化 Python SDK 工程骨架（src/python-sdk/）

**Implements:** ADR-006 | **Estimate:** 6h | **Phase:** M5

**Description:**
- 新增 `src/python-sdk/pyproject.toml`（依赖版本固定）
- 新增 `src/python-sdk/wkteam_api_sdk/`（唯一源码目录，满足“收敛到一个源代码文件夹”要求）
- 新增 `src/python-sdk/tests/`（pytest 离线回归）
- README 写清安装/使用/开发命令

**Definition of Done:**
- [ ] `python -m venv` + `pip install -e "src/python-sdk[dev]"` 可用（或进入 `src/python-sdk/` 执行 `pip install -e ".[dev]"`）
- [ ] `pytest` 可运行（即使只有占位测试）

### TASK-014：实现 Python 版 codegen（catalog → wrappers/manifest）

**Implements:** ADR-005, ADR-006, US-008 | **Estimate:** 10h | **Phase:** M5

**Description:**
- 从 `docs/specs/engineering-spec/02_Technical_Design/schemas/api_catalog.json` 生成：
  - `src/python-sdk/wkteam_api_sdk/manifest.py`（operationIds + endpointDefs）
  - `src/python-sdk/wkteam_api_sdk/generated_api.py`（模块化 wrapper：`client.api.*`）
- 生成输出必须稳定（同输入同输出）

**Done Criteria:**
- [ ] 运行 codegen 后，Python SDK 可以导入并创建 client
- [ ] 生成的 `operation_ids` 数量与 catalog 一致（127）

### TASK-015：实现 Python Core Client（transport/重试/错误/解析/脱敏/hook）

**Implements:** ADR-002/003/004/006, US-001, US-007 | **Estimate:** 16h | **Phase:** M5

**Description:**
- httpx 默认 transport（sync/async）+ 可注入 fake transport
- envelope 解析（`code/message/msg/data`）+ 默认成功规则 `code==1000`
- 分类重试（safe vs side_effect），与 TS 规则一致
- 日志与 hook 事件（脱敏后输出）

**Done Criteria:**
- [ ] 离线单测覆盖：网络错误/超时/HTTP 非 2xx/business error/解析失败
- [ ] 默认不泄露 `Authorization` 原文（日志与 hook）

### TASK-016：实现 Python 覆盖性护栏（AT-008）与代表性场景

**Implements:** AT-001/002/006/008 | **Estimate:** 10h | **Phase:** M5

**Description:**
- pytest：读取 `api_catalog.json` 与 `wkteam_api_sdk.manifest.operation_ids` 做集合对比
- fake transport：遍历 endpointDefs 做 method/path contract smoke
- 重试门槛：safe 可重试、side_effect 默认不重试

**Done Criteria:**
- [ ] `pytest` 离线回归通过
- [ ] 覆盖性 gate 阻断“接口漏实现”
