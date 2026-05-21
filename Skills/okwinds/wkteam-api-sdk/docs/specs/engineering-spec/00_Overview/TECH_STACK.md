# Technology Stack（SDK 仓库）

> 说明：本项目是“客户端 SDK”，不包含服务端数据库/缓存等组件；Operations 章节主要描述发布与集成测试的工程化方案。

> 更新（2026-02-10）：仓库将同时交付 TypeScript SDK 与 Python SDK（Python 3.11），两者共享同一份离线 API 文档与 `api_catalog.json` 作为权威输入。

| Layer | Technology | Version | Rationale | Alternatives Considered |
|-------|-----------|---------|-----------|------------------------|
| Language | TypeScript | 5.x | 类型系统适合大接口面维护与回归 | Java / Python / Go |
| Runtime | Node.js | >= 18.18（建议 20 LTS） | Node18+ 原生 `fetch` 可用；便于工具链 | Deno / Bun |
| HTTP | `fetch`（可注入实现） | Node 内置 | 避免强绑 axios；便于在不同运行时复用 | axios / undici 直接使用 |
| Testing | Vitest | 固定版本（实现阶段锁定） | 单测快，适合库项目 | Jest / Node test |
| Build | tsup（基于 esbuild） | 固定版本（实现阶段锁定） | 一条命令输出 ESM/CJS/types | rollup |
| Lint/Format | Biome（可选） | 固定版本（实现阶段锁定） | 单工具覆盖 lint+format | ESLint+Prettier |
| Schema/Validation | Zod | 固定版本（实现阶段锁定） | 用于参数校验与类型推导（尤其适合 codegen） | 手写校验 |

## Python SDK（Python 3.11）

> 目标：提供“工程可用”的 Python SDK，与 TypeScript SDK 在 **endpoint 覆盖**、**错误模型**、**重试/幂等风险控制**、**可观测性（hook/日志脱敏）** 上保持一致；并复用同一份 `api_catalog.json` 做覆盖性门槛（AT-008）。

| Layer | Technology | Version | Rationale | Alternatives Considered |
|-------|-----------|---------|-----------|------------------------|
| Language | Python | 3.11 | 兼顾类型注解与运行时稳定；符合用户要求 | 3.10 / 3.12 |
| HTTP | httpx | 固定版本（实现阶段锁定） | 同时支持 sync/async；API 设计适合库项目；易注入/替换 | requests（仅 sync）/ aiohttp（仅 async） |
| Testing | pytest | 固定版本（实现阶段锁定） | 生态成熟；断言表达清晰；适合离线回归与覆盖性护栏 | unittest |
| Async Testing | pytest-asyncio | 固定版本（实现阶段锁定） | 覆盖 async client 的离线回归 | anyio 原生 |
| Lint/Format | ruff（可选） | 固定版本（实现阶段锁定） | 单工具覆盖 lint+format；降低维护成本 | black + flake8 |
| Build/Packaging | setuptools | 固定版本（实现阶段锁定） | 兼容性最好；PEP 621 元数据；支持 editable 安装 | hatchling / poetry |

## External Dependencies（实现阶段锁定）

> 约束：为保证可复现，核心依赖必须在 `package.json` 中锁定到具体版本（不使用 `^` 漂移）。

| Dependency | Purpose | Version Pinned | License | Risk |
|-----------|---------|---------------|---------|------|
| `typescript` | 编译 | Y | - | Low |
| `vitest` | 单测 | Y | - | Low |
| `tsup` | 构建打包 | Y | - | Low |
| `zod` | 运行时参数校验/类型推导 | Y | - | Low |
| `@biomejs/biome`（可选） | lint/format | Y | - | Low |

> Python SDK 的依赖锁定策略：使用 `src/python-sdk/pyproject.toml` 的 `dependencies` / `optional-dependencies` 固定版本（不使用宽松区间），以实现“同环境可复现”。
