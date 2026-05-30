# User Stories

> 说明：用户故事面向“SDK 使用方开发者”。每条故事在实现阶段会拆到更细的任务与测试用例。

## US-001：创建客户端并配置环境

**Priority:** P0 | **Status:** Draft

**Story:** 作为 SDK 使用方开发者，我希望能用少量配置创建客户端（baseUrl、token、logger、timeout），从而快速开始调用接口并可控地在不同环境运行。

**Acceptance Criteria:**

```gherkin
Given 我有 baseUrl 与（可选）Authorization token
When 我创建 SDK Client
Then Client 能在调用任意 endpoint 时正确拼装 URL 并注入 headers
And 当缺少必需配置时应在本地抛出可读错误（不发出请求）
```

**Dependencies:** -

## US-002：登录并获取 Authorization

**Priority:** P0 | **Status:** Draft

**Story:** 作为 SDK 使用方开发者，我希望通过 SDK 封装登录接口获取 Authorization，从而避免手写请求与解析。

**Acceptance Criteria:**

```gherkin
Given 我提供账号/密码（或二维码登录所需参数）
When 我调用登录 wrapper
Then 我得到 Authorization 并可用于后续请求
And 登录失败时能得到结构化错误（包含业务 code/message）
```

**Business Rules:** BR-001, BR-002

## US-003：全量 endpoint wrapper 可追溯覆盖

**Priority:** P0 | **Status:** Draft

**Story:** 作为 SDK 使用方开发者，我希望 SDK 覆盖离线文档中的所有 endpoint，并能追溯到对应文档路径，从而降低遗漏与维护成本。

**Acceptance Criteria:**

```gherkin
Given 离线文档目录 docs/api/api-wen-dang2/
When 我查看 SDK 的 endpoint catalog
Then 每个 endpoint 文档都能映射到一个 wrapper（operationId）
And 对非 endpoint 文档（目录页/参考页）也有明确处理方式（忽略/类型/工具）
```

## US-004：统一错误模型与重试策略

**Priority:** P0 | **Status:** Draft

**Story:** 作为 SDK 使用方开发者，我希望所有接口失败都以统一 error 类型表达，并具备可配置的超时与重试策略，从而在工程上可控。

**Acceptance Criteria:**

```gherkin
Given 任意一次请求失败（网络/HTTP/业务 code/解析）
When SDK 抛出错误
Then 错误类型可区分并携带足够上下文（但不泄露 Authorization）
And 默认策略不对有副作用接口自动重试
```

## US-005：消息发送（多类型）

**Priority:** P0 | **Status:** Draft

**Story:** 作为 SDK 使用方开发者，我希望用统一接口发送文本/图片/文件/链接/小程序等消息，从而减少不同消息类型的重复逻辑。

**Acceptance Criteria:**

```gherkin
Given 我选择一种消息类型并提供必要参数（wId/wcId/...）
When 我调用对应 wrapper
Then 请求参数按文档要求发送
And 返回中能拿到 msgId/newMsgId/createTime 等关键字段
```

## US-006：消息接收与回调 payload 解析

**Priority:** P0 | **Status:** Draft

**Story:** 作为 SDK 使用方开发者，我希望 SDK 能提供回调 payload 的类型定义与解析辅助（含去重建议），从而安全可靠地消费回调消息。

**Acceptance Criteria:**

```gherkin
Given 平台向我的回调地址 POST JSON
When 我使用 SDK 的回调解析器
Then 能得到类型化结构（messageType/data/...）
And 文档提示的重复推送场景有明确去重策略建议
```

## US-007：好友与通讯录操作

**Priority:** P1 | **Status:** Draft

**Story:** 作为 SDK 使用方开发者，我希望能搜索/添加/删除好友，获取通讯录与详情，从而支撑 CRM/机器人业务。

## US-008：群管理操作

**Priority:** P1 | **Status:** Draft

**Story:** 作为 SDK 使用方开发者，我希望能创建群、邀请/踢人、查群列表/详情/二维码等，从而实现群运营自动化。

## US-009：朋友圈能力

**Priority:** P2 | **Status:** Draft

**Story:** 作为 SDK 使用方开发者，我希望能发送/获取/点赞/评论朋友圈，并处理异步结果，从而实现社交自动化。

## US-010：视频号能力

**Priority:** P2 | **Status:** Draft

**Story:** 作为 SDK 使用方开发者，我希望能对视频号执行关注/评论/私信/发布等操作，从而实现内容运营自动化。

## US-011：标签/收藏夹/工具箱

**Priority:** P2 | **Status:** Draft

**Story:** 作为 SDK 使用方开发者，我希望能对标签与收藏夹做增删改查，并使用工具箱接口（CDN 上传下载、代理设置等），从而完善周边能力。
