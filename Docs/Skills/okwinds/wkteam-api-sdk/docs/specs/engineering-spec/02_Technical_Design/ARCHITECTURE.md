# SDK Architecture（TypeScript / Python）

## Overview

本项目的核心目标是实现一个工程级 SDK（多语言交付）：

- 对离线文档 `docs/api/api-wen-dang2/` 的 endpoint 做全量封装（清单见 `API_SPEC.md` 与 `schemas/api_catalog.json`）
- 提供统一的 Client / 请求管线 / 错误模型 / 可观测性 / 测试策略
- 允许使用方自主管理运行环境（baseUrl、token、代理、日志、超时、重试）

## High-level Diagram

```mermaid
flowchart TD
  App[User App] --> SDK[SDK Client]
  SDK --> Pipeline[Request Pipeline]
  Pipeline --> Transport[HTTP Transport (fetch or injected)]
  Transport --> API[(wkteam API baseUrl)]

  SDK --> Auth[Auth/Session]
  SDK --> Modules[Endpoint Modules]
  SDK --> Webhook[Webhook Parser/Types]

  Modules --> Pipeline
  Auth --> Pipeline
```

## Repo Layout（目标结构）

> 说明：此处是“实现阶段”的目标结构，用于指导落地与拆分；当前阶段以规格文档为主。

> 更新：源码已按技术栈收敛到 `src/typescript-sdk/` 与 `src/python-sdk/`；以下仍以“组件层次”描述 TypeScript SDK 的内部结构。

- `src/typescript-sdk/src/`
  - `core/`
    - `config/`：配置结构、默认值、环境变量映射（集成测试）
    - `http/`：transport 接口、超时、重试、请求构建、响应解析
    - `errors/`：统一错误类型与序列化
    - `logging/`：logger 接口、脱敏、请求上下文
  - `auth/`
    - `session.ts`：Authorization token 与（可选）wId 的会话对象
    - `memberLogin.ts`：`/member/login` 等登录接口封装
    - `wechatLogin.ts`：二维码/微信登录相关封装（按离线文档模块拆分）
  - `modules/`（按离线文档模块拆分）
    - `dengLu/`、`xiaoXiFaSong/`、`xiaoXiJieShou/`、`haoYouCaoZuo/`、`qunCaoZuo/`、`pengYouQuan/`、`shipinHao/`、`biaoQian/`、`shouCangJia/`、`weiXinGuanLi/`、`teShu/`
  - `webhook/`
    - `types.ts`：回调 payload 类型（见 `docs/api/.../callback.md`）
    - `parse.ts`：解析与校验辅助（不含存储去重实现，但提供建议与 hook）
- `src/typescript-sdk/tools/`
  - `generate_api_artifacts.mjs`：从离线文档生成 `api_catalog.json` 与 `API_SPEC.md`（保证覆盖性）

## Key Components

| Component | Purpose | Contract | Notes |
|----------|---------|----------|------|
| `SDKClient` | SDK 总入口；承载配置、会话、模块 | `createClient(config)` | 允许注入 transport/logger |
| Request Pipeline | 统一请求处理：校验→构建→发送→解析→错误 | `request(operationId, spec, input)` | 支持中间件/钩子 |
| Transport | 发送 HTTP 请求 | `transport(request) -> response` | 默认 `fetch`，可注入 |
| Error Model | 统一错误分类与上下文 | `NetworkError/HttpError/...` | 默认不泄露 token |
| API Catalog | endpoint 清单与映射 | `schemas/api_catalog.json` | 由离线文档生成 |
| Webhook Types/Parser | 回调 payload 类型与解析 | `parseCallback(payload)` | 去重策略由使用方实现 |

## Communication Model

| From | To | Protocol | Pattern | Auth |
|------|----|----------|---------|------|
| User App | SDK | in-process | sync/async | - |
| SDK | wkteam API | HTTP(S) + JSON | synchronous request/response | header `Authorization`（多数接口） |
| wkteam API | User Webhook | HTTP POST JSON | async callback | 由用户提供公网 URL（文档约定） |

## Naming & Module Conventions

### operationId

- operationId 来源：`module + fileStem`（见 `schemas/api_catalog.json` 的 `operationId`）
- 作用：
  - 日志标识（哪个接口）
  - 错误上下文（trace）
  - 测试用例命名（可追溯）

### 文件/函数命名

- module 名尽量与离线文档目录一致（例如 `xiao-xi-fa-song` → `xiaoXiFaSong`）
- wrapper 函数名优先使用文档中的 endpoint 名或文件名（例如 `sendFile`、`revokeMsg`）

## Extensibility（扩展点）

- **transport 注入**：支持 axios/undici/代理等
- **logger 注入**：对接 pino/winston/自研日志
- **retry policy 注入**：全局与 endpoint 级策略覆盖
- **success 判定覆盖**：当发现某 endpoint 与默认 `code==1000` 不一致时可覆盖
