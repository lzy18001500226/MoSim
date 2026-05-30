# wkteam-api-sdk

本仓库基于api离线文档，交付一套 **工程可用** 的 SDK：

- 以 `docs/api/` 为权威输入（离线 Markdown）
- 以 `docs/specs/engineering-spec/` 为可复刻级工程规格（Spec-Driven）
- 以各 SDK 目录内的生成器保证 **127 个 endpoint 不漏**（codegen + 覆盖性测试）
- 以各 SDK 目录内的离线回归作为“功能完成”的门槛（TDD）

当前交付形态：
- TypeScript SDK（Node.js 优先）：`src/typescript-sdk/`
- Python SDK（Python 3.11）：`src/python-sdk/`

## 安装（本地使用）

本仓库未发布到 npm / PyPI 时，可用本地路径安装：

### TypeScript SDK（Node.js）

```bash
npm i ../wkteam-api-sdk/src/typescript-sdk
```

### Python SDK（Python 3.11）

在仓库根目录执行（推荐虚拟环境）：

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e "src/python-sdk[dev]"
```

> 说明：`node_modules/` 与 `dist/` 属于本地安装/构建产物；Python 的 `.venv/`、缓存目录同理，均不作为仓库存档内容（可随时通过命令重建）。

## 使用示例

### TypeScript SDK

```ts
import { createClient } from "wkteam-api-sdk";

const client = createClient({
  baseUrl: "https://你的域名或网关前缀",
  authorization: "你的 Authorization（平台登录返回）",
  // authorizationPrefix: "Bearer ", // 如果平台需要前缀才打开
});

// 全量 API wrapper 入口：client.api.<模块>.<方法>()
// 模块名由离线文档目录推导，例如 `deng-lu` -> `dengLu`
const result = await client.api.dengLu.memberLogin({
  account: "xxx",
  password: "xxx",
});
console.log(result);
```

> 注意：`baseUrl` 与 `authorization` 需要你在真实环境中自行提供；SDK 不内置这些常量。

### Python SDK（同步）

```py
from wkteam_api_sdk import WkteamClient

# 典型用法：把 Authorization 做成 callable，便于后续你拿到 token 后“原地生效”
token_box = {"value": "YOUR_AUTH_TOKEN"}

client = WkteamClient(
    base_url="https://你的域名或网关前缀",
    authorization=lambda: token_box["value"],
    # authorization_prefix="Bearer ",  # 如果平台需要前缀才打开
)

# 全量 API wrapper 入口：client.api.<模块>.<方法>()
# 模块名由离线文档目录推导，例如 `deng-lu` -> `deng_lu`
res = client.api.deng_lu.member_login(account="xxx", password="xxx")
print(res)
```

### Python SDK（异步）

```py
import asyncio
from wkteam_api_sdk import AsyncWkteamClient


async def main() -> None:
    client = AsyncWkteamClient(
        base_url="https://你的域名或网关前缀",
        authorization="YOUR_AUTH_TOKEN",
    )

    res = await client.api.biao_qian.get_contact_label_list(wId="...")
    print(res)


asyncio.run(main())
```

## 如何从离线文档定位到 SDK 方法

权威离线文档在 `docs/api/api-wen-dang2/`，每个接口 Markdown 里会有 `请求URL`、`请求方式`、`请求头Headers`、参数表等信息。

1) **先找文档路径**
   - 例：`docs/api/api-wen-dang2/deng-lu/deng-lu-wei-kong-ping-tai-di-yi-bu.md`
2) **模块名来自目录名**
   - TypeScript：`deng-lu` → `client.api.dengLu`
   - Python：`deng-lu` → `client.api.deng_lu`
3) **方法名默认优先由请求 path 推导**
   - 例：`POST /member/login`
   - TypeScript：通常映射为 `memberLogin(...)`
   - Python：通常映射为 `member_login(...)`
4) **当 path 推导发生冲突/不稳定时**
   - 生成器会回退到 `operationId` 做稳定命名（可在生成物里查证）：
     - TypeScript：`src/typescript-sdk/src/generated/operation-index.ts`
     - Python：`src/python-sdk/wkteam_api_sdk/operation_index.py`

## Python SDK 进一步说明

更完整的 Python SDK 使用、配置项解释与开发命令见：`src/python-sdk/README.md`（包含 sync/async、重试、hook、脱敏等）。

## 开发与验证（仓库内）

```bash
# TypeScript SDK
cd src/typescript-sdk
npm i
npm run generate:api
npm run generate:sdk
npm test
npm run build

# Python SDK
cd ../../
python3.11 src/python-sdk/tools/generate_sdk.py
PYTHONPATH=src/python-sdk python3.11 -m pytest -q src/python-sdk/tests
```
