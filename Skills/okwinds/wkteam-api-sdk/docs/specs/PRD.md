# PRD：wkteam `api-wen-dang2` 工程级 SDK

**版本：** `1.0`  
**状态：** Draft（规格优先，先文档后实现）  
**作者：** Agent（基于离线 API 文档抽象）  
**最后更新：** 2026-02-10  
**利益相关方：** SDK 使用方开发者、接口平台运维/交付方

## 1. 背景与问题陈述（Problem Statement）

我们已从 `wkteam.cn` 抓取并离线化了 `https://wkteam.cn/api-wen-dang2/` 下的 API 说明文档（见 `docs/api/`）。当前痛点是：

- 接口数量多、分散在多级文档中（约 142 个页面），人工对接成本高，容易遗漏参数/返回值/错误码细节。
- 接口普遍要求 `Authorization` 头（来自登录接口），token 生命周期、错误语义、重试/超时等缺乏工程化封装。
- 开发者需要“可用”的 SDK：统一配置、统一错误模型、统一日志与可回归测试，避免每个项目重复造轮子。

## 2. 目标（Goals）与成功指标（Success Metrics）

### 2.1 Goals（必须达成）

1. **接口覆盖**：SDK 对 `docs/api/api-wen-dang2/` 中的每个接口/章节提供可追溯的封装（wrapper）与文档映射（覆盖性可核验）。
2. **可用性**：SDK 能完成核心链路（登录 → 通讯录 → 发消息 → 配置回调 → 下载内容/撤回等）的工程落地，不以 demo 为目标。
3. **一致性**：统一的请求构建、参数校验、错误分类、返回解析（以文档中的 `code/message/data` 结构为主）。
4. **可回归**：离线单测覆盖 SDK 关键能力；在具备真实环境时可跑集成冒烟（可显式 skip）。
5. **可复刻**：规格文档足够详细，第三方团队可在不额外沟通的情况下实现相同 SDK。

### 2.2 Success Metrics（可衡量）

- 覆盖率：`docs/api/api-wen-dang2/**/*.md`（排除 `README.md`/目录页的定义见规格）与 SDK wrapper 的映射覆盖率达到 100%。
- 稳定性：离线测试通过率 100%，且核心模块具备错误/边界用例。
- 体验指标（定性）：使用方能在 30 分钟内完成“登录 + 发送文本消息”的最小集成。

## 3. 用户与使用场景（Users & Personas）

### Persona A：业务集成开发者（Primary）

- 目标：快速集成个人号相关能力（消息、好友、群、朋友圈、视频号等）
- 技术：Node/TS 或其他后端语言开发者，具备 HTTP/JSON 基础
- 使用频率：开发期高频调用，生产期按业务触发调用
- 痛点：参数多、鉴权易错、错误处理混乱、缺少可复用的封装

### Persona B：平台交付/运维（Secondary）

- 目标：统一配置、可观测、可定位问题（请求 ID、关键日志、错误分类）
- 痛点：缺乏可观测性与一致错误语义，线上定位困难

## 4. 范围（Scope）

### 4.1 In Scope

- 针对 `api-wen-dang2` 文档子集（`/api-wen-dang2/`）的 SDK 设计与实现规格：
  - 登录与 token 管理
  - 统一 HTTP Client（超时、重试、限流/退避策略）
  - 统一错误模型（网络/HTTP/业务 code/解析失败）
  - 全量 endpoint wrapper 的模块划分、命名、参数与返回类型规范
  - Webhook/回调相关的解析与校验工具（以文档为准）
  - 文档映射与覆盖性校验机制（保证“不漏接口”）

### 4.2 Out of Scope

- 构建 GUI 控制台/后台管理系统
- 账号体系/权限体系的业务化再设计（以现有 API 行为为准）
- 对外提供新的业务 API（本项目仅作为客户端 SDK）

## 5. 功能需求（Functional Requirements）

> 注：详细拆分、编号与验收标准在工程规格的 `docs/specs/engineering-spec/01_Requirements/` 中展开。

### 5.1 基础能力

- FR-BASIC-001：SDK 支持配置 `baseUrl`（文档中的 `http://域名地址/...` 作为占位），并支持多环境（dev/staging/prod）切换。
- FR-BASIC-002：所有请求自动注入 `Authorization`（来自登录接口返回）。
- FR-BASIC-003：为每个 endpoint wrapper 提供：
  - method/path（或等价的请求 URL 组装规则）
  - 请求体/Query 结构化参数
  - 返回结构解析与类型定义
  - 参数校验（必填、类型、取值范围/格式）

### 5.2 登录与会话

- FR-AUTH-001：封装登录链路（二维码/账号密码/弹框等），并输出 token。
- FR-AUTH-002：支持显式传入 token（外部系统管理 token），SDK 仅负责使用。
- FR-AUTH-003：明确 token 失效/过期/权限不足的错误识别与重登策略（策略需可配置）。

