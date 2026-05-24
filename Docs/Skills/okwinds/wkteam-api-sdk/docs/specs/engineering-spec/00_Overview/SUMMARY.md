# Engineering Specification Summary — wkteam `api-wen-dang2` SDK

## Document Info

- **Project:** `wkteam-api-sdk`
- **Version:** 1.0
- **Status:** Draft（文档优先，先规格后实现）
- **Author:** Agent
- **Last Updated:** 2026-02-10

## Executive Summary

本工程规格用于指导实现一套工程级 SDK，用于对接 `wkteam.cn` 文档子集 `api-wen-dang2` 所描述的个人号相关 API。规格以“可用”为目标：不仅要求 wrapper 全量覆盖接口，还要在鉴权、错误、重试、日志、配置、测试与发布等工程维度形成可复刻的落地方案。

本仓库当前同时交付：
- TypeScript SDK（Node.js 优先）
- Python SDK（Python 3.11）

本规格的权威输入来源为本仓库内的离线文档：`docs/api/`。

重要：`docs/api/` 为从第三方站点抓取的离线资料，**不进入开源仓库**（本地开发需自行获取并放置到该目录）。在此基础上，`docs/specs/engineering-spec/02_Technical_Design/API_SPEC.md` 与 `docs/specs/engineering-spec/02_Technical_Design/schemas/api_catalog.json` 从离线文档自动提取生成，用作覆盖性与实现清单。

## Scope

### In Scope

- API endpoint wrapper：对 `docs/api/api-wen-dang2/` 中标记为 endpoint 的文档做到全量覆盖与可追溯映射
- 统一请求/响应处理：`baseUrl` 配置、headers 注入、参数校验、响应解析
- 鉴权与会话：登录与 token 注入策略、错误识别、重登/失败策略（可配置）
- 错误模型与可靠性：网络/HTTP/业务 code/解析失败分类；超时、重试与幂等策略
- 回调（Webhook）相关：回调地址配置接口、回调 payload 的 schema/类型与去重建议
- 工程化交付：测试策略、集成冒烟、配置规范、发布/版本策略、排障手册

### Out of Scope

- GUI 控制台/后台系统
- 替平台侧重新定义账号/权限业务规则（以既有 API 行为为准）
- 新增平台侧 API（本项目仅客户端 SDK）

## Key Decisions（摘要）

| Decision | Choice | Rationale | Date |
|----------|--------|-----------|------|
| SDK 语言 | TypeScript + Python | 同一份离线文档与 catalog 驱动多语言 SDK；覆盖性门槛一致 | 2026-02-10 |
| baseUrl 处理 | 必配 + 多环境 | 文档使用 `http://域名地址` 占位，必须外置配置 | 2026-02-10 |
| 成功判定 | 默认 `code == 1000` | 文档多数接口约定；允许接口级覆盖 | 2026-02-10 |
| 重试策略 | 默认保守（副作用接口不自动重试） | 避免消息/群等接口发生副作用重放 | 2026-02-10 |

## Document Index

- `docs/specs/engineering-spec/00_Overview/`：总览、可追溯矩阵、决策日志、技术栈
- `docs/specs/engineering-spec/01_Requirements/`：用户故事、功能/非功能需求
- `docs/specs/engineering-spec/02_Technical_Design/`：SDK 架构、数据模型、API 规格、业务逻辑
- `docs/specs/engineering-spec/03_Security/`：鉴权、安全、审计（日志）
- `docs/specs/engineering-spec/04_Operations/`：配置、发布/部署、监控建议、排障
- `docs/specs/engineering-spec/05_Testing/`：测试计划、验收用例
- `docs/specs/engineering-spec/06_Implementation/`：任务拆分、里程碑、风险、迁移策略
