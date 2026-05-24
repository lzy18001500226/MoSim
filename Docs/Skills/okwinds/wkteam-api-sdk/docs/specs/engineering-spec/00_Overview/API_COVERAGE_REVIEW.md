# API Coverage Review（对照离线 API 文档的覆盖复盘）

> 目标：回答“这套工程规格是否已全面覆盖离线 API 说明文档，足以实现一个可用 SDK？”  
> 结论必须可证据化：以生成物与索引为证据，明确剩余不确定点与闭环方式。

## 1. 证据来源（Source of Truth）

- 离线文档根目录：`docs/api/api-wen-dang2/`
- 文档索引：`docs/api/SUMMARY.md`
- 解析生成的 catalog：`docs/specs/engineering-spec/02_Technical_Design/schemas/api_catalog.json`
- 全量 endpoint 清单（生成）：`docs/specs/engineering-spec/02_Technical_Design/API_SPEC.md`
- 覆盖率报告（生成）：`docs/specs/engineering-spec/00_Overview/API_DOC_COVERAGE.generated.md`

> 规则：当“解析结果”与“原文文档”不一致时，以 `docs/api/` 原文为准，并修复解析规则与生成物。

## 2. 覆盖统计（What we have）

来自 `API_DOC_COVERAGE.generated.md` 的统计（以最后一次生成时间为准）：
- markdown 文件总数：142
- catalog 条目：142
- endpoint 条目：127（method + path 均可解析）
- 非 endpoint 文档：目录类/说明类（category/reference）

**结论（覆盖面）：**
- “接口清单维度”已具备：所有 endpoint 都在 `API_SPEC.md` 表格中具备 `module + operationId + method + path + doc` 五要素，可用于实现与测试的输入。
- “不漏接口”的工程闭环已在规格中定义：`05_Testing/TEST_PLAN.md` 要求实现 manifest 校验（US-008/AT-008）。

## 3. 规格文档对照（Spec ↔ Docs）

本项目的“覆盖”不仅是列出 endpoint，还包括让 SDK 在工程上可用：鉴权、错误、重试、脱敏、回调、测试门槛等。

### 3.1 Endpoint 层（method/path + wrapper）

- 证据：`docs/specs/engineering-spec/02_Technical_Design/API_SPEC.md`
  - 每个 endpoint 有唯一 `operationId` 与 doc 路径
  - SDK 实现阶段以此为“全量清单”，并通过 AT-008 做覆盖性门槛
- 设计约束：
  - wrapper 必须至少做到：参数校验、请求构造、响应解析、错误映射
  - wrapper 命名稳定（避免升级破坏）——见 `06_Implementation/TASK_BREAKDOWN.md`（TASK-006）

### 3.2 全局契约（baseUrl / Authorization / 成功判定）

离线文档在全局约定上存在“占位/隐含契约”：
- `baseUrl`：文档写 `http://域名地址/...` 占位
- `Authorization`：多数接口需要，但前缀/生命周期未明确
- 成功判定：常见 `code==1000`，失败 `1001`，但字段（`message`/`msg`）可能不一致

对应的工程规格落点：
- `03_Security/AUTH_DESIGN.md`：鉴权注入策略与不确定点
- `04_Operations/CONFIGURATION.md`：baseUrl/prefix 可配置、校验要求
- `02_Technical_Design/BUSINESS_LOGIC.md`：success rule、字段兼容与 endpoint 覆盖点
- `05_Testing/TEST_PLAN.md`：这些规则必须通过离线回归固定下来

### 3.3 错误、重试与副作用控制（工程可用的关键）

离线文档通常不系统描述错误分类与重试风险；SDK 必须补齐：
- `ADR-003`：错误分层模型（网络/HTTP/业务/解析/校验）
- `ADR-004`：分类重试（避免副作用重放）
- `04_Operations/MONITORING.md`：结构化日志与 hook，便于上层监控
- `04_Operations/RUNBOOK.md`：排查手册（用户/维护者）

### 3.4 回调（消息接收）说明文档（reference 类）

离线文档中存在 callback 说明（属于“不是 endpoint 的协议文档”）：
- SDK 需要提供：payload parse、dedupKey、参考去重策略
- 规格落点：
  - `02_Technical_Design/DATA_MODEL.md`（payload 类型）
  - `02_Technical_Design/BUSINESS_LOGIC.md`（dedup 规则）
  - `05_Testing/TEST_PLAN.md` 与 `05_Testing/ACCEPTANCE_TESTS.md`（AT-005）

## 4. 当前仍不确定/需要集成验证的点（Gaps）

这些点不影响“离线回归 + SDK 结构落地”，但会影响“真实可用性”。必须在实现阶段通过集成 smoke 或与平台方确认闭环：

1) **真实 baseUrl 形态**
   - 是否存在固定前缀 path（例如 `/openApi` 之类）
2) **Authorization 格式**
   - 是否需要 `Bearer ` 前缀或其他 scheme
3) **token 生命周期与失效表现**
   - 过期后是 HTTP 401 还是业务 `code!=1000`，是否可刷新
4) **限流/风控策略**
   - 是否存在 QPS/并发限制、429 表现、封禁阈值
5) **幂等机制**
   - 上游是否支持幂等 key（尤其是消息发送/群操作）
6) **文件上传/下载类接口的真实 payload 形态**
   - 文档参数字段是否需要 base64、URL、还是 multipart（需要实际验证）
7) **回调安全性**
   - 是否存在签名/验签字段（当前离线文档未体现时，SDK 不应自创协议）

闭环机制（已在规格中定义）：
- `04_Operations/CONFIGURATION.md` 提供可配置项（baseUrl/prefix/timeout/retry/concurrency）
- `05_Testing/TEST_PLAN.md` 提供 `WKTEAM_INTEGRATION=1` 的可选集成 smoke
- 风险登记：`06_Implementation/RISKS.md`

## 5. 结论（能否实现“API 可用”的 SDK）

**规格覆盖性结论：通过（Pass with integration gaps）。**

理由：
- endpoint 清单完整且可用于“覆盖性门槛”自动化（127 endpoints 不漏）
- SDK 工程关键面（配置/鉴权/错误/重试/脱敏/回调/测试/发布）均有明确落点与验收要求
- 不确定点被显式识别并纳入集成验证与风险管理，而非隐藏在实现里

下一步（实现前的最小确认项）：
- 确认真实 `baseUrl` 与 `Authorization` scheme（2 项）
- 选定 endpoint wrapper 的规模化实现策略（生成 vs 通用 request + 薄封装），并补充 ADR（1 项）