### 5.3 业务模块（按离线文档分类）

SDK 必须覆盖并按模块组织（示例）：

- `deng-lu`（登录/通讯录初始化/通讯录查询）
- `xiao-xi-fa-song`（消息发送：文本/文件/base64/图片/视频/链接/名片/动图/app/小程序/群@/转发/撤回）
- `xiao-xi-jie-shou`（消息接收：回调配置/释义/下载内容）
- `hao-you-cao-zuo`（好友：搜索/添加/删除/备注/权限/免打扰/置顶/检测/企微好友/二维码等）
- `qun-cao-zuo`（群：创建/邀请/踢人/群公告/群待办/群列表/群详情/群二维码/昵称等）
- `peng-you-quan`（朋友圈：发文/点赞/评论/删除/下载视频/隐私等）
- `shipinhao`（视频号：关注/浏览/评论/发布/收藏/私信/登录助手等）
- `biao-qian`（标签：增删改查）
- `shou-cang-jia`（收藏夹：列表/内容/删除）
- `wei-xin-guan-li`（账户管理：下线/重连/在线状态等）
- `te-shu`（工具箱：CDN 上传下载、代理设置、流量/调用次数/掉线原因等）

## 6. 业务规则（Business Rules）

以下规则来自离线文档常见约定（以最终规格的 “API 目录/解析结果” 为准）：

- BR-001：多数接口返回字段含 `code`，其中 `1000` 表示成功，`1001` 表示失败（详见各接口文档）。
- BR-002：除登录外，多数接口需要 `Authorization` 请求头，值为登录接口返回（文档描述为 “Authorization：login接口返回”）。
- BR-003：多数接口以 `POST` + `application/json` 发送请求体。
- BR-004：部分接口涉及异步任务（例如视频下载、朋友圈视频发送结果查询），需提供轮询/结果查询辅助方法（策略可配置）。

## 7. 数据需求（Data Requirements）

SDK 需要处理/保存/传递的数据包括：

- `Authorization` token（敏感）：不得默认写入磁盘日志；需要脱敏策略
- `wId`（登录实例标识）：大量接口必填，需在 SDK 会话对象中承载
- `wcId`（微信 id/群 id 等）：大量接口必填
- 其他：图片/文件 URL、Base64 内容、消息 ID、时间戳等

## 8. 错误处理与边界场景（Error Handling & Edge Cases）

- EH-001：网络错误（DNS/连接失败/超时）应归类为 `NetworkError`，携带原始异常与请求上下文（不含敏感头）。
- EH-002：HTTP 非 2xx 归类为 `HttpError`，保留 status、响应片段（可配置截断）。
- EH-003：业务 `code != 1000` 归类为 `ApiBusinessError`，携带 `code/message/data`。
- EH-004：响应解析失败归类为 `ParseError`（例如返回非 JSON）。
- EH-005：重试策略必须可配置且默认保守（避免对“发送消息/群操作”类接口造成副作用重放）。

## 9. 非功能需求（Non-Functional Requirements）

- NFR-COMPAT-001：明确 SDK 运行环境与最低版本（例如 Node LTS）；浏览器支持与否需决策。
- NFR-SEC-001：不得在默认日志中输出 `Authorization` 原文；提供脱敏与可控 debug。
- NFR-OPS-001：提供可插拔 logger（用户可接入自身日志系统）。
- NFR-REL-001：对请求提供超时控制；对可安全重试的请求提供退避重试。

## 10. 集成与依赖（Integration Requirements）

- 集成对象：wkteam/E云平台 提供的 HTTP API（实际 baseUrl 由使用方配置）。
- 依赖：
  - HTTP 传输层（fetch/axios/undici 等，具体选型在工程规格决策日志中明确）
  - 测试框架（离线单测）

## 11. 里程碑与交付（Timeline & Milestones）

本仓库先交付规格，后交付实现：

1. M1：PRD + 工程规格文档（覆盖性审计通过）
2. M2：SDK 基础骨架与核心模块（Auth/HTTP/Error）
3. M3：按模块补齐所有 endpoint wrapper + 离线单测
4. M4：集成冒烟测试与运维文档（配置/排障/监控建议）

## 12. 风险与未决问题（Open Questions & Risks）

### 未决问题（需要在规格中明确或通过实测补齐）

1. 实际服务 baseUrl（文档使用 `http://域名地址/...` 占位）
2. `Authorization` 的格式（是否需要 `Bearer ` 前缀）
3. token 过期/刷新机制是否存在（文档未统一说明）
4. 是否存在全局/单接口限流规则

### 先行假设（为推进规格而设，需标注风险）

- A-001：`Authorization` 直接使用登录返回值原文（不自动添加前缀），如需前缀由配置控制。
- A-002：默认不对“可能产生副作用”的接口启用自动重试（或仅对网络超时做一次重试，且可配置关闭）。
